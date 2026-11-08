"""Public demo of Ainooru on Modal.

Deploy: modal deploy modal_app.py
URL:    https://applemacbook6sep2004--ainooru.us-east.modal.run

One small container (a quarter CPU, 512 MB) that scales to zero when idle, so the first
visit after a quiet spell takes a few seconds. AINOORU_HOSTED=1 gives every browser its own
household in memory (nothing on disk, wiped on restart). The optional meter-photo reader
needs GROQ_API_KEY: it is read from the local .env at deploy time and passed as a Modal
secret. Without it the photo option is hidden.
"""

import os
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent


def _groq_key() -> dict:
    key = os.environ.get("GROQ_API_KEY", "")
    env = HERE / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("GROQ_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return {"GROQ_API_KEY": key} if key else {}


image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("fastapi>=0.162.0", "jinja2>=3.1.6", "numpy>=2.5.4", "pillow>=13.0.0", "httpx>=0.28.1", "python-multipart>=0.0.33")
    .env({"AINOORU_HOSTED": "1", "AINOORU_DB": "/tmp/unused.sqlite3"})
    .add_local_dir(str(HERE / "ainooru"), "/root/ainooru", ignore=["**/__pycache__"])
)

app = modal.App("ainooru")


@app.function(image=image, cpu=0.25, memory=512, min_containers=0, max_containers=1, scaledown_window=900,
              secrets=[modal.Secret.from_dict(_groq_key())])
@modal.concurrent(max_inputs=50)
@modal.asgi_app(label="ainooru")
def web():
    import sys

    sys.path.insert(0, "/root")
    from ainooru.app import app as fastapi_app

    return fastapi_app
