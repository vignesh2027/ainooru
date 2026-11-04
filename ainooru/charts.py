"""Server-rendered SVG chart of the cycle: what has been used and where it is heading."""

from __future__ import annotations

from datetime import date, timedelta
from html import escape

from .forecast import Forecast, Reading

W, H = 720, 320
L, R, T, B = 52, 16, 18, 40  # margins


def _fmt_day(d: date) -> str:
    return f"{d.day} {d.strftime('%b')}"


def cycle_chart(start: Reading, readings: list[Reading], expected_end: date, late_max: int, f: Forecast) -> str:
    total_days = max(1, (expected_end - start.day).days + late_max)
    top_band = max((b[3] for b in f.band), default=f.used)
    ymax = max(f.threshold * 1.2, top_band * 1.08, f.used * 1.1)
    ymax = int((ymax + 99) // 100 * 100)

    def x(day: float) -> float:
        return L + (W - L - R) * day / total_days

    def y(units: float) -> float:
        return T + (H - T - B) * (1 - units / ymax)

    parts: list[str] = []
    add = parts.append
    # Danger zone and threshold line.
    add(f'<rect class="c-danger-zone" x="{L}" y="{T}" width="{W - L - R}" height="{y(f.threshold) - T:.1f}"/>')
    # Possible reading window.
    nominal = (expected_end - start.day).days
    add(f'<rect class="c-window" x="{x(nominal):.1f}" y="{T}" width="{max(2.0, x(total_days) - x(nominal)):.1f}" height="{H - T - B}"/>')
    add(f'<text class="c-note" x="{x(nominal) - 4:.1f}" y="{T + 12}" text-anchor="end">reading due</text>')
    # Grid and y ticks.
    for u in range(0, ymax + 1, 100):
        add(f'<line class="c-grid" x1="{L}" x2="{W - R}" y1="{y(u):.1f}" y2="{y(u):.1f}"/>')
        add(f'<text class="c-tick" x="{L - 8}" y="{y(u) + 4:.1f}" text-anchor="end">{u}</text>')
    add(f'<line class="c-threshold" x1="{L}" x2="{W - R}" y1="{y(f.threshold):.1f}" y2="{y(f.threshold):.1f}"/>')
    add(f'<text class="c-threshold-label" x="{L + 6}" y="{y(f.threshold) - 6:.1f}">{f.threshold} units: free units drop from 200 to 100</text>')
    # x ticks.
    step = 10 if total_days > 30 else 5
    for d in range(0, total_days + 1, step):
        add(f'<text class="c-tick" x="{x(d):.1f}" y="{H - B + 18}" text-anchor="middle">{_fmt_day(start.day + timedelta(days=d))}</text>')
    # Forecast band and median.
    if f.band:
        first = (f.days_elapsed, f.used, f.used, f.used)
        pts = [first] + f.band
        upper = " ".join(f"{x(d):.1f},{y(hi):.1f}" for d, lo, mid, hi in pts)
        lower = " ".join(f"{x(d):.1f},{y(lo):.1f}" for d, lo, mid, hi in reversed(pts))
        add(f'<polygon class="c-band" points="{upper} {lower}"/>')
        mid = " ".join(f"{x(d):.1f},{y(m):.1f}" for d, lo, m, hi in pts)
        add(f'<polyline class="c-median" points="{mid}"/>')
    # Observed readings.
    obs = [start] + sorted(readings, key=lambda r: r.day)
    path = " ".join(f"{x((r.day - start.day).days):.1f},{y(r.value - start.value):.1f}" for r in obs)
    add(f'<polyline class="c-observed" points="{path}"/>')
    for r in obs:
        add(f'<circle class="c-point" cx="{x((r.day - start.day).days):.1f}" cy="{y(r.value - start.value):.1f}" r="4"/>')
    add(f'<text class="c-tick" x="{L}" y="{T - 6}">units used</text>')

    label = (
        f"Units used this cycle: {f.used} so far. Likely total {f.units_p50} units, "
        f"80 percent range {f.units_p10} to {f.units_p90}. Threshold {f.threshold}."
    )
    return (
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>{''.join(parts)}</svg>"
    )
