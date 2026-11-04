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
