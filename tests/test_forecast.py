from datetime import date, timedelta

import pytest

from ainooru.forecast import Noise, Reading, estimate_rate, simulate
from ainooru.tariff import TN_2026

START = date(2026, 10, 1)
END = START + timedelta(days=60)


def run(rate, days=30, late_max=3, **kw):
    start = Reading(START, 10000)
    r = Reading(START + timedelta(days=days), 10000 + rate * days)
    return simulate(tariff=TN_2026, start=start, readings=[r], expected_end=END, late_max=late_max, **kw)


def test_rate_from_single_interval():
    rate, observed = estimate_rate(Reading(START, 100), [Reading(START + timedelta(days=10), 180)])
    assert rate == pytest.approx(8.0)
    assert observed == 10


def test_recent_intervals_weigh_more():
    readings = [Reading(START + timedelta(days=20), 100 + 20 * 5), Reading(START + timedelta(days=30), 200 + 10 * 12)]
    rate, _ = estimate_rate(Reading(START, 100), readings)
    assert 8.5 < rate < 12


def test_low_usage_is_safe():
    f = run(rate=5)  # about 300 units a cycle
    assert f.status == "safe"
    assert f.p_cross < 0.01
    assert f.unit_value == pytest.approx(4.70, abs=0.5)


def test_high_usage_is_lost():
    f = run(rate=14)  # about 840 units a cycle
    assert f.status == "lost"
    assert f.p_cross > 0.99
    assert f.unit_value > 8


def test_near_cliff_unit_is_worth_far_more_than_slab_rate():
    f = run(rate=8.3)  # about 500 units a cycle
    assert 0.2 < f.p_cross < 0.9
    assert f.unit_value > 8.40  # above every slab rate it could land in
    assert f.safe_rate is not None and f.safe_rate < f.rate
    # Following the budget saves far more per unit given up than any slab rate.
    assert f.saving_if_safe / f.units_cut_if_safe > 8.40


def test_unit_value_spikes_near_reading_day():
    rate = 500 / 60
    early = run(rate=rate, days=15, late_max=0)
    late = run(rate=rate, days=58, late_max=0)
    assert late.unit_value > 3 * early.unit_value
    assert late.unit_value > 30


def test_safe_rate_actually_achieves_target():
    f = run(rate=8.3)
    assert f.p_cross > f.target
    assert f.p_cross_at_safe <= f.target + 0.005
    assert f.p_cross_at_safe >= f.target - 0.03  # and it is not needlessly strict


def test_already_over():
    f = run(rate=20, days=30)
    assert f.status == "over"
    assert f.safe_rate is None


def test_more_lateness_raises_risk():
    a = run(rate=7.9, late_max=0)
    b = run(rate=7.9, late_max=10)
    assert b.p_cross > a.p_cross


def test_deterministic_with_seed():
    assert run(rate=8.3).p_cross == run(rate=8.3).p_cross


def test_meter_going_backwards_rejected():
    with pytest.raises(ValueError):
        simulate(tariff=TN_2026, start=Reading(START, 500), readings=[Reading(START + timedelta(days=3), 400)],
                 expected_end=END)


def test_band_is_ordered_and_starts_after_last_reading():
    f = run(rate=8.3)
    assert f.band[0][0] == 31
    for _, lo, mid, hi in f.band:
        assert lo <= mid <= hi
