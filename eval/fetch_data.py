"""Download the UCI 'Individual household electric power consumption' dataset.

Hebrail, G. and Berard, A. (2006). UCI Machine Learning Repository.
https://doi.org/10.24432/C58K54 (licence: CC BY 4.0)
"""

import io
import zipfile
from pathlib import Path

import httpx

URL = "https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip"
OUT = Path(__file__).resolve().parent / "data"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    target = OUT / "household_power_consumption.txt"
    if target.exists():
        print(f"already present: {target}")
        return
    print(f"downloading {URL}")
    r = httpx.get(URL, follow_redirects=True, timeout=300)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extract("household_power_consumption.txt", OUT)
    print(f"saved {target} ({target.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
