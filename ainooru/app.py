"""Ainooru web app: enter meter readings, see where the cycle is heading."""

from __future__ import annotations

import re
import secrets
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import meter_photo, store
from .charts import cycle_chart
from .forecast import Reading, default_end, simulate
from .i18n import LANGS, S, fmt_day, translator
from .tariff import CURRENT, TN_2025

HERE = Path(__file__).resolve().parent
app = FastAPI(title="Ainooru")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")

# Typical draw in units (kWh) per hour. Only used to turn a daily cut into
# something a family can act on; the page tells them to check their own label.
APPLIANCES = (("ac15", 1.2), ("ac1", 0.9), ("geyser", 2.0), ("motor", 0.75), ("iron", 1.0), ("fan", 0.075))


def rupees(v: float, decimals: int = 0) -> str:
    return f"₹{v:,.{decimals}f}"


templates.env.filters["rupees"] = rupees
templates.env.globals["hosted"] = store.HOSTED
COOKIE = "ainooru_id"


@app.middleware("http")
async def household(request: Request, call_next):
    """Hosted demo: tie each browser to its own in-memory household with a random cookie id."""
    if not store.HOSTED:
        return await call_next(request)
    owner = request.cookies.get(COOKIE, "")
    fresh = not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", owner)
    if fresh:
        owner = secrets.token_urlsafe(18)
    token = store.OWNER.set(owner)
    try:
        response = await call_next(request)
    finally:
        store.OWNER.reset(token)
    if fresh:
        response.set_cookie(COOKIE, owner, httponly=True, samesite="lax", secure=True, max_age=7 * 24 * 3600)
    return response
# Cache-busting stamp so browsers pick up a changed stylesheet.
templates.env.globals["css_v"] = int((HERE / "static" / "style.css").stat().st_mtime)


def today() -> date:
    return date.today()


def lang_of(request: Request) -> str:
    lang = request.cookies.get("lang", "en")
    return lang if lang in LANGS else "en"


def back(error: str | None = None, **params) -> RedirectResponse:
    if not error:
        return RedirectResponse("/", status_code=303)
    return RedirectResponse("/?" + urlencode({"error": error, **params}), status_code=303)


def advice(f, t) -> str:
    if f.status == "over":
        return t("advice_over", T=f.threshold)
    if f.status == "lost":
        return t("advice_lost", T=f.threshold, v=rupees(f.unit_value, 2))
    if f.status == "safe":
        return t("advice_safe", T=f.threshold)
    return t("advice_cut", safe=f"{f.safe_rate:.1f}", rate=f"{f.rate:.1f}", cut=f"{f.cut_per_day:.1f}")


def appliance_chips(cut: float, t) -> list[str]:
    chips = []
    for key, kwh in APPLIANCES:
        hours = cut / kwh
        if hours <= 24:
            chips.append(t("chip", h=f"{hours:.1f}", name=t(key)))
    return chips


def error_text(request: Request, t) -> str | None:
    key = request.query_params.get("error")
    if not key or key not in S or not key.startswith("err_"):
        return None
    params = {k: v for k, v in request.query_params.items() if k != "error"}
    try:
        return t(key, **params)
    except KeyError:
        return None


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    lang = lang_of(request)
    t = translator(lang)
    cycle = store.get_cycle()
    prefill = request.query_params.get("prefill", "")
    ctx = {"error": error_text(request, t), "today": today(), "tariff": CURRENT, "old_tariff": TN_2025,
           "t": t, "lang": lang, "day": lambda d, year=False: fmt_day(d, lang, year),
           "photo": meter_photo.available(), "prefill": prefill if prefill.isdigit() else ""}
    if cycle is None:
        return templates.TemplateResponse(request, "setup.html", ctx)
    stored = store.readings()
    start = Reading(cycle.start_day, cycle.start_reading)
    rs = [Reading(r.day, r.value) for r in stored]
    ctx.update(cycle=cycle, readings=stored, forecast=None)
    try:
        f = simulate(tariff=CURRENT, start=start, readings=rs, expected_end=cycle.expected_end, late_max=cycle.late_max)
    except ValueError:
        ctx["error"] = t("err_order")
        return templates.TemplateResponse(request, "dashboard.html", ctx)
    cut = f.cut_per_day or 0
    ctx.update(
        forecast=f,
        advice=advice(f, t),
        chart_wide=cycle_chart(start, rs, cycle.expected_end, cycle.late_max, f, lang),
        chart_compact=cycle_chart(start, rs, cycle.expected_end, cycle.late_max, f, lang, compact=True),
        chips=appliance_chips(cut, t),
        cut=cut,
        appliance_list=", ".join(f"{t(k)} {v:g}" for k, v in APPLIANCES),
    )
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@app.get("/lang/{code}")
def set_lang(code: str):
    r = RedirectResponse("/", status_code=303)
    if code in LANGS:
        r.set_cookie("lang", code, max_age=365 * 24 * 3600, samesite="lax")
    return r


@app.post("/cycle")
def set_cycle(
    start_day: date = Form(...),
    start_reading: float = Form(...),
    expected_end: date | None = Form(None),
    late_max: int = Form(3),
):
    if start_day > today():
        return back("err_future")
    if start_reading < 0:
        return back("err_negative")
    end = expected_end or default_end(start_day)
    if end <= start_day:
        return back("err_end")
    store.set_cycle(store.Cycle(start_day, start_reading, end, max(0, min(late_max, 15)), sample=False))
    return back()


@app.post("/readings")
def add_reading(day: date = Form(...), value: float = Form(...)):
    cycle = store.get_cycle()
    if cycle is None:
        return back("err_setup")
    if day < cycle.start_day or day > today():
        return back("err_range")
    earlier = [r.value for r in store.readings() if r.day <= day]
    floor = max([cycle.start_reading] + earlier)
    if value < floor:
        return back("err_lower", v=f"{value:g}", floor=f"{floor:g}")
    store.add_reading(day, value)
    return back()


MAX_PHOTO_BYTES = 15 * 1024 * 1024


@app.post("/photo")
async def read_photo(photo: UploadFile = File(...)):
    data = await photo.read(MAX_PHOTO_BYTES + 1)
    if not data or len(data) > MAX_PHOTO_BYTES:
        return back("err_photo")
    value = meter_photo.read_meter(data)
    if value is None:
        return back("err_photo")
    return RedirectResponse(f"/?prefill={value}#add-h", status_code=303)


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
