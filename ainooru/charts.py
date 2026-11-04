"""Server-rendered SVG chart of the cycle: what has been used and where it is heading.

Two sizes are rendered: a wide one for desktops and a compact one for phones,
so text stays readable without shrinking a desktop chart onto a small screen.
"""

from __future__ import annotations

from datetime import date, timedelta
from html import escape

from .forecast import Forecast, Reading
from .i18n import fmt_day, translator


def cycle_chart(
    start: Reading,
    readings: list[Reading],
    expected_end: date,
    late_max: int,
    f: Forecast,
    lang: str = "en",
    compact: bool = False,
) -> str:
    t = translator(lang)
    W, H = (380, 300) if compact else (720, 320)
    L, R, T, B = (40, 10, 18, 34) if compact else (52, 16, 18, 40)
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
    add(f'<rect class="c-danger-zone" x="{L}" y="{T}" width="{W - L - R}" height="{y(f.threshold) - T:.1f}"/>')
    nominal = (expected_end - start.day).days
    add(f'<rect class="c-window" x="{x(nominal):.1f}" y="{T}" width="{max(2.0, x(total_days) - x(nominal)):.1f}" height="{H - T - B}"/>')
    add(f'<text class="c-note" x="{x(nominal) - 4:.1f}" y="{T + 12}" text-anchor="end">{escape(t("chart_due"))}</text>')
    ystep = 200 if compact and ymax > 600 else 100
    for u in range(0, ymax + 1, ystep):
        add(f'<line class="c-grid" x1="{L}" x2="{W - R}" y1="{y(u):.1f}" y2="{y(u):.1f}"/>')
        add(f'<text class="c-tick" x="{L - 6}" y="{y(u) + 4:.1f}" text-anchor="end">{u}</text>')
    add(f'<line class="c-threshold" x1="{L}" x2="{W - R}" y1="{y(f.threshold):.1f}" y2="{y(f.threshold):.1f}"/>')
    line_label = t("chart_line_short" if compact else "chart_line", T=f.threshold)
    add(f'<text class="c-threshold-label" x="{L + 6}" y="{y(f.threshold) - 6:.1f}">{escape(line_label)}</text>')
    step = 20 if compact else 10
    for d in range(0, total_days + 1, step):
        add(f'<text class="c-tick" x="{x(d):.1f}" y="{H - B + 18}" text-anchor="middle">'
            f'{escape(fmt_day(start.day + timedelta(days=d), lang))}</text>')
    if f.band:
        pts = [(f.days_elapsed, f.used, f.used, f.used)] + f.band
        upper = " ".join(f"{x(d):.1f},{y(hi):.1f}" for d, lo, mid, hi in pts)
        lower = " ".join(f"{x(d):.1f},{y(lo):.1f}" for d, lo, mid, hi in reversed(pts))
        add(f'<polygon class="c-band" points="{upper} {lower}"/>')
        add(f'<polyline class="c-median" points="{" ".join(f"{x(d):.1f},{y(m):.1f}" for d, lo, m, hi in pts)}"/>')
    obs = [start] + sorted(readings, key=lambda r: r.day)
    add(f'<polyline class="c-observed" points="{" ".join(f"{x((r.day - start.day).days):.1f},{y(r.value - start.value):.1f}" for r in obs)}"/>')
    for r in obs:
        add(f'<circle class="c-point" cx="{x((r.day - start.day).days):.1f}" cy="{y(r.value - start.value):.1f}" r="4"/>')
    add(f'<text class="c-tick" x="{L}" y="{T - 6}">{escape(t("chart_units"))}</text>')

    label = t("chart_aria", used=f.used, p50=f.units_p50, p10=f.units_p10, p90=f.units_p90, T=f.threshold)
    cls = "chart chart-compact" if compact else "chart chart-wide"
    return (
        f'<svg class="{cls}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>{''.join(parts)}</svg>"
    )
