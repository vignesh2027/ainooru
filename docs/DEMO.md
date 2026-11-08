# Two-minute demo script

Setup before recording:

* Recorded on the hosted demo, https://applemacbook6sep2004--ainooru.us-east.modal.run, in a fresh browser profile (each browser gets its own household, so it starts on the setup screen). The photo step works there.

* `uv run uvicorn ainooru.app:app --port 8000`, open http://localhost:8000, browser window about 1280 wide, zoom 100%.
* Click "Start a new cycle" if a cycle is already loaded, so the recording starts on the setup screen in English.
* Optional: put `GROQ_API_KEY` in `.env` and have a clear photo of a real meter display ready on the computer. Without a key, skip the photo step and type the reading.

The sample figures below are what the sample household shows on any day, because its readings are dated relative to today and the simulation uses a fixed seed.

| Time | On screen | Say |
|---|---|---|
| 0:00 | Setup screen, headline "One extra unit can cost ₹478.40." | "In Tamil Nadu, electricity is billed every two months. Since May this year, a home that stays at 500 units gets 200 units free. At 501 it gets only 100, and the whole bill moves to a costlier table." |
| 0:15 | Point at the two boxes: ₹1,570.00 and ₹2,048.40 | "So 500 units cost ₹1,570, and 501 units cost ₹2,048. One unit, ₹478. Before May that step was ₹243; the new scheme almost doubled it. These rates are checked against TNERC's own orders." |
| 0:30 | Click "Try it with sample readings" | "Families only see the meter when the reader comes, which is too late. Ainooru takes the reading from the last bill and a few readings since then." |
| 0:40 | Hero: "67% chance of crossing 500 units" | "This home has used 289 units in 34 days. Ainooru simulates the rest of the cycle 4,000 times, including the meter reader coming up to 3 days late, and says: a 67% chance of crossing." |
| 0:55 | Stat tile "A unit saved today is worth ₹11.42" | "Here is the part people do not see. The printed rate near 500 is ₹4.70 to ₹6.30. Counting the cliff, a unit saved today is worth ₹11.42 to this family, and that value climbs as the reading day gets close." |
| 1:10 | Budget card and appliance chips | "So it gives a plan. Keep to 6 units a day instead of 8.6 and the risk drops to 10%. That is about 71 fewer units for an expected saving of ₹779, roughly two hours less AC a day." |
| 1:25 | Scroll to the chart | "The chart shows the readings so far, the range it is heading for, and the window when the reader may come." |
| 1:35 | Click "தமிழ்" at the top right | "Many families here read Tamil first, so every screen, chart and message is in Tamil too." |
| 1:45 | Back to English. Under "Add today's meter reading", choose the meter photo, click "Read the photo"; the number fills the box | "Reading the meter is the chore. Optionally, snap a photo and an open vision model reads the kWh number into the box. It never saves on its own: you check it and press Add. Typing always works." |
| 1:55 | Show README section "Does the forecast hold up?" | "And it is tested: on three years of a real household's data its Brier score was 32% lower than straight-line guessing, which means more honest probabilities. Ainooru: stay under 500." |

Fallback if the photo step fails during recording: type the reading and say "or just type it".
