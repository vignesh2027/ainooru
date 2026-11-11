# Devpost submission texts

Copy these into the LaunchPad Hacks project page. Every number here can be traced to the code, `eval/RESULTS.md` or the TNERC orders cited in `DESIGN.md`.

## Name

Ainooru

## Short pitch (tagline)

Tamil Nadu homes pay ₹478 extra for the 501st unit. Ainooru forecasts your two-month cycle from a few meter readings and tells you, before the reader comes, whether you will cross 500 and what to do about it.

## Links

* Try it live: https://ainooru.140-245-16-129.sslip.io (click "Try it with sample readings")
* Source code: [GITHUB REPO LINK]
* Demo video: https://youtu.be/5YScJBcHMBs

## Team

Solo: Vigneshwar (final-year CSE student, Chennai).

## The problem

Tamil Nadu bills household electricity every two months. Since 10 May 2026 (G.O. (Ms) No. 50, given effect by TNERC Order No. 5 of 2026), a home that uses 500 units or fewer in a cycle gets 200 units free. A home that uses 501 units gets only 100 free, and all its units are billed on a costlier table. In energy charges:

* 500 units cost ₹1,570.00.
* 501 units cost ₹2,048.40.

That single unit costs ₹478.40. Before May it cost ₹243.40, so the new scheme almost doubled the cliff. TNERC set aside a provisional subsidy of ₹1,545.14 crore for this scheme for 10 May 2026 to 31 March 2027, a measure of how many homes the scheme reaches.

Families see their consumption only when the meter reader comes, and by then the cycle is over. The meter itself shows a running total, but nothing tells a family what that number means for this cycle's bill.

## Intended users

Tamil Nadu households on the LT-IA domestic tariff whose two-month use is near 500 units: typically a family with one or two ACs, a water pump and a water heater. I built it for Chennai households like my own family's, so the app is fully bilingual in English and Tamil.

## What it does

* You enter the reading and date from the last bill, then add a meter reading whenever you remember. Weekly is enough.
* **Chance of crossing 500** by the reading date, allowing for a reader who comes a few days late.
* **Likely bill** as a median with an 8 in 10 range.
* **What a unit saved today is really worth**, counting the cliff. For a home on course for exactly 500 units this is about ₹10 at mid-cycle and passes ₹40 two days before a known reading date, against a printed rate of ₹4.70 to ₹6.30.
* **A daily unit budget** that brings the risk down to 10%, with the expected saving and what the cut means in hours of AC, water heater or pump.
* **An honest "the cliff is lost" message** when even halving use would not help, so the family stops giving up comfort for nothing.
* **Optional meter photo reading.** An open vision model reads the kWh number from a photo into the box. It is never saved automatically, and typing always works.

## How I built it

* **Python, managed with uv.** FastAPI serves Jinja templates rendered on the server, and the charts are plain SVG drawn by the server. There is no JavaScript framework; the browser receives HTML and CSS.
* **Tariff engine.** Both tariff versions are stored as telescopic slab tables with exact decimal billing. Tests rebuild every slab rate as approved tariff minus Government subsidy, straight from the tables in TNERC Orders 4 and 5 of 2026.
* **Forecaster.** It estimates the recent daily rate, weighted towards the last two weeks. NumPy then runs 4,000 simulated futures, each with day-to-day variation that persists across days, uncertainty in the rate estimate, and a random reader delay. Every path ends in whole units and an exact bill. The value of a saved unit is computed by comparing each path's bill with the same path one unit lower.
* **Storage.** SQLite on the user's own machine. The public demo, in one small container, gives each browser its own SQLite database in memory instead, so nothing is written to disk and it is wiped when the demo restarts.
* **Languages.** English and Tamil throughout, including the chart, dates and error messages.
* **Photo reading.** The `qwen/qwen3.8-27b` model on Groq's free tier, behind a feature switch. Without a key it is simply hidden.

## Does it work? (evaluation)

