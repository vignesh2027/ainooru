<p align="center"><img src="assets/logo.svg" width="96" alt="Ainooru logo"></p>

# Ainooru

**Stay under 500 units.** Ainooru (ஐநூறு, Tamil for "five hundred") forecasts a Tamil Nadu household's two-month electricity cycle from a few meter readings. It tells the family, before the meter reader comes, whether they will cross the 500-unit line and what crossing it would cost.

**Live demo:** https://applemacbook6sep2004--ainooru.us-east.modal.run

The demo runs on one small Modal container that sleeps when idle, so the first visit can take a few seconds. Each browser gets its own household, kept in server memory only and wiped when the demo restarts; nothing is written to disk. The meter-photo option is switched on: a photo is shrunk, sent to the open vision model on Groq, and not kept.

## The problem

Since 10 May 2026, a Tamil Nadu home that uses 500 units or fewer in a two-month cycle gets 200 units free. At 501 units only 100 are free, and the whole bill moves to a costlier table.

| Units in the cycle | Energy charge |
|---|---|
| 500 | ₹1,570.00 |
| 501 | ₹2,048.40 |

That one unit costs ₹478.40. Before May 2026 it cost ₹243.40, so the cliff has almost doubled. Families only find out where they stand when the bill arrives.

## What Ainooru shows

* The chance of crossing 500 units by the reading date, allowing for a reader who comes a few days late.
* The likely bill, as a median with an 8 in 10 range.
* What a unit saved today is really worth once the cliff is counted. For a home on course for exactly 500 units it is about ₹10 at mid-cycle, and it passes ₹40 two days before a reading whose date is known. The printed rate near the line is ₹4.70 to ₹6.30.
* A daily unit budget that brings the risk down to 10%, with the expected saving and the cut in hours of AC.
* When the cliff is already lost, so the family stops sacrificing comfort for nothing.

![Dashboard with sample readings](docs/screenshots/dashboard.png)

The same screen in Tamil: [docs/screenshots/dashboard-tamil.png](docs/screenshots/dashboard-tamil.png). Phone views and the photo step are in `docs/screenshots/`.

## Run it

You need [uv](https://docs.astral.sh/uv/). It installs the right Python for you.

```sh
git clone <this repository> ainooru
cd ainooru
uv sync
uv run uvicorn ainooru.app:app --port 8000
```

Open http://localhost:8000. Click **Try it with sample readings** to see a household near the line, or enter the reading date and value from your last bill and add today's meter reading.

Readings are stored in `data/ainooru.sqlite3` on your own machine. Set `AINOORU_DB` to use another file.

The interface is in English and Tamil; use the switch at the top right.

### Optional: read the meter from a photo

Typing the reading always works. To also allow a photo of the meter, put a free Groq API key in a `.env` file:

```sh
cp .env.example .env
# then edit .env and set GROQ_API_KEY
```

Restart the server and an "Or take a photo of the meter" option appears under the reading box. The photo is shrunk and sent to an open vision model (`qwen/qwen3.8-27b` on Groq) that returns only the kWh number. Ainooru puts the number in the box for you to check against the meter; nothing is saved until you press Add, and the photo is not stored. Without a key the option is simply hidden.

## Tests

```sh
uv run pytest
```

The tests cover:

* the tariff, including the published worked examples (500 units cost ₹1,570; 600 units cost ₹2,880) and the exact cliff values;
* the forecaster: risk ordering, lateness, and a check that the daily budget really hits its 10% target;
* the web flow, including the rejection of impossible readings.

## Does the forecast hold up?

I backtested the forecaster on a real home's daily use: the public UCI household power dataset, one home near Paris, December 2006 to November 2010. The home's usage was scaled so that its typical two-month cycle sits right at 500 units. I chose the noise settings on the first year only, then scored 282 forecasts (days 15, 30 and 45 of 94 cycles) on the next three years against the straight-line sum people do in their heads.

| Method | Brier score (lower is better) | Right side of 500 at the 50% mark | Typical miss in units | 80% range held the true total |
|---|---|---|---|---|
| Straight line | 0.103 | 90% | 38 | no range given |
| Ainooru | **0.070** | 90% | **32** | **84%** |

Ainooru is no better at the simple yes-or-no call. What it adds is honest probabilities and ranges: a 32% lower Brier score overall, and the biggest gain early in the cycle, when the decision still matters (day 15: 0.181 against 0.114). It is somewhat cautious in the 70 to 90% band, where 98% of those cycles did cross. Full tables, calibration and limits are in [eval/RESULTS.md](eval/RESULTS.md). Reproduce them with:

```sh
uv run python eval/fetch_data.py
uv run python eval/backtest.py
```

## How it works

* `ainooru/tariff.py` holds both tariff versions (before and after 10 May 2026) as telescopic slab tables, with exact decimal billing.
* `ainooru/forecast.py` estimates the recent daily rate, weighted towards the last two weeks. It then simulates the rest of the cycle 4,000 times, with day-to-day variation that persists across days, uncertainty in the rate estimate, and a random reader delay. Every path ends in whole units and an exact bill.
* `ainooru/charts.py` draws the cycle chart as plain SVG on the server.
* The pages are Jinja templates served by FastAPI, with no JavaScript framework.

## Hosted demo

`modal_app.py` deploys the demo with `modal deploy modal_app.py`: a quarter CPU, 512 MB, scale to zero, `AINOORU_HOSTED=1`. In hosted mode every browser gets its own SQLite database in memory, keyed by a random cookie id (the oldest are dropped past 500). The Groq key is read from the local `.env` at deploy time and passed as a Modal secret; without it the photo option is hidden.

## Limitations

* Only energy charges are compared. Fixed charges depend on connected load and are the same either side of 500.
* The noise settings were fitted on one French household's data, not on Chennai homes. The backtest covers one home only.
* The tariff figures come from TNERC Order No. 4 of 2026 (consumer-payable rates per slab) and TNERC Order No. 5 of 2026 (200 free units up to 500), both on tnerc.tn.gov.in; see `DESIGN.md`. A future tariff order would need a new table in `ainooru/tariff.py`.
* Appliance conversions use typical ratings (for example 1.2 units an hour for a 1.5 ton inverter split AC) and say so on screen.
* Photo reading has been checked on a rendered meter display and with mocked responses, not on a broad set of real meter photos. It only ever suggests a number for the user to confirm.

## Credits

FastAPI, Jinja2, Uvicorn, NumPy, Pillow, httpx and pytest. Optional photo reading uses the open Qwen model served by Groq. Backtest data: UCI Individual household electric power consumption (Hebrail and Berard, 2006, CC BY 4.0). Tariff facts come from TNERC orders, cited in `DESIGN.md`. Built for LaunchPad Hacks 2026; all code was written during the event.
