"""Simple JSON save/load helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import Player

SAVE_DIR = Path.home() / ".hacker_sandbox"
SAVE_FILE = SAVE_DIR / "save_slot.json"


def save_state(player: Player, stage: str, market_index: int) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "player": player.to_dict(),
        "stage": stage,
        "market_index": market_index,
    }
    SAVE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def load_state() -> Optional[dict]:
    if not SAVE_FILE.exists():
        return None
    return json.loads(SAVE_FILE.read_text())


def has_save() -> bool:
    return SAVE_FILE.exists()
