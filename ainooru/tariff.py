"""Tamil Nadu LT-IA domestic energy charges for one bimonthly cycle.

The tariff is telescopic: each slab rate applies only to the units inside
that slab. What makes it unusual is the eligibility switch. Consumption at
or below the threshold (500 units) is billed on a generous table; anything
above it is billed from unit 1 on a harsher table. That switch is the cliff.

Fixed charges depend on connected load and are identical on both sides of
the cliff, so they are left out of every comparison here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import lru_cache

import numpy as np

D = Decimal


@dataclass(frozen=True)
class Slab:
    upto: int | None  # inclusive upper unit of this slab; None means no limit
    rate: Decimal  # rupees per unit


@dataclass(frozen=True)
class Tariff:
    key: str
    name: str
    effective_from: date
    threshold: int
    at_or_below: tuple[Slab, ...]
    above: tuple[Slab, ...]
    source: str

    def table_for(self, units: int) -> tuple[Slab, ...]:
        return self.at_or_below if units <= self.threshold else self.above

    def energy_charge(self, units: int) -> Decimal:
        """Exact energy charge in rupees for a whole number of units."""
        if units < 0:
            raise ValueError("units cannot be negative")
        total = D(0)
        lower = 0
        for slab in self.table_for(units):
            top = units if slab.upto is None else min(units, slab.upto)
            if top > lower:
                total += (top - lower) * slab.rate
            if slab.upto is None or units <= slab.upto:
                break
            lower = slab.upto
        return total.quantize(D("0.01"))

    def breakdown(self, units: int) -> list[tuple[int, int, Decimal, Decimal]]:
        """Rows of (from_unit, to_unit, rate, amount) for display."""
        rows = []
        lower = 0
        for slab in self.table_for(units):
            top = units if slab.upto is None else min(units, slab.upto)
            if top > lower:
                rows.append((lower + 1, top, slab.rate, ((top - lower) * slab.rate).quantize(D("0.01"))))
            if slab.upto is None or units <= slab.upto:
                break
            lower = slab.upto
        return rows

    def cliff(self) -> Decimal:
        """Extra rupees charged for the single unit that crosses the threshold."""
        return self.energy_charge(self.threshold + 1) - self.energy_charge(self.threshold)

    def marginal_rate(self, units: int) -> Decimal:
        """Rupees for one more unit at this consumption, cliff included."""
        return self.energy_charge(units + 1) - self.energy_charge(units)

    def charge_lookup(self, max_units: int = 4000) -> np.ndarray:
        return _lookup(self.key, max_units)


# Rates above 500 units are shared by both regimes.
_ABOVE_500 = (
    Slab(100, D("0")),
    Slab(400, D("4.70")),
    Slab(500, D("6.30")),
    Slab(600, D("8.40")),
    Slab(800, D("9.45")),
    Slab(1000, D("10.50")),
    Slab(None, D("11.55")),
)

TN_2026 = Tariff(
    key="tn-lt1a-2026-05",
    name="Tamil Nadu domestic (LT-IA), from 10 May 2026",
    effective_from=date(2026, 5, 10),
    threshold=500,
    at_or_below=(Slab(200, D("0")), Slab(400, D("4.70")), Slab(500, D("6.30"))),
    above=_ABOVE_500,
    source=(
        "TNERC Order No. 5 of 2026 (26 May 2026), under G.O. (Ms) No. 50 dated 10 May 2026: 200 free units "
        "bimonthly for domestic consumers up to 500 units. Other slab rates: consumer-payable energy charges "
        "in TNERC Order No. 4 of 2026 (27 April 2026)."
    ),
)

TN_2025 = Tariff(
    key="tn-lt1a-2025-07",
    name="Tamil Nadu domestic (LT-IA), 1 July 2025 to 9 May 2026",
    effective_from=date(2025, 7, 1),
    threshold=500,
    at_or_below=(Slab(100, D("0")), Slab(200, D("2.35")), Slab(400, D("4.70")), Slab(500, D("6.30"))),
    above=_ABOVE_500,
    source="Consumer-payable LT-IA energy charges from 1 July 2025, TNERC Order No. 4 of 2026 (27 April 2026).",
)

TARIFFS = {t.key: t for t in (TN_2026, TN_2025)}
CURRENT = TN_2026


def tariff_on(day: date) -> Tariff:
    """The tariff in force on a given date."""
    for t in sorted(TARIFFS.values(), key=lambda t: t.effective_from, reverse=True):
        if day >= t.effective_from:
            return t
    return TN_2025


@lru_cache(maxsize=8)
def _lookup(key: str, max_units: int) -> np.ndarray:
    t = TARIFFS[key]
    return np.array([float(t.energy_charge(u)) for u in range(max_units + 1)])


def charges(tariff: Tariff, units: np.ndarray) -> np.ndarray:
    """Vectorised energy charge for an array of whole units."""
    units = np.asarray(units, dtype=np.int64)
    table = tariff.charge_lookup()
    top = len(table) - 1
    out = table[np.clip(units, 0, top)]
    over = units > top
    if over.any():
        out = out.copy()
        out[over] = table[top] + (units[over] - top) * float(tariff.above[-1].rate)
    return out
