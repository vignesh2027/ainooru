import io

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from ainooru import meter_photo


def png_bytes(size=(2400, 1800)):
    out = io.BytesIO()
    Image.new("RGB", size, (150, 170, 150)).save(out, format="PNG")
    return out.getvalue()


@pytest.mark.parametrize("content, expected", [
    ('{"kwh": "018529"}', 18529),
    ('<think>looking</think> {"kwh": 18529}', 18529),
    ('Sure: {"kwh": "18,529"}', 18529),
    ('{"kwh": null}', None),
    ("no idea", None),
    ('{"kwh": "123456789"}', None),
])
def test_parse(content, expected):
    assert meter_photo.parse(content) == expected


def test_prepare_shrinks_large_photos():
    jpeg = meter_photo.prepare(png_bytes())
    img = Image.open(io.BytesIO(jpeg))
    assert max(img.size) == meter_photo.MAX_SIDE and img.format == "JPEG"


def fake_client(content):
    def handler(request):
        assert request.headers["authorization"].startswith("Bearer ")
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_read_meter_with_mocked_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    assert meter_photo.read_meter(png_bytes((300, 200)), client=fake_client('{"kwh": "018529"}')) == 18529


def test_read_meter_without_key_returns_none(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert meter_photo.read_meter(png_bytes((300, 200))) is None


def test_photo_route_prefills_but_does_not_save(tmp_path, monkeypatch):
    monkeypatch.setenv("AINOORU_DB", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(meter_photo, "read_meter", lambda data: 18600)
    from ainooru import store
    from ainooru.app import app

    c = TestClient(app)
    c.post("/sample")
    before = len(store.readings())
    r = c.post("/photo", files={"photo": ("m.png", png_bytes((300, 200)), "image/png")}, follow_redirects=True)
    assert 'value="18600"' in r.text and "Read from your photo: 18600" in r.text
    assert len(store.readings()) == before


def test_photo_route_failure_asks_to_type(tmp_path, monkeypatch):
    monkeypatch.setenv("AINOORU_DB", str(tmp_path / "t.sqlite3"))
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(meter_photo, "read_meter", lambda data: None)
    from ainooru.app import app

    c = TestClient(app)
    c.post("/sample")
    r = c.post("/photo", files={"photo": ("m.png", b"not an image", "image/png")}, follow_redirects=True)
    assert "type the reading instead" in r.text


def test_photo_form_hidden_without_key(tmp_path, monkeypatch):
    monkeypatch.setenv("AINOORU_DB", str(tmp_path / "t.sqlite3"))
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    from ainooru.app import app

    c = TestClient(app)
    r = c.post("/sample", follow_redirects=True)
    assert 'action="/photo"' not in r.text
    assert 'action="/readings"' in r.text


def test_read_meter_retries_when_the_model_is_over_capacity(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(meter_photo, "BACKOFF", 0)
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) < 3:
            return httpx.Response(503, json={"error": {"message": "over capacity"}})
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"kwh": "018534"}'}}]})

    assert meter_photo.read_meter(png_bytes(), httpx.Client(transport=httpx.MockTransport(handler))) == 18534
    assert len(calls) == 3


def test_read_meter_gives_up_after_retries(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(meter_photo, "BACKOFF", 0)
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(503, json={})))
    assert meter_photo.read_meter(png_bytes(), client) is None
