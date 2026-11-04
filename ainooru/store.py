"""SQLite storage for one household's billing cycle and meter readings."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS cycle (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    start_day TEXT NOT NULL,
    start_reading REAL NOT NULL,
    expected_end TEXT NOT NULL,
    late_max INTEGER NOT NULL DEFAULT 3,
    sample INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS reading (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,
    value REAL NOT NULL
);
"""


@dataclass
class Cycle:
    start_day: date
    start_reading: float
    expected_end: date
    late_max: int
    sample: bool


@dataclass
class StoredReading:
    id: int
    day: date
    value: float


def db_path() -> Path:
    return Path(os.environ.get("AINOORU_DB", Path(__file__).resolve().parent.parent / "data" / "ainooru.sqlite3"))


@contextmanager
def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        con.executescript(SCHEMA)
        yield con
        con.commit()
    finally:
        con.close()


def get_cycle() -> Cycle | None:
    with connect() as con:
        row = con.execute("SELECT start_day, start_reading, expected_end, late_max, sample FROM cycle WHERE id = 1").fetchone()
    if not row:
        return None
    return Cycle(date.fromisoformat(row[0]), row[1], date.fromisoformat(row[2]), row[3], bool(row[4]))


def set_cycle(c: Cycle, keep_readings: bool = False) -> None:
    with connect() as con:
        con.execute("DELETE FROM cycle")
        if not keep_readings:
            con.execute("DELETE FROM reading")
        con.execute(
            "INSERT INTO cycle (id, start_day, start_reading, expected_end, late_max, sample) VALUES (1, ?, ?, ?, ?, ?)",
            (c.start_day.isoformat(), c.start_reading, c.expected_end.isoformat(), c.late_max, int(c.sample)),
        )


def readings() -> list[StoredReading]:
    with connect() as con:
        rows = con.execute("SELECT id, day, value FROM reading ORDER BY day, id").fetchall()
    return [StoredReading(r[0], date.fromisoformat(r[1]), r[2]) for r in rows]


def add_reading(day: date, value: float) -> None:
    with connect() as con:
        con.execute("INSERT INTO reading (day, value) VALUES (?, ?)", (day.isoformat(), value))


def delete_reading(reading_id: int) -> None:
    with connect() as con:
        con.execute("DELETE FROM reading WHERE id = ?", (reading_id,))


def reset() -> None:
    with connect() as con:
        con.execute("DELETE FROM cycle")
        con.execute("DELETE FROM reading")
