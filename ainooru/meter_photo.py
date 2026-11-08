"""Optional: read the kWh number from a photo of the meter.

It sends the photo to an open vision model hosted on Groq's free tier. It is
never required: if no key is set, or the model cannot read the photo, the user
types the number as usual. The result is only ever a suggestion that fills the
reading box; the user checks it against the meter and presses Add.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
import time
from pathlib import Path

import httpx
from PIL import Image, ImageOps

ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.environ.get("AINOORU_VISION_MODEL", "qwen/qwen3.8-27b")
MAX_SIDE = 1280
RETRIES = 3
BACKOFF = 1.0  # seconds, doubled each retry
PROMPT = (
    "This is a photo of a household electricity meter in Tamil Nadu. Find the cumulative energy reading in kWh "
    "on its display. Ignore serial numbers, ratings such as 5-30A or 240V, and the imp/kWh constant. "
    'Reply with JSON only: {"kwh": "<digits only>"} or {"kwh": null} if no reading is clearly visible.'
)


def _load_env_file() -> None:
    env = Path(__file__).resolve().parent.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_file()


def available() -> bool:
    return bool(os.environ.get("GROQ_API_KEY"))


def prepare(image_bytes: bytes) -> bytes:
    """Fix orientation, shrink to MAX_SIDE and re-encode as JPEG."""
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=88)
    return out.getvalue()


def parse(content: str) -> int | None:
    content = re.sub(r"(?s)<think>.*?</think>", "", content)
    m = re.search(r"\{.*?\}", content, re.S)
    if not m:
        return None
    try:
        value = json.loads(m.group(0)).get("kwh")
    except (ValueError, AttributeError):
        return None
    if value is None:
        return None
    digits = re.sub(r"[^0-9]", "", str(value))
    if not digits or len(digits) > 7:
        return None
    return int(digits)


def read_meter(image_bytes: bytes, client: httpx.Client | None = None) -> int | None:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        jpeg = prepare(image_bytes)
    except Exception:
        return None
    body = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": 300,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()}},
        ]}],
    }
    own = client is None
    client = client or httpx.Client(timeout=20)
    try:
        # Groq's free tier sometimes answers 503 "over capacity" or 429; back off briefly and try again.
        for attempt in range(RETRIES + 1):
            r = client.post(ENDPOINT, json=body, headers={"Authorization": f"Bearer {key}"})
            if r.status_code in (429, 500, 502, 503) and attempt < RETRIES:
                time.sleep(BACKOFF * 2 ** attempt)
                continue
            r.raise_for_status()
            return parse(r.json()["choices"][0]["message"]["content"])
        return None
    except Exception:
        return None
    finally:
        if own:
            client.close()
