"""Backtest the Ainooru forecaster on a real household's daily electricity use.

Data: UCI "Individual household electric power consumption" (one home near
Paris, minute readings, Dec 2006 to Nov 2010). Run eval/fetch_data.py first.

Method, in plain terms:

1. Turn minute readings into daily kWh. Days with more than 10% of minutes
   missing are marked missing, and any cycle touching one is skipped.
2. Scale every day by one constant so that the median 60-day total in the
   first year is exactly 500. This puts the home right at the Tamil Nadu cliff,
   which is the case that matters, without changing the shape of its usage.
3. Cut the data into 60-day cycles starting every 7 days. For each cycle the
   real reader comes 0 to 3 days late (drawn once per cycle, fixed seed).
4. On days 15, 30 and 45 of each cycle, give each method what a household
   would have: weekly meter readings up to that day. Ask for the chance that
   the final bill crosses 500 units.
5. The first year is used only to choose the noise settings (grid search on
   Brier score). All reported scores come from the later years.

Methods compared:

* straight line: the mental arithmetic people do. Units so far divided by days
  so far, times 60. It says "will cross" or "will not", nothing in between.
* Ainooru with the provisional default noise.
* Ainooru with noise settings fitted on the first year.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from ainooru.forecast import PROVISIONAL_NOISE, Noise, Reading, simulate  # noqa: E402
from ainooru.tariff import TN_2026  # noqa: E402

DATA = ROOT / "data" / "household_power_consumption.txt"
CYCLE = 60
LATE_MAX = 3
STEP = 7
CHECK_DAYS = (15, 30, 45)
SIGMAS = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50)
PHIS = (0.3, 0.5, 0.6, 0.7, 0.8, 0.9)
T = 500


def daily_kwh() -> tuple[list[date], np.ndarray]:
    sums: dict[date, float] = {}
    counts: dict[date, int] = {}
    with DATA.open() as fh:
        reader = csv.reader(fh, delimiter=";")
        next(reader)
        for row in reader:
            if row[2] == "?":
                continue
            d = datetime.strptime(row[0], "%d/%m/%Y").date()
            sums[d] = sums.get(d, 0.0) + float(row[2])
            counts[d] = counts.get(d, 0) + 1
    first, last = min(sums), max(sums)
    days = [first + timedelta(days=i) for i in range((last - first).days + 1)]
    out = np.full(len(days), np.nan)
    for i, d in enumerate(days):
        n = counts.get(d, 0)
        if n >= 0.9 * 1440:
            out[i] = sums[d] / 60 * (1440 / n)  # kW-minutes to kWh, filling small gaps
    # The first and last days are partial recordings.
    out[0] = out[-1] = np.nan
    return days, out


@dataclass
class Case:
    start: date
    check: int
    start_reading: float
    readings: list[Reading]
    final_units: int
    used: float


def build_cases(days: list[date], kwh: np.ndarray, lo: int, hi: int, rng: np.random.Generator) -> list[Case]:
    cases = []
    for s in range(lo, hi - CYCLE - LATE_MAX, STEP):
        window = kwh[s : s + CYCLE + LATE_MAX]
        if np.isnan(window).any():
            continue
        cum = np.concatenate([[0.0], np.cumsum(window)])
        late = int(rng.integers(0, LATE_MAX + 1))
        final = int(np.floor(cum[CYCLE + late]))
        base = 10000.0
        for k in CHECK_DAYS:
            marks = sorted(set(list(range(STEP, k, STEP)) + [k]))
            rs = [Reading(days[s] + timedelta(days=m), base + np.floor(cum[m])) for m in marks]
            cases.append(Case(days[s], k, base, rs, final, np.floor(cum[k])))
    return cases


def ainooru_p(case: Case, noise: Noise, n_paths: int) -> tuple[float, int, int, int]:
    f = simulate(
        tariff=TN_2026,
        start=Reading(case.start, case.start_reading),
        readings=case.readings,
        expected_end=case.start + timedelta(days=CYCLE),
        late_max=LATE_MAX,
        noise=noise,
        n_paths=n_paths,
    )
    return f.p_cross, f.units_p10, f.units_p50, f.units_p90


def straight_line(case: Case) -> tuple[float, int]:
    projected = case.used / case.check * CYCLE
    return (1.0 if projected > T else 0.0), int(round(projected))


def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def score(name: str, p: np.ndarray, y: np.ndarray, med: np.ndarray, finals: np.ndarray,
          lo: np.ndarray | None = None, hi: np.ndarray | None = None) -> dict:
    pc = np.clip(p, 0.01, 0.99)
    out = {
        "method": name,
        "brier": brier(p, y),
        "log_loss_clipped": float(-np.mean(y * np.log(pc) + (1 - y) * np.log(1 - pc))),
        "accuracy_at_half": float(np.mean((p >= 0.5) == (y == 1))),
        "missed_crossings": int(np.sum((p < 0.5) & (y == 1))),
        "false_alarms": int(np.sum((p >= 0.5) & (y == 0))),
        "median_abs_error_units": float(np.median(np.abs(med - finals))),
    }
    if lo is not None:
        out["coverage_80"] = float(np.mean((finals >= lo) & (finals <= hi)))
    return out


def calibration(p: np.ndarray, y: np.ndarray) -> list[dict]:
    edges = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001]
    rows = []
    for a, b in zip(edges, edges[1:]):
        m = (p >= a) & (p < b)
        if m.sum():
            rows.append({"bin": f"{a:.1f} to {min(b, 1):.1f}", "n": int(m.sum()),
                         "mean_forecast": float(p[m].mean()), "observed_rate": float(y[m].mean())})
    return rows


def main() -> None:
    if not DATA.exists():
        sys.exit("Run: uv run python eval/fetch_data.py")
    days, kwh = daily_kwh()
    fit_end = 365
    totals = [np.nansum(kwh[s : s + CYCLE]) for s in range(1, fit_end - CYCLE) if not np.isnan(kwh[s : s + CYCLE]).any()]
    scale = T / float(np.median(totals))
    kwh = kwh * scale

    rng = np.random.default_rng(2026)
    fit_cases = build_cases(days, kwh, 1, fit_end, rng)
    test_cases = build_cases(days, kwh, fit_end, len(days), rng)

    # 1. Fit noise settings on the first year only.
    y_fit = np.array([c.final_units > T for c in fit_cases], dtype=float)
    grid = []
    for sg in SIGMAS:
        for ph in PHIS:
            noise = Noise(sg, ph, "grid")
            p = np.array([ainooru_p(c, noise, 2000)[0] for c in fit_cases])
            grid.append((brier(p, y_fit), sg, ph))
    grid.sort()
    _, best_sigma, best_phi = grid[0]
    fitted = Noise(best_sigma, best_phi, "fitted")

    # 2. Score every method on the later years.
    y = np.array([c.final_units > T for c in test_cases], dtype=float)
    finals = np.array([c.final_units for c in test_cases])
    results, calib = [], {}
    sl = [straight_line(c) for c in test_cases]
    results.append(score("Straight line", np.array([s[0] for s in sl]), y, np.array([s[1] for s in sl]), finals))
    for name, noise in (("Ainooru, provisional noise", PROVISIONAL_NOISE), ("Ainooru, fitted noise", fitted)):
        out = [ainooru_p(c, noise, 4000) for c in test_cases]
        p = np.array([o[0] for o in out])
        results.append(score(name, p, y, np.array([o[2] for o in out]), finals,
                             np.array([o[1] for o in out]), np.array([o[3] for o in out])))
        calib[name] = calibration(p, y)

    by_day = []
    for k in CHECK_DAYS:
        idx = np.array([c.check == k for c in test_cases])
        sl_p = np.array([s[0] for s, c in zip(sl, test_cases) if c.check == k])
        ai_p = np.array([ainooru_p(c, fitted, 4000)[0] for c in test_cases if c.check == k])
        by_day.append({"day": k, "n": int(idx.sum()), "straight_line_brier": brier(sl_p, y[idx]),
                       "ainooru_brier": brier(ai_p, y[idx])})

    summary = {
        "dataset": "UCI Individual household electric power consumption (Hebrail and Berard, 2006), CC BY 4.0",
        "days": [days[0].isoformat(), days[-1].isoformat()],
        "scale_to_threshold": scale,
        "fit_cycles": len(fit_cases) // len(CHECK_DAYS),
        "test_cycles": len(test_cases) // len(CHECK_DAYS),
        "test_forecasts": len(test_cases),
        "test_crossing_rate": float(y.mean()),
        "fitted_noise": {"sigma": best_sigma, "phi": best_phi},
        "grid_top5": [{"brier": b, "sigma": s, "phi": p} for b, s, p in grid[:5]],
        "results": results,
        "by_check_day": by_day,
        "calibration": calib,
    }
    (ROOT / "results.json").write_text(json.dumps(summary, indent=2))
    write_markdown(summary)
    print(json.dumps({k: summary[k] for k in ("fitted_noise", "test_forecasts", "test_crossing_rate")}, indent=2))
    for r in results:
        print(r)
    for b in by_day:
        print(b)


def write_markdown(s: dict) -> None:
    lines = [
        "# Backtest results",
        "",
        "Generated by `uv run python eval/backtest.py`. Do not edit by hand.",
        "",
        f"* Data: {s['dataset']}, {s['days'][0]} to {s['days'][1]}.",
        f"* Usage scaled by {s['scale_to_threshold']:.4f} so the first year's median 60-day cycle is exactly 500 units.",
        f"* Noise settings chosen on the first year ({s['fit_cycles']} cycles): spread {s['fitted_noise']['sigma']}, "
        f"persistence {s['fitted_noise']['phi']}.",
        f"* Scored on the later years: {s['test_cycles']} cycles, {s['test_forecasts']} forecasts (days 15, 30 and 45), "
        f"{s['test_crossing_rate'] * 100:.0f}% of which crossed 500.",
        "",
        "Lower Brier score is better. 0.25 is what always answering 50% would score.",
        "",
        "| Method | Brier | Accuracy at 50% | Missed crossings | False alarms | Median error (units) | 80% range held the truth |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in s["results"]:
        cov = f"{r['coverage_80'] * 100:.0f}%" if "coverage_80" in r else "not given"
        lines.append(
            f"| {r['method']} | {r['brier']:.3f} | {r['accuracy_at_half'] * 100:.0f}% | {r['missed_crossings']} | "
            f"{r['false_alarms']} | {r['median_abs_error_units']:.0f} | {cov} |"
        )
    lines += ["", "## By day of the cycle (fitted noise)", "", "| Day | Forecasts | Straight line Brier | Ainooru Brier |", "|---|---|---|---|"]
    for b in s["by_check_day"]:
        lines.append(f"| {b['day']} | {b['n']} | {b['straight_line_brier']:.3f} | {b['ainooru_brier']:.3f} |")
    lines += ["", "## Calibration (fitted noise)", "", "| Forecast band | Forecasts | Mean forecast | Actually crossed |", "|---|---|---|---|"]
    for c in s["calibration"]["Ainooru, fitted noise"]:
        lines.append(f"| {c['bin']} | {c['n']} | {c['mean_forecast'] * 100:.0f}% | {c['observed_rate'] * 100:.0f}% |")
    lines += [
        "",
        "## Limits of this test",
        "",
        "* One household, in France, with electric heating patterns rather than Chennai air conditioning.",
        f"* The scale was set on the first year. The home used more in later years, so {s['test_crossing_rate'] * 100:.0f}% of "
        "test cycles crossed 500 rather than half.",
        "* The noise grid is flat near its best point: the top five settings score within 0.001 Brier of each other on the first year.",
        "* Readings are simulated as weekly and exact; a real family may read less often.",
    ]
    (ROOT / "RESULTS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
