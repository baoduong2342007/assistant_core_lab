"""Knowledge retrieval for university offices and academic handbook rules."""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError
from assistant_core.models import Rule


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        """Load office records from a CSV file."""
        if not path.is_file():
            raise DataError(f"office file not found: {path}")

        try:
            with path.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None or not {"name", "room", "hours"}.issubset(set(reader.fieldnames)):
                    raise DataError(f"Missing required CSV columns in {path}")
                rows = list(reader)
        except Exception as exc:
            if isinstance(exc, DataError):
                raise
            raise DataError(f"Error reading office CSV file: {exc}") from exc

        offices = {}
        for r in rows:
            name = r.get("name", "").strip()
            room = r.get("room", "").strip()
            hours = r.get("hours", "").strip()
            if not name or not room or not hours:
                raise DataError(f"Invalid office row: {r}")
            offices[name.lower()] = Office(name=name, room=room, hours=hours)

        return cls(offices)

    @property
    def names(self) -> set[str]:
        return set(self._offices.keys())

    def find(self, text: str) -> Office | None:
        """Find the first matching office whose name appears in text (case-insensitive)."""
        t = text.lower()
        return next((o for name, o in self._offices.items() if name in t), None)


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @property
    def rules(self) -> list[Rule]:
        """Return all rules currently loaded."""
        return list(self._rules)

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        """Load student handbook rules from a JSON file."""
        if not path.is_file():
            raise DataError(f"handbook file not found: {path}")

        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            raise DataError(f"Error reading handbook JSON file: {exc}") from exc

        if not isinstance(data, list):
            raise DataError(f"Handbook JSON must be a list, got {type(data).__name__}")

        rules: list[Rule] = []
        for item in data:
            if not isinstance(item, dict) or not {"id", "title", "text"}.issubset(item.keys()):
                raise DataError(f"Rule missing required fields (id, title, text): {item}")
            rules.append(Rule(id=str(item["id"]), title=str(item["title"]), text=str(item["text"])))

        return cls(rules)

    def search(self, query: str) -> Rule | None:
        """Search for the best-matching rule based on token overlap (token length > 3)."""
        tokens = query.lower().split()
        best: Rule | None = None
        best_score = 0

        for rule in self._rules:
            text_lower = rule.text.lower()
            score = sum(1 for w in tokens if len(w) > 3 and w in text_lower)
            if score > best_score:
                best_score = score
                best = rule

        if best_score >= 1:
            return best
        return None

    def get_by_id(self, rule_id: str) -> Rule | None:
        """Find a rule by exact rule ID (e.g. 'H26-5.3')."""
        target = rule_id.strip().lower()
        return next((r for r in self._rules if r.id.lower() == target), None)
