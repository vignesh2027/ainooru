"""Probabilistic forecast of a bimonthly cycle's total units and bill.

The household gives us the reading on its last bill and a few meter readings
since. We estimate the recent daily rate, then simulate the rest of the cycle
many times. Each path draws:

* a level factor for how wrong our rate estimate may be (shrinks as more days
  are observed),
* day-to-day usage with persistence, since hot spells and guests last days,
* how many days late the meter reader turns up.

Every path ends in a whole number of units and a bill. From these paths we
read off the chance of crossing the threshold, the bill range, the value of a
unit saved today, and the largest daily rate that keeps the risk acceptable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from math import sqrt

import numpy as np

from .tariff import Tariff, charges


@dataclass(frozen=True)
class Noise:
    sigma: float  # standard deviation of daily log usage around the mean
    phi: float  # day-to-day persistence (AR(1) coefficient) of that deviation
    source: str


# Chosen by grid search on the first year of a public household dataset and
# scored on the following three years. See eval/RESULTS.md.
DEFAULT_NOISE = Noise(sigma=0.20, phi=0.90, source="fitted on one year of a public household dataset (eval/RESULTS.md)")
PROVISIONAL_NOISE = Noise(sigma=0.30, phi=0.60, source="provisional default")


@dataclass(frozen=True)
class Reading:
    day: date
    value: float


@dataclass
class Forecast:
    status: str  # over, lost, danger, watch, safe
    used: int
    days_elapsed: int
    days_left_nominal: int
    rate: float
    p_cross: float
    bill_p10: float
    bill_p50: float
    bill_p90: float
    bill_mean: float
    units_p10: int
    units_p50: int
    units_p90: int
    unit_value: float  # expected rupees saved by using one unit fewer
    safe_rate: float | None  # daily units that keep p_cross at or under target
    p_cross_at_safe: float | None  # check: crossing chance if the safe rate is followed
    saving_if_safe: float | None  # expected rupees saved by following the safe rate
    units_cut_if_safe: float | None  # expected units given up to get that saving
    target: float
    threshold: int
    cliff: float
    noise: Noise
    band: list[tuple[int, float, float, float]] = field(default_factory=list)  # (day, p10, p50, p90) cumulative

    @property
    def cut_per_day(self) -> float | None:
        if self.safe_rate is None:
            return None
        return max(0.0, self.rate - self.safe_rate)


def estimate_rate(start: Reading, readings: list[Reading], half_life_days: float = 14.0) -> tuple[float, int]:
    """Recency-weighted daily rate and number of observed days."""
    points = [start] + sorted(readings, key=lambda r: r.day)
    last = points[-1].day
    num = den = 0.0
    for a, b in zip(points, points[1:]):
        days = (b.day - a.day).days
        if days <= 0:
            continue
        mid_age = (last - a.day).days - days / 2
        w = days * 0.5 ** (mid_age / half_life_days)
        num += w * (b.value - a.value) / days
        den += w
    observed = (last - start.day).days
    return (num / den if den else 0.0), observed


def validate(start: Reading, readings: list[Reading]) -> None:
    prev = start
    for r in sorted(readings, key=lambda r: r.day):
        if r.day < start.day:
            raise ValueError(f"Reading on {r.day} is before the cycle started on {start.day}.")
        if r.value < prev.value:
            raise ValueError(f"Reading {r.value:g} on {r.day} is lower than the earlier {prev.value:g}. Meters only go up.")
        prev = r


def simulate(
    *,
    tariff: Tariff,
    start: Reading,
    readings: list[Reading],
    expected_end: date,
    late_max: int = 3,
    noise: Noise = DEFAULT_NOISE,
    target: float = 0.10,
    n_paths: int = 4000,
    seed: int = 7,
) -> Forecast:
    validate(start, readings)
    last = max(readings, key=lambda r: r.day) if readings else start
    used = last.value - start.value
    rate, observed = estimate_rate(start, readings)
    days_elapsed = (last.day - start.day).days
    days_left = max(0, (expected_end - last.day).days)
    horizon = days_left + late_max

    rng = np.random.default_rng(seed)
    sigma, phi = noise.sigma, noise.phi
    # Uncertainty of a mean of an AR(1) process observed over `observed` days.
    long_run = sigma * sqrt((1 + phi) / (1 - phi))
    s_level = long_run / sqrt(max(observed, 1))
    level = np.exp(rng.normal(0, s_level, n_paths) - s_level**2 / 2)

    if horizon > 0:
        eps = rng.normal(0, 1, (n_paths, horizon))
        x = np.empty_like(eps)
        x[:, 0] = sigma * eps[:, 0]
        k = sqrt(1 - phi**2) * sigma
        for t in range(1, horizon):
            x[:, t] = phi * x[:, t - 1] + k * eps[:, t]
        daily = rate * level[:, None] * np.exp(x - sigma**2 / 2)
        cum = np.cumsum(daily, axis=1)
    else:
        cum = np.zeros((n_paths, 0))

    late = rng.integers(0, late_max + 1, n_paths)
    end_idx = days_left + late  # number of future days in each path
    if horizon:
        picked = cum[np.arange(n_paths), np.maximum(end_idx - 1, 0)]
        future = np.where(end_idx > 0, picked, 0.0)
    else:
        future = np.zeros(n_paths)

    units = np.rint(used + future).astype(np.int64)
    bills = charges(tariff, units)
    fewer = charges(tariff, np.maximum(units - 1, 0))
    T = tariff.threshold
    p_cross = float(np.mean(units > T))

    # Largest multiplier m on the future usage so that P(used + m*future > T) <= target.
    headroom = T + 0.5 - used
    if headroom <= 0:
        safe_rate = None
    else:
        q = float(np.quantile(future, 1 - target)) if horizon else 0.0
        safe_rate = rate * headroom / q if q > 0 else None
    p_cross_at_safe = saving_if_safe = units_cut_if_safe = None
    if safe_rate is not None and rate > 0:
        m = min(1.0, safe_rate / rate)
        units_safe = np.rint(used + m * future).astype(np.int64)
        p_cross_at_safe = float(np.mean(units_safe > T))
        saving_if_safe = float(bills.mean() - charges(tariff, units_safe).mean())
        units_cut_if_safe = float(units.mean() - units_safe.mean())
    halved = np.rint(used + 0.5 * future)
    p_cross_halved = float(np.mean(halved > T))

    if used > T:
        status = "over"
    elif p_cross_halved >= 0.9:
        status = "lost"
    elif p_cross >= 0.5:
        status = "danger"
    elif p_cross > target:
        status = "watch"
    else:
        status = "safe"

    band = []
    if horizon:
        qs = np.quantile(cum, [0.1, 0.5, 0.9], axis=0)
        for t in range(horizon):
            band.append((days_elapsed + t + 1, used + qs[0, t], used + qs[1, t], used + qs[2, t]))

    pct = lambda a, p: float(np.quantile(a, p))  # noqa: E731
    return Forecast(
        status=status,
        used=int(round(used)),
        days_elapsed=days_elapsed,
        days_left_nominal=days_left,
        rate=rate,
        p_cross=p_cross,
        bill_p10=pct(bills, 0.1),
        bill_p50=pct(bills, 0.5),
        bill_p90=pct(bills, 0.9),
        bill_mean=float(bills.mean()),
        units_p10=int(pct(units, 0.1)),
        units_p50=int(pct(units, 0.5)),
        units_p90=int(pct(units, 0.9)),
        unit_value=float((bills - fewer).mean()),
        safe_rate=safe_rate,
        p_cross_at_safe=p_cross_at_safe,
        saving_if_safe=saving_if_safe,
        units_cut_if_safe=units_cut_if_safe,
        target=target,
        threshold=T,
        cliff=float(tariff.cliff()),
        noise=noise,
        band=band,
    )


def default_end(cycle_start: date) -> date:
    return cycle_start + timedelta(days=60)