I backtested the forecaster on the public UCI household power dataset: one real home, December 2006 to November 2010, scaled so that its typical cycle sits at 500 units. I chose the noise settings on the first year only, then scored 282 forecasts on the following three years against the straight-line sum people do in their heads.

| Method | Brier score | Right side of 500 | Typical miss | 80% range held the truth |
|---|---|---|---|---|
| Straight line | 0.103 | 90% | 38 units | no range |
| Ainooru | 0.070 | 90% | 32 units | 84% |

It is no better at the yes-or-no call, but its probabilities are much more honest. Its Brier score is 32% lower overall, and the gap is largest early in the cycle (day 15: 0.181 against 0.114), when there is still time to act. The full tables are in `eval/RESULTS.md` and can be reproduced with two commands.

## Challenges

* **My own first claim was wrong.** I expected a saved unit near the cliff to be worth "many times" the slab rate at any point in the cycle. The forecaster showed that mid-cycle uncertainty spreads the ₹478 out, so the honest figure is about ₹10, rising sharply only near the reading date. I changed the product to show the measured number.
* **Finding the real tariff.** Press articles disagreed on rates and free units. I went to TNERC's own subsidy orders, which list approved tariff and subsidy per slab, and wrote tests against those tables.
* **Making uncertainty readable.** A chart of ranges means little at a glance, so each screen leads with one probability, one rupee value and a daily target in hours of AC, and keeps the chart for those who want it.

## What I learned

* How a telescopic tariff with an eligibility switch creates a decision problem, and how simulation turns "will we cross?" into a probability.
* Why a straight-line forecast can be right as often as a probabilistic one and still be worse to act on.
* How to evaluate a forecaster honestly: fit on one period, score on another, and report calibration and the cases where it is cautious.

## Limitations

* Only energy charges are compared. Fixed charges depend on connected load and are the same on both sides of 500.
* The backtest uses one household in France, because no public Chennai household data was available. The model is somewhat cautious in the 70 to 90% band, where 98% of those cycles did cross.
* Appliance conversions use typical ratings and tell the user to check their own labels.
* Photo reading was checked on a rendered meter display and with mocked responses, not on a broad set of real meter photos. It only suggests a number for the user to confirm.
* A future TNERC tariff order would need a new table in `ainooru/tariff.py`.

## Work done during the event

Everything in the repository was built during LaunchPad Hacks, starting 4 Nov 2026, and the git history shows each step. There is no pre-existing code.

## Setup steps (for judges)

```sh
git clone [GITHUB REPO LINK] ainooru
cd ainooru
uv sync
uv run uvicorn ainooru.app:app --port 8000
```

Or skip setup and use the live demo: https://ainooru.140-245-16-129.sslip.io

Open http://localhost:8000 and click "Try it with sample readings". Run the tests with `uv run pytest`. Photo reading is optional and needs a free Groq key in `.env` (see `.env.example`).

## Built with

python, uv, fastapi, jinja2, sqlite, numpy, pillow, httpx, svg, pytest, groq, modal

## Credits

* Libraries: FastAPI, Jinja2, Uvicorn, NumPy, Pillow, httpx, pytest.
* Data: UCI Individual household electric power consumption (Hebrail and Berard, 2006, CC BY 4.0).
* Tariff: TNERC Orders No. 4 and No. 5 of 2026.
* Optional photo reading: the open Qwen model hosted by Groq.
* Hosting for the public demo: an Oracle Cloud Always Free VM (Docker behind Caddy); `modal_app.py` is kept as an alternative host.
* [AI-ASSISTANCE CREDITS LINE]

## Owner checklist before submitting

* Replace [GITHUB REPO LINK] (twice) and https://youtu.be/5YScJBcHMBs above. The demo video is recorded (see /Users/vignesh/dev-challenges/nov/video/ainooru-demo-notes.md).
* Upload screenshots from `docs/screenshots/`.
* If possible, try one real meter photo and one real cycle with your family, and add one true sentence on how it went (for example under The problem or Challenges). Do not add it if it did not happen.
* Replace [AI-ASSISTANCE CREDITS LINE] in Credits.
