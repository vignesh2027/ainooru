from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AINOORU_DB", str(tmp_path / "t.sqlite3"))
    from ainooru.app import app

    return TestClient(app)


def test_setup_page_shows_the_cliff(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "₹1,570.00" in r.text and "₹2,048.40" in r.text
    assert "478.40" in r.text


def test_sample_flow(client):
    r = client.post("/sample", follow_redirects=True)
    assert r.status_code == 200
    assert "chance of crossing 500 units" in r.text
    assert "made-up sample readings" in r.text
    assert "<svg" in r.text and 'role="img"' in r.text


def test_own_cycle_and_reading(client):
    start = date.today() - timedelta(days=20)
    client.post("/cycle", data={"start_day": start.isoformat(), "start_reading": "1000", "late_max": "3"})
    r = client.post("/readings", data={"day": date.today().isoformat(), "value": "1100"}, follow_redirects=True)
    assert "100 units" in r.text
    assert "5.0 a day" in r.text
    assert "On track to stay at or under 500" in r.text


def test_backwards_reading_is_refused(client):
    start = date.today() - timedelta(days=10)
    client.post("/cycle", data={"start_day": start.isoformat(), "start_reading": "1000"})
    r = client.post("/readings", data={"day": date.today().isoformat(), "value": "900"}, follow_redirects=True)
    assert "lower than an earlier reading" in r.text


def test_future_bill_date_refused(client):
    r = client.post("/cycle", data={"start_day": (date.today() + timedelta(days=1)).isoformat(), "start_reading": "5"},
                    follow_redirects=True)
    assert "cannot be in the future" in r.text


def test_delete_and_reset(client):
    client.post("/sample")
    r = client.post("/readings/1/delete", follow_redirects=True)
    assert r.status_code == 200
    r = client.post("/reset", follow_redirects=True)
    assert "Start with your last bill" in r.text


def test_every_string_has_both_languages():
    from ainooru.i18n import LANGS, S

    for key, texts in S.items():
        for lang in LANGS:
            assert texts.get(lang), f"{key} missing {lang}"


def test_tamil_switch(client):
    client.post("/sample")
    r = client.get("/lang/ta", follow_redirects=True)
    assert 'lang="ta"' in r.text
    assert "யூனிட்டைத் தாண்ட" in r.text
    assert "நாளொன்றுக்கு" in r.text
    r = client.get("/lang/en", follow_redirects=True)
    assert "chance of crossing" in r.text


def test_error_message_in_tamil(client):
    client.get("/lang/ta")
    start = date.today() - timedelta(days=10)
    client.post("/cycle", data={"start_day": start.isoformat(), "start_reading": "1000"})
    r = client.post("/readings", data={"day": date.today().isoformat(), "value": "900"}, follow_redirects=True)
    assert "முந்தைய அளவீடான 1000" in r.text


def test_unknown_error_key_is_ignored(client):
    r = client.get("/?error=title")
    assert 'role="alert"' not in r.text


def test_appliance_chips_and_compact_chart(client):
    r = client.post("/sample", follow_redirects=True)
    assert "1.5 ton AC" in r.text and "1 HP water pump" in r.text
    assert "chart-compact" in r.text and "chart-wide" in r.text


def test_hosted_households_are_per_browser_and_in_memory(tmp_path, monkeypatch):
    monkeypatch.setenv("AINOORU_DB", str(tmp_path / "t.sqlite3"))
    from ainooru import app as app_module, store
    from ainooru.app import app

    monkeypatch.setattr(store, "HOSTED", True)
    monkeypatch.setitem(app_module.templates.env.globals, "hosted", True)
    a = TestClient(app, base_url="https://testserver")
    b = TestClient(app, base_url="https://testserver")
    assert "public demo" in a.get("/").text
    r = a.post("/sample", follow_redirects=True)
    assert "chance of crossing 500 units" in r.text
    assert "chance of crossing 500 units" not in b.get("/").text
    assert "chance of crossing 500 units" in a.get("/").text
    assert not (tmp_path / "t.sqlite3").exists()
    a.post("/reset")
    assert "chance of crossing 500 units" not in a.get("/").text
