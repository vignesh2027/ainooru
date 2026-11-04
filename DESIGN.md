# Ainooru: design notes

Ainooru (ஐநூறு) is Tamil for "five hundred", the bimonthly unit limit this project is about.

## The person this is for

The owner is a final-year CSE student in Chennai. The ideas below all come from problems in that life: the household electricity bill, campus placement season, the monsoon commute, the final-year viva and hostel food. Each one has a person we can name as the user.

Hard constraints from the brief: the idea must be new (not Padi, Kavach, Haat or Merged), demoable in 2 minutes, free to run with no card, honest about numbers, and built in Python or Go with server-rendered HTML.

## Five candidates

### 1. Ainooru: a bill-cliff forecaster for Tamil Nadu homes

Tamil Nadu bills domestic electricity every two months. Since G.O. (Ms) No. 50 of 10 May 2026 (backed by TNERC Order No. 5 of 2026), a home that uses 500 units or fewer in a cycle gets 200 units free. A home that uses 501 units gets only 100 units free and moves onto the higher slab table. Using the published slab rates:

* 500 units cost Rs 1,570.00 in energy charges.
* 501 units cost Rs 2,048.40.

That one extra unit costs **Rs 478.40**. Before May 2026 the same step cost Rs 243.40, so the cliff almost doubled this year. A household sees its consumption only when the meter reader comes, by which time it is too late.

Ainooru takes a few meter readings, which anyone can read off the LCD in ten seconds. It runs a probabilistic forecast of where the cycle will end, allowing for the uncertain reading date, and reports three things:

* the chance of crossing 500;
* the **cliff-aware price of a unit saved today**. Near the cliff it is about Rs 10 at mid-cycle and above Rs 40 in the last two days, against printed rates of Rs 4.70 and Rs 6.30. These figures were measured with the forecaster; an earlier draft guessed it would be "many times" the slab rate, which overstated the mid-cycle case;
* a daily unit budget that keeps the risk under a chosen level, translated into appliance hours.

It also says when the cliff is already lost, so the family stops sacrificing comfort for nothing.

The user is a Tamil Nadu household on the LT-IA domestic tariff, such as my own family in Chennai. The need is public: the cut-off has drawn press coverage and complaints from households "slightly above 500 units".

### 2. Drive Desk: a placement-drive notice parser

The placement cell forwards 5 to 15 drive notices a week on WhatsApp and email. Each one buries its eligibility (CGPA cut-off, standing arrears, branch, batch, 10th and 12th marks) and its registration deadline in a PDF or a wall of text. Drive Desk would parse a notice, check it against the student's profile and produce a calendar entry. The user is a final-year student at my college.

### 3. Subway Sense: Chennai underpass flood risk

Chennai's vehicular subways close during heavy northeast-monsoon rain, and commuters learn this only on arrival. Subway Sense would combine an Open-Meteo rainfall nowcast with per-subway thresholds and suggest a dry route. The user is a Chennai commuter in November.

### 4. Viva Mock: a final-year project viva examiner

This would read the student's project report, ask likely viva questions, and grade spoken answers against the report with citations. The user is an Anna University final-year student before the April viva.

### 5. Mess Count: a hostel mess headcount forecaster

This would predict tomorrow's mess headcount from attendance, exams and holidays so the kitchen cooks less surplus. The user is a hostel mess manager.

## Scoring

The four judging criteria, quoted verbatim from the rules page:

* **Innovation & Originality:** "How original is the idea or approach? Does the project offer a fresh solution, thoughtful improvement, or creative use of technology?"
* **Usefulness & Impact:** "How clearly does the project address a real problem or opportunity? Consider its value to the intended users, evidence of user needs, and potential positive impact."
* **Implementation & Functionality:** "How well does the working prototype deliver its core promise? Consider functionality, thoughtful technical choices, reliability, and what the team built during the event. Complexity alone does not earn a higher score."
* **Design & Presentation:** "Is the project understandable and easy to use? Consider accessibility, the clarity of the user experience, and how clearly the submission explains the problem, solution, demo, and limitations."

The fifth column, **Gallery originality**, is my own check. The LaunchPad gallery is unpublished, so this column compares each idea against the visible galleries of comparable ended events listed in RULES.md (Hack to the Future, Neighborhood Hacks 2026, Student Innovators Without Borders). Each score is 1 to 5. The first four columns are what judges add up; the fifth breaks ties between my own options.

| Candidate | Innovation | Usefulness | Implementation | Design | Judged total (of 20) | Gallery originality | Total (of 25) |
|---|---|---|---|---|---|---|---|
| 1. Ainooru | 5 | 5 | 4 | 5 | **19** | 5 | **24** |
| 2. Drive Desk | 3 | 4 | 4 | 4 | 15 | 2 | 17 |
| 3. Subway Sense | 4 | 4 | 2 | 3 | 13 | 4 | 17 |
| 4. Viva Mock | 3 | 3 | 4 | 4 | 14 | 2 | 16 |
| 5. Mess Count | 2 | 3 | 3 | 3 | 11 | 2 | 13 |

