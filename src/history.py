"""CSV persistence for daily subscriber observations."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Observation:
    observation_date: date
    subscribers: int


def load_history(path: str | Path) -> list[Observation]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    observations: dict[date, Observation] = {}
    with file_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            try:
                observed_date = date.fromisoformat(row["date"])
                subscribers = int(row["subscribers"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid history row: {row}") from error
            if subscribers < 0:
                raise ValueError(f"Subscriber count cannot be negative: {row}")
            observations[observed_date] = Observation(observed_date, subscribers)
    return sorted(observations.values(), key=lambda item: item.observation_date)


def upsert_observation(path: str | Path, observation: Observation) -> None:
    """Atomically upsert one valid observation, preserving one row per date."""
    if observation.subscribers < 0:
        raise ValueError("Subscriber count cannot be negative")
    observations = {item.observation_date: item for item in load_history(path)}
    observations[observation.observation_date] = observation
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date", "subscribers"])
        for item in sorted(observations.values(), key=lambda value: value.observation_date):
            writer.writerow([item.observation_date.isoformat(), item.subscribers])
    temporary.replace(destination)