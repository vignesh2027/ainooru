from datetime import date
from decimal import Decimal as D

import numpy as np
import pytest

from ainooru.tariff import TN_2024, TN_2026, charges, tariff_on


def test_published_worked_examples_2026():
    # Worked examples printed alongside the May 2026 scheme.
    assert TN_2026.energy_charge(500) == D("1570.00")
    assert TN_2026.energy_charge(600) == D("2880.00")


def test_first_200_units_free_at_or_below_500():
    assert TN_2026.energy_charge(0) == D("0.00")
    assert TN_2026.energy_charge(200) == D("0.00")
    assert TN_2026.energy_charge(201) == D("4.70")


def test_cliff_values():
    assert TN_2026.energy_charge(501) == D("2048.40")
    assert TN_2026.cliff() == D("478.40")
    assert TN_2024.cliff() == D("243.40")


def test_may_2026_change_saves_235_below_cliff():
    # Press coverage: households below the cut-off save Rs 235 per cycle.
    for units in (200, 350, 500):
        assert TN_2024.energy_charge(units) - TN_2026.energy_charge(units) == D("235.00")
    # Above the cut-off nothing changed.
    for units in (501, 750, 1200):
        assert TN_2024.energy_charge(units) == TN_2026.energy_charge(units)


@pytest.mark.parametrize("t", [TN_2024, TN_2026])
def test_monotone_within_each_regime(t):
    below = [t.energy_charge(u) for u in range(0, 501)]
    above = [t.energy_charge(u) for u in range(501, 1500)]
    assert below == sorted(below)
    assert above == sorted(above)


def test_marginal_rate_far_from_cliff_is_slab_rate():
    assert TN_2026.marginal_rate(300) == D("4.70")
    assert TN_2026.marginal_rate(450) == D("6.30")
    assert TN_2026.marginal_rate(500) == D("478.40")
    assert TN_2026.marginal_rate(700) == D("9.45")
    assert TN_2026.marginal_rate(2000) == D("11.55")


def test_breakdown_sums_to_charge():
    for u in (0, 150, 433, 500, 501, 999, 1234):
        assert sum(r[3] for r in TN_2026.breakdown(u)) == TN_2026.energy_charge(u)


def test_vectorised_matches_exact():
    units = np.array([0, 199, 500, 501, 777, 3999, 4000, 5000])
    exact = [float(TN_2026.energy_charge(int(u))) for u in units]
    assert np.allclose(charges(TN_2026, units), exact)


def test_tariff_on_dates():
    assert tariff_on(date(2026, 5, 9)) is TN_2024
    assert tariff_on(date(2026, 5, 10)) is TN_2026
    assert tariff_on(date(2026, 11, 4)) is TN_2026


def test_negative_units_rejected():
    with pytest.raises(ValueError):
        TN_2026.energy_charge(-1)