### Reasons behind the scores

**Ainooru.**
* Innovation 5. No student tool I found treats a subsidy cliff as a decision problem under uncertainty. The idea of a "price of one saved unit" that swings from Rs 6 to hundreds of rupees is new to most people and easy to state.
* Usefulness 5. The cliff is in force now, applies to about 2 crore domestic connections, and costs a real household Rs 478 or more for one unit. The press coverage gives evidence of need. My own family can try it this week.
* Implementation 4. The tariff engine is exact and testable against published worked examples, and the forecaster is a small, honest Monte Carlo. The risk is calibration, which the evaluation plan below covers.
* Design 5. The core screen holds one number, one chart and one sentence of advice. Tamil labels make it usable by the actual user.
* Gallery originality 5. No comparable gallery has anything on utility tariffs.

**Drive Desk.** Usefulness is real, but the idea is a cousin of "Google Classroom: Hidden Deadlines" and many deadline trackers, and it needs real notices that contain classmates' data. Gallery originality is 2.

**Subway Sense.** The idea is strong, but no public ground truth for closures exists, so accuracy cannot be shown honestly. The demo also depends on it raining on the day. Implementation is 2.

**Viva Mock.** It is useful, but it falls in the crowded space of automated tutors and mock interviewers. Gallery originality is 2.

**Mess Count.** It needs data from a real mess that I do not have, and food-waste dashboards are common.

**Choice: Ainooru.** It has the highest total, and it also wins the event's first tie-breaker, Usefulness & Impact. It wins the second tie-breaker too, because its core, the tariff engine and forecaster, is verifiable by tests and a backtest instead of by trust.

## Name search (4 Nov 2026)

The working name was "Minnal" (lightning). I dropped it because it is heavily used: 234 GitHub repositories, including the `minnal/minnal` REST framework, and the 2021 film "Minnal Murali". I then checked two Tamil words tied to the idea.

| Check | Vilimbu (விளிம்பு, "brink") | **Ainooru (ஐநூறு, "five hundred")** |
|---|---|---|
| GitHub repositories with the name | 0 | 0 |
| GitHub users and organisations | empty org `vilimbu` (created 22 Oct 2026, 0 repos), one personal user | one personal user, `AinooruKodiDaa` (no product) |
| GitHub code mentions | 356, mostly Tamil text, a short film page and an audiobook entry | 59, all number-word lists in Tamil and Kannada lessons |
| Apple App Store (India and US search API) | no app with this name | no app with this name |
| Google Play search (India) | fuzzy matches only, none named Vilimbu | fuzzy matches only, none named Ainooru |
| Web search | a novel titled Vilimbu by Sujatha, an amateur short film | a village spelled Ayanooru in Karnataka, and the dictionary word |
| Domains | vilimbu.com registered (no site responds) | ainooru.com, ainooru.in and ainooru.app do not resolve |

**Decision: Ainooru.** No product, app, company or brand uses it. The word is the generic numeral, which is fine for a project name and tells the user exactly what the tool protects. Vilimbu was close, but it is the title of a well-known novel and its .com is taken. I did not run a formal search of the Indian trademark register; that is listed as a limitation.

## Logo

The mark is original and built from the idea itself. A white usage line climbs to a dotted limit line, and at the deep violet point where it meets the limit the line jumps straight up: the bill's cliff. It sits on a primary-blue rounded tile. It uses only theme colours (#2563EB, #4C1D95, white, and a light tint of the primary) and contains no letterform or borrowed symbol. Files: `assets/logo.svg` (also served as `ainooru/static/logo.svg`) and `assets/logo-512.png` (512 by 512, transparent corners, rendered from the SVG in headless Chrome).

## Facts Ainooru depends on (with sources)

Tamil Nadu LT-IA domestic energy charges per bimonthly cycle, telescopic:

| Slab | 500 units or fewer (since 10 May 2026) | 500 or fewer (before 10 May 2026) | More than 500 units |
|---|---|---|---|
| 1 to 100 | 0 | 0 | 0 |
| 101 to 200 | 0 | 2.35 | 4.70 |
| 201 to 400 | 4.70 | 4.70 | 4.70 |
| 401 to 500 | 6.30 | 6.30 | 6.30 |
| 501 to 600 | | | 8.40 |
| 601 to 800 | | | 9.45 |
| 801 to 1000 | | | 10.50 |
| above 1000 | | | 11.55 |

**Primary sources (checked 4 Nov 2026 on tnerc.tn.gov.in, Tariff Orders page):**

