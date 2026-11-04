"""English and Tamil text for every screen. Numbers stay in Western digits, as on TNPDCL bills."""

from __future__ import annotations

from datetime import date

from markupsafe import Markup, escape

LANGS = ("en", "ta")

# Keys whose text contains our own <b> markup. Arguments are escaped before formatting.
HTML_KEYS = {"budget_body"}

S: dict[str, dict[str, str]] = {
    "title": {"en": "Ainooru: stay under 500 units", "ta": "ஐநூறு: 500 யூனிட்டுக்குள் இருங்கள்"},
    "brand": {"en": "Ainooru", "ta": "ஐநூறு"},
    "brand_sub": {"en": "Stay under 500 units", "ta": "500 யூனிட்டுக்குள் இருங்கள்"},
    "pill": {"en": "Tamil Nadu domestic tariff, from 10 May 2026", "ta": "தமிழ்நாடு வீட்டு மின் கட்டணம், 10 மே 2026 முதல்"},
    "switch": {"en": "தமிழ்", "ta": "English"},
    "footer": {
        "en": "Energy charges only. Fixed charges depend on your connected load and are the same on both sides of 500, "
              "so they are left out. Readings stay in a file on this computer.",
        "ta": "இது மின் ஆற்றல் கட்டணம் மட்டுமே. நிலைக் கட்டணம் உங்கள் இணைப்புச் சுமையைப் பொறுத்தது; 500க்கு இருபுறமும் "
              "ஒன்றே என்பதால் சேர்க்கப்படவில்லை. அளவீடுகள் இந்தக் கணினியிலேயே சேமிக்கப்படும்.",
    },
    "tariff_source": {"en": "Tariff source:", "ta": "கட்டண ஆதாரம்:"},
    # Setup
    "setup_h1": {"en": "One extra unit can cost ₹{cliff}.", "ta": "ஒரே ஒரு யூனிட் கூடுதலானால் ₹{cliff} அதிகம் ஆகலாம்."},
    "setup_lead": {
        "en": "Tamil Nadu bills homes every two months. At 500 units or fewer, the first 200 units are free. At 501, only 100 "
              "are free and a costlier table applies. Ainooru watches your meter and tells you, before the reader comes, "
              "whether you will cross the line and what to do about it.",
        "ta": "தமிழ்நாட்டில் வீட்டு மின் கட்டணம் இரண்டு மாதத்திற்கு ஒருமுறை கணக்கிடப்படுகிறது. 500 யூனிட் வரை பயன்படுத்தினால் "
              "முதல் 200 யூனிட் இலவசம். 501 யூனிட் ஆனால் 100 யூனிட் மட்டுமே இலவசம், மேலும் அதிக விலை அட்டவணை பொருந்தும். "
              "மீட்டர் கணக்கெடுப்பவர் வருவதற்கு முன்பே, நீங்கள் இந்த எல்லையைத் தாண்டுவீர்களா, அதற்கு என்ன செய்யலாம் என்பதை "
              "ஐநூறு சொல்லும்.",
    },
    "start_h": {"en": "Start with your last bill", "ta": "கடைசி கட்டண விவரத்திலிருந்து தொடங்குங்கள்"},
    "f_start_day": {"en": "Date of the last meter reading", "ta": "கடைசி மீட்டர் கணக்கெடுப்பு தேதி"},
    "f_start_reading": {"en": "Meter reading on that bill (kWh)", "ta": "அப்போதைய மீட்டர் அளவீடு (kWh)"},
    "f_placeholder": {"en": "for example 18240", "ta": "உதாரணமாக 18240"},
    "f_expected_end": {
        "en": "Next reading expected on (optional, default 60 days later)",
        "ta": "அடுத்த கணக்கெடுப்பு தேதி (விருப்பம்; இல்லையெனில் 60 நாள் கழித்து)",
    },
    "f_late": {"en": "The reader may come up to this many days late", "ta": "கணக்கெடுப்பவர் எத்தனை நாள் வரை தாமதமாக வரலாம்"},
    "btn_start": {"en": "Start tracking", "ta": "கண்காணிக்கத் தொடங்கு"},
    "cliff_h": {"en": "The cliff, in rupees", "ta": "500க்கும் 501க்கும் உள்ள வித்தியாசம்"},
    "units_n": {"en": "{n} units", "ta": "{n} யூனிட்"},
    "cliff_note": {
        "en": "Energy charges for one two-month cycle. Before 10 May 2026 the same single unit cost ₹{old} extra; "
              "the new 200 free units almost doubled the cliff.",
        "ta": "இரண்டு மாதக் கணக்கிற்கான மின் ஆற்றல் கட்டணம். 10 மே 2026க்கு முன் இதே ஒரு யூனிட்டுக்கு ₹{old} கூடுதல்; "
              "புதிய 200 இலவச யூனிட் திட்டத்தால் இந்த வித்தியாசம் ஏறக்குறைய இரட்டிப்பானது.",
    },
    "btn_sample": {"en": "Try it with sample readings", "ta": "மாதிரி அளவீடுகளுடன் பார்க்க"},
    # Dashboard
    "sample_banner": {"en": "You are looking at made-up sample readings.", "ta": "இவை கற்பனையான மாதிரி அளவீடுகள்."},
    "sample_own": {"en": "Start with your own bill", "ta": "உங்கள் சொந்தக் கட்டணத்துடன் தொடங்குங்கள்"},
    "hero_over": {"en": "Already past {T} units this cycle", "ta": "இந்தக் கணக்கில் ஏற்கனவே {T} யூனிட்டைத் தாண்டிவிட்டது"},
    "hero_p": {"en": "{p}% chance of crossing {T} units", "ta": "{T} யூனிட்டைத் தாண்ட {p}% வாய்ப்பு"},
    "advice_over": {
        "en": "This cycle has already passed {T} units, so it is billed on the higher table. "
              "From here each unit costs the normal slab rate of ₹8.40 to ₹11.55.",
        "ta": "இந்தக் கணக்கு ஏற்கனவே {T} யூனிட்டைத் தாண்டிவிட்டதால் அதிக கட்டண அட்டவணையில் கணக்கிடப்படும். "
              "இனி ஒவ்வொரு யூனிட்டும் ₹8.40 முதல் ₹11.55 வரை.",
    },
    "advice_lost": {
        "en": "Even halving use from today would very likely end above {T}. The cliff is lost for this cycle, so cutting "
              "back now saves only about {v} a unit. Do not give up comfort for it.",
        "ta": "இன்றிலிருந்து பயன்பாட்டைப் பாதியாகக் குறைத்தாலும் {T}ஐத் தாண்டவே வாய்ப்பு அதிகம். இந்தக் கணக்கில் அந்த "
              "எல்லை கை நழுவிவிட்டது; இப்போது குறைத்தால் ஒரு யூனிட்டுக்குச் சுமார் {v} மட்டுமே மிச்சம். அதற்காக வசதியை "
              "விட்டுக்கொடுக்க வேண்டாம்.",
    },
    "advice_safe": {
        "en": "On track to stay at or under {T} units. Keep going as you are.",
        "ta": "{T} யூனிட்டுக்குள் இருக்கும் பாதையில் இருக்கிறீர்கள். இப்படியே தொடருங்கள்.",
    },
    "advice_cut": {
        "en": "Keep to {safe} units a day (now {rate}). That is {cut} units a day less.",
        "ta": "நாளொன்றுக்கு {safe} யூனிட்டுக்குள் வைத்துக்கொள்ளுங்கள் (இப்போது {rate}). அதாவது நாளொன்றுக்கு {cut} யூனிட் குறைவு.",
    },
    "used_label": {"en": "Used so far", "ta": "இதுவரை பயன்பாடு"},
    "used_sub": {
        "en": "in {d} days, about {r} a day. Reading due in {left} days.",
        "ta": "{d} நாட்களில், நாளொன்றுக்குச் சுமார் {r}. கணக்கெடுப்புக்கு இன்னும் {left} நாள்.",
    },
    "bill_label": {"en": "Likely bill (energy)", "ta": "எதிர்பார்க்கும் கட்டணம் (மின் ஆற்றல்)"},
    "bill_sub": {
        "en": "8 in 10 chance between {lo} and {hi}. Likely {u} units.",
        "ta": "10இல் 8 வாய்ப்பு {lo} முதல் {hi} வரை. பெரும்பாலும் {u} யூனிட்.",
    },
    "unit_label": {"en": "A unit saved today is worth", "ta": "இன்று சேமிக்கும் ஒரு யூனிட்டின் மதிப்பு"},
    "unit_sub": {
        "en": "on average, cliff included. The printed rate near 500 is ₹4.70 to ₹6.30.",
        "ta": "சராசரியாக, எல்லைத் தாண்டலின் விலையும் சேர்த்து. 500க்கு அருகில் அச்சிடப்பட்ட விலை ₹4.70 முதல் ₹6.30.",
    },
    "budget_h": {"en": "Your daily budget", "ta": "உங்கள் தினசரி அளவு"},
    "budget_body": {
        "en": "Keep to <b>{safe} units a day</b> until the reading and the chance of crossing drops to {target}%. "
              "That means using about {units} fewer units this cycle, and it saves about <b>{saving}</b> on average, "
              "or {per} for every unit you give up.",
        "ta": "கணக்கெடுப்பு வரை நாளொன்றுக்கு <b>{safe} யூனிட்டுக்குள்</b> இருந்தால், தாண்டும் வாய்ப்பு {target}% ஆகக் "
              "குறையும். இந்தக் கணக்கில் சுமார் {units} யூனிட் குறைவாகப் பயன்படுத்த வேண்டும்; சராசரியாக <b>{saving}</b> "
              "மிச்சம், அதாவது விட்டுக்கொடுக்கும் ஒவ்வொரு யூனிட்டுக்கும் {per}.",
    },
    "cut_as": {"en": "{cut} units a day is about", "ta": "நாளொன்றுக்கு {cut} யூனிட் என்பது சுமார்"},
    "chip": {"en": "{h} h less {name}", "ta": "{name} {h} மணி நேரம் குறைவு"},
    "appliance_note": {
        "en": "Typical ratings in units an hour: {list}. Check the label on your own appliance.",
        "ta": "வழக்கமான மின் அளவு (மணிக்கு யூனிட்): {list}. உங்கள் சாதனத்தின் லேபிளைச் சரிபாருங்கள்.",
    },
    "ac15": {"en": "1.5 ton AC", "ta": "1.5 டன் ஏசி"},
    "ac1": {"en": "1 ton AC", "ta": "1 டன் ஏசி"},
    "geyser": {"en": "water heater", "ta": "வாட்டர் ஹீட்டர்"},
    "motor": {"en": "1 HP water pump", "ta": "1 HP தண்ணீர் மோட்டார்"},
    "iron": {"en": "iron box", "ta": "அயர்ன் பாக்ஸ்"},
    "fan": {"en": "ceiling fan", "ta": "மின்விசிறி"},
    "chart_h": {"en": "This cycle", "ta": "இந்தக் கணக்குக் காலம்"},
    "legend_readings": {"en": "Your readings", "ta": "உங்கள் அளவீடுகள்"},
    "legend_band": {"en": "Where it is heading (8 in 10 range)", "ta": "செல்லும் திசை (10இல் 8 வாய்ப்பு வரம்பு)"},
    "legend_window": {"en": "Reader may come", "ta": "கணக்கெடுப்பவர் வரக்கூடிய நாட்கள்"},
    "legend_line": {"en": "{T}-unit line", "ta": "{T} யூனிட் எல்லை"},
    "chart_due": {"en": "reading due", "ta": "கணக்கெடுப்பு"},
    "chart_units": {"en": "units used", "ta": "பயன்பட்ட யூனிட்"},
    "chart_line": {"en": "{T} units: free units drop from 200 to 100", "ta": "{T} யூனிட்: இலவசம் 200இலிருந்து 100 ஆகக் குறையும்"},
    "chart_line_short": {"en": "{T} units", "ta": "{T} யூனிட்"},
    "chart_aria": {
        "en": "Units used this cycle: {used} so far. Likely total {p50} units, 80 percent range {p10} to {p90}. Threshold {T}.",
        "ta": "இந்தக் கணக்கில் இதுவரை {used} யூனிட். மொத்தம் பெரும்பாலும் {p50} யூனிட், 80 சதவீத வரம்பு {p10} முதல் {p90}. எல்லை {T}.",
    },
    "add_h": {"en": "Add today's meter reading", "ta": "இன்றைய மீட்டர் அளவீட்டைச் சேர்க்கவும்"},
    "f_date": {"en": "Date", "ta": "தேதி"},
    "f_reading": {"en": "Reading (kWh)", "ta": "அளவீடு (kWh)"},
    "btn_add": {"en": "Add", "ta": "சேர்"},
    "add_note": {
        "en": "Read the kWh number on the meter display. One reading a week is enough; more readings make the forecast tighter.",
        "ta": "மீட்டர் திரையில் உள்ள kWh எண்ணைப் படியுங்கள். வாரத்திற்கு ஒரு அளவீடு போதும்; அதிக அளவீடுகள் கணிப்பைத் துல்லியமாக்கும்.",
    },
    "readings_h": {"en": "Readings", "ta": "அளவீடுகள்"},
    "th_date": {"en": "Date", "ta": "தேதி"},
    "th_reading": {"en": "Reading", "ta": "அளவீடு"},
    "th_since": {"en": "Units since bill", "ta": "கட்டணத்திற்குப் பின் யூனிட்"},
    "last_bill": {"en": "last bill", "ta": "கடைசி கட்டணம்"},
    "delete": {"en": "Delete", "ta": "நீக்கு"},
    "how_h": {"en": "How this is worked out", "ta": "இது எப்படிக் கணக்கிடப்படுகிறது"},
    "how_body": {
        "en": "Ainooru estimates your recent daily use, weighting the last two weeks most, then simulates the rest of the "
              "cycle 4,000 times. Each run varies how much you use from day to day, how wrong the estimate might be, and how "
              "many days late the reader comes (up to {late}). Every run ends in a whole number of units and an exact bill "
              "from the tariff table.",
        "ta": "ஐநூறு உங்கள் சமீபத்திய தினசரி பயன்பாட்டை, கடைசி இரண்டு வாரங்களுக்கு அதிக முக்கியத்துவம் கொடுத்துக் கணக்கிட்டு, "
              "மீதமுள்ள நாட்களை 4,000 முறை உருவகப்படுத்துகிறது. ஒவ்வொரு முறையும் நாளுக்கு நாள் மாறும் பயன்பாடு, மதிப்பீட்டில் "
              "இருக்கக்கூடிய பிழை, கணக்கெடுப்பவர் எத்தனை நாள் தாமதமாக வருவார் (அதிகபட்சம் {late}) ஆகியவை மாறுகின்றன. ஒவ்வொரு "
              "முடிவும் முழு யூனிட்டாகவும், கட்டண அட்டவணைப்படி சரியான தொகையாகவும் முடிகிறது.",
    },
    "how_noise": {
        "en": "Day-to-day variation was fitted on one year of a public household dataset and tested on three more "
              "(spread {s}, persistence {p}). Cycle {a} to about {b}.",
        "ta": "நாளுக்கு நாள் மாறுபாடு ஒரு பொது வீட்டு மின் தரவுத்தொகுப்பின் ஓராண்டுத் தரவில் பொருத்தப்பட்டு, அடுத்த மூன்று "
              "ஆண்டுகளில் சோதிக்கப்பட்டது (பரவல் {s}, தொடர்ச்சி {p}). கணக்குக் காலம் {a} முதல் சுமார் {b} வரை.",
    },
    "btn_new": {"en": "Start a new cycle", "ta": "புதிய கணக்குக் காலத்தைத் தொடங்கு"},
    "photo_label": {"en": "Or take a photo of the meter", "ta": "அல்லது மீட்டரைப் புகைப்படம் எடுக்கவும்"},
    "btn_photo": {"en": "Read the photo", "ta": "புகைப்படத்தைப் படி"},
    "photo_note": {
        "en": "The photo is sent to an open model on Groq to read the number. Ainooru does not keep it.",
        "ta": "எண்ணைப் படிக்க, புகைப்படம் Groq இல் உள்ள ஒரு திறந்த மாதிரிக்கு அனுப்பப்படும். ஐநூறு அதைச் சேமிப்பதில்லை.",
    },
    "prefill_note": {
        "en": "Read from your photo: {v}. Check it matches the meter, then press Add.",
        "ta": "உங்கள் புகைப்படத்திலிருந்து படித்தது: {v}. மீட்டருடன் ஒப்பிட்டுச் சரிபார்த்து, பிறகு சேர் அழுத்தவும்.",
    },
    # Errors
    "err_photo": {
        "en": "Could not read a number from that photo. Please type the reading instead.",
        "ta": "அந்தப் புகைப்படத்திலிருந்து எண்ணைப் படிக்க முடியவில்லை. அளவீட்டைத் தட்டச்சு செய்யவும்.",
    },
    "err_future": {"en": "The last bill's reading date cannot be in the future.", "ta": "கடைசி கணக்கெடுப்பு தேதி எதிர்காலத்தில் இருக்க முடியாது."},
    "err_negative": {"en": "A meter reading cannot be negative.", "ta": "மீட்டர் அளவீடு எதிர்மறையாக இருக்க முடியாது."},
    "err_end": {"en": "The next reading date must be after the last one.", "ta": "அடுத்த கணக்கெடுப்பு தேதி கடைசி தேதிக்குப் பிறகு இருக்க வேண்டும்."},
    "err_setup": {"en": "Set up the cycle first.", "ta": "முதலில் கணக்குக் காலத்தை அமையுங்கள்."},
    "err_range": {
        "en": "The reading date must be between the last bill and today.",
        "ta": "அளவீட்டுத் தேதி கடைசி கட்டணத்திற்கும் இன்றைக்கும் இடையில் இருக்க வேண்டும்.",
    },
    "err_lower": {
        "en": "{v} is lower than an earlier reading of {floor}. Check the number on the meter.",
        "ta": "{v} என்பது முந்தைய அளவீடான {floor}ஐ விடக் குறைவு. மீட்டரில் உள்ள எண்ணைச் சரிபாருங்கள்.",
    },
    "err_order": {
        "en": "Readings must not go down over time. Check the numbers.",
        "ta": "அளவீடுகள் காலப்போக்கில் குறையக்கூடாது. எண்களைச் சரிபாருங்கள்.",
    },
}

MONTHS_TA = ("ஜன", "பிப்", "மார்", "ஏப்", "மே", "ஜூன்", "ஜூலை", "ஆக", "செப்", "அக்", "நவ", "டிச")


def translator(lang: str):
    lang = lang if lang in LANGS else "en"

    def t(key: str, **kw):
        text = S[key][lang]
        if key in HTML_KEYS:
            return Markup(text.format(**{k: escape(v) for k, v in kw.items()}))
        return text.format(**kw) if kw else text

    return t


def fmt_day(d: date, lang: str, year: bool = False) -> str:
    month = MONTHS_TA[d.month - 1] if lang == "ta" else d.strftime("%b")
    return f"{d.day} {month}" + (f" {d.year}" if year else "")
