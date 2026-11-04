"""Ainooru web app: enter meter readings, see where the cycle is heading."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import store
from .charts import cycle_chart
from .forecast import Reading, default_end, simulate
from .tariff import CURRENT, TN_2024

HERE = Path(__file__).resolve().parent
app = FastAPI(title="Ainooru")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")

# Typical draw of a 1.5 ton inverter split AC in a Chennai bedroom. Shown with a
# "check your label" note; it only converts units into something people can act on.
AC_KWH_PER_HOUR = 1.2


def rupees(v: float, decimals: int = 0) -> str:
    return f"₹{v:,.{decimals}f}"


templates.env.filters["rupees"] = rupees


def today() -> date:
    return date.today()


def back(error: str | None = None) -> RedirectResponse:
    url = "/" if not error else f"/?error={quote(error)}"
    return RedirectResponse(url, status_code=303)


def advice(f) -> str:
    if f.status == "over":
        return (
            f"This cycle has already passed {f.threshold} units, so it is billed on the higher table. "
            "From here each unit costs the normal slab rate of ₹8.40 to ₹11.55."
        )
    if f.status == "lost":
        return (
            f"Even halving use from today would very likely end above {f.threshold}. The cliff is lost for this cycle, "
            f"so cutting back now saves only about {rupees(f.unit_value, 2)} a unit. Do not give up comfort for it."
        )
    if f.status == "safe":
        return f"On track to stay at or under {f.threshold} units. Keep going as you are."
    cut = f.cut_per_day or 0
    hours = cut / AC_KWH_PER_HOUR
    return (
        f"Keep to {f.safe_rate:.1f} units a day (now {f.rate:.1f}). That is {cut:.1f} units a day less, "
        f"about {hours:.1f} hours less of a 1.5 ton AC."
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request, error: str | None = None):
    cycle = store.get_cycle()
    ctx = {"error": error, "today": today(), "tariff": CURRENT, "old_tariff": TN_2024}
    if cycle is None:
        return templates.TemplateResponse(request, "setup.html", ctx)
    stored = store.readings()
    start = Reading(cycle.start_day, cycle.start_reading)
    rs = [Reading(r.day, r.value) for r in stored]
    try:
        f = simulate(tariff=CURRENT, start=start, readings=rs, expected_end=cycle.expected_end, late_max=cycle.late_max)
    except ValueError as e:
        ctx.update(cycle=cycle, readings=stored, forecast=None, error=str(e))
        return templates.TemplateResponse(request, "dashboard.html", ctx)
    ctx.update(
        cycle=cycle,
        readings=stored,
        forecast=f,
        advice=advice(f),
        chart=cycle_chart(start, rs, cycle.expected_end, cycle.late_max, f),
        ac_rate=AC_KWH_PER_HOUR,
        hours_cut=(f.cut_per_day or 0) / AC_KWH_PER_HOUR,
    )
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@app.post("/cycle")
def set_cycle(
    start_day: date = Form(...),
    start_reading: float = Form(...),
    expected_end: date | None = Form(None),
    late_max: int = Form(3),
):
    if start_day > today():
        return back("The last bill's reading date cannot be in the future.")
    if start_reading < 0:
        return back("A meter reading cannot be negative.")
    end = expected_end or default_end(start_day)
    if end <= start_day:
        return back("The next reading date must be after the last one.")
    store.set_cycle(store.Cycle(start_day, start_reading, end, max(0, min(late_max, 15)), sample=False))
    return back()


@app.post("/readings")
def add_reading(day: date = Form(...), value: float = Form(...)):
    cycle = store.get_cycle()
    if cycle is None:
        return back("Set up the cycle first.")
    if day < cycle.start_day or day > today():
        return back("The reading date must be between the last bill and today.")
    earlier = [r for r in store.readings() if r.day <= day] or []
    floor = max([cycle.start_reading] + [r.value for r in earlier])
    if value < floor:
        return back(f"{value:g} is lower than an earlier reading of {floor:g}. Check the number on the meter.")
    store.add_reading(day, value)
    return back()


@app.post("/readings/{reading_id}/delete")
def delete_reading(reading_id: int):
    store.delete_reading(reading_id)
    return back()


@app.post("/sample")
def load_sample():
    """Load made-up readings so the screen can be tried without a meter."""
    start = today() - timedelta(days=34)
    store.set_cycle(store.Cycle(start, 18240, start + timedelta(days=60), 3, sample=True))
    for days, used in ((9, 71), (20, 167), (34, 289)):
        store.add_reading(start + timedelta(days=days), 18240 + used)
    return back()


@app.post("/reset")
def reset():
    store.reset()
    return back()


@app.get("/healthz")
def healthz():
    return {"ok": True}