* TNERC Order No. 4 of 2026, "Provisional Tariff Subsidy Order for FY 2026-27", dated 27 April 2026 (https://tnerc.tn.gov.in/Orders/files/TO-Order%20No%20280420261156.pdf). Its section "Domestic Consumers - LT Tariff I-A" lists, for each slab, the approved tariff, the subsidy paid by the Government and the energy charge payable by the consumer from 1 July 2025. Every rate in the two right-hand columns above is that payable figure, for example 101 to 200 units at 495 minus 260, which is 235 paise.
* TNERC Order No. 5 of 2026, "Additional Tariff Subsidy Order for FY 2026-27 due to increase of free electricity of total 200 units bimonthly to domestic consumers who consumes electricity upto 500 units bimonthly", dated 26 May 2026 (https://tnerc.tn.gov.in/Orders/files/TO-Order%20No%20270520261449.pdf). It records G.O. (Ms) No. 50 dated 10 May 2026, which makes 200 units free from 10 May 2026 for consumers up to 500 units, through an extra subsidy of 2.35 per unit on 101 to 200. It also states that consumers above 500 units keep "the existing tariff structure... including free electricity of 100 units bimonthly".
* `tests/test_tariff.py` rebuilds every slab rate as approved tariff minus subsidy from these two orders' tables.

**Secondary sources that agree:** Verified.RealEstate, "Tamil Nadu Electricity Charges 2026" (May 2026), gives the worked examples of 500 units at Rs 1,570 and 600 units at Rs 2,880, which the tests also pin. SolarQuarter (29 May 2026) and Mercom India report the order, and DT Next's "save Rs 235" equals 100 units at 2.35.

* Fixed charges depend on connected load and do not change at the cliff, so Ainooru leaves them out of the comparison and says so on screen.

Nothing in the tariff is hard-coded in templates. It lives in one versioned table in `ainooru/tariff.py`, and tests pin both the official per-slab rates and the published worked examples.

## How the forecast works

Inputs:

* the date and meter reading of the last bill, which is printed on the card or SMS;
* the expected date of the next reading (default: 60 days later);
* how many days late the reader may come (user setting, default 0 to 3 days, shown as an assumption);
* one or more of today's meter readings, entered whenever the user remembers.

Model:

1. The daily rate comes from the readings so far, weighting recent intervals more heavily.
2. Day-to-day variation is multiplicative log-normal noise with day-to-day persistence (AR(1)), because hot spells and guests last several days. The noise parameters come from the household's own readings when there are enough of them. Otherwise Ainooru uses defaults estimated from the public dataset in the evaluation, and the screen labels which source was used.
3. Monte Carlo runs 4,000 paths with a fixed seed. Each path draws a reading date and the daily usage until then, and gives total units and a bill.

Outputs:

* **Chance of crossing 500.**
* **Bill range:** P10, median and P90.
* **Price of a unit saved today:** the expected bill minus the expected bill with one unit fewer, using common random numbers. Far from the cliff this equals the slab rate. Near it, the cliff's Rs 478.40 is spread over the probability mass near 500.
* **Safe daily budget:** the largest daily rate from now on that keeps the chance of crossing under 10%, found by bisection. Ainooru shows it next to the current rate and converts the gap into hours of a typical appliance. The wattages are typical ratings, labelled "check your appliance label".
* **Cliff already lost:** if even halving usage leaves the chance of crossing above 90%, Ainooru says so and quotes the normal marginal rate instead.

## Honest evaluation plan

* **Tariff:** unit tests against the published worked examples, plus checks on structure (monotone within each regime, and the exact cliff values 478.40 and 243.40).
* **Forecaster:** a backtest on a public household dataset, the UCI "Individual household electric power consumption" set (one home, about 4 years of minute-level data). I will cut it into rolling 60-day cycles and forecast at days 15, 30 and 45 from a few simulated readings. The threshold is set at the household's own median cycle total, so roughly half the cycles cross it. I will report Brier score and calibration of the crossing probability against naive straight-line extrapolation, which is what people do in their heads. The data is French, not Chennai, and the write-up will say so.
* Every number in the README and on Devpost will come from a script in `eval/` that anyone can rerun.

## Stack

* Python 3.12, managed with uv. FastAPI serves Jinja2 templates. Storage is SQLite from the standard library.
* Charts are inline SVG rendered on the server, so the browser needs no chart library.
* Inline JS is limited to a few lines, for example a language toggle.
* The only optional external call reads the meter from a photo, using an open vision model on Groq's free tier. Typing the reading is the fallback and always works.
* pytest for tests.
* Theme: background #F4F9FF, surface #FFFFFF, primary #2563EB, text #0B1B33, accent #4C1D95, danger #9F1239.

## Build order

1. Tariff engine with tests.
2. Forecaster with tests.
3. One-page web app (enter readings, see the forecast). This is the first end-to-end slice.
4. Polish: Tamil labels, a cycle history, appliance conversion, and meter-photo reading with a manual fallback.
5. Backtest in `eval/`, and wire its numbers into the README.
6. 2-minute demo script and screenshots.
