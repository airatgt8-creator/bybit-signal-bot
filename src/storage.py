from __future__ import annotations

import json
from pathlib import Path


class LocalState:
    def __init__(self, path: str = "state.json"):
        self.path = Path(path)
        self.state = {"sent": [], "positions": {}}
        self.load()

    def load(self):
        if self.path.exists():
            self.state = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self):
        self.path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def already_sent(self, key: str) -> bool:
        return key in self.state["sent"]

    def mark_sent(self, key: str):
        if key not in self.state["sent"]:
            self.state["sent"].append(key)
            self.save()

    def position_count(self) -> int:
        return len(self.state.get("positions", {}))

    def add_position(self, symbol: str, entry: float):
        self.state.setdefault("positions", {})[symbol] = {"entry": entry}
        self.save()
