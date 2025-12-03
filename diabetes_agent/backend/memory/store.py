import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config import MEMORY_FILE_PATH


def _ensure_file():
    path = Path(MEMORY_FILE_PATH)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")


def _load_all() -> Dict[str, Any]:
    _ensure_file()
    with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    return data


def _save_all(data: Dict[str, Any]):
    with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_user_memory(user_id: str) -> Dict[str, Any]:
    all_mem = _load_all()
    return all_mem.get(user_id, {"profile": {}, "history": []})


def upsert_user_profile(user_id: str, profile: Dict[str, Any]):
    all_mem = _load_all()
    user_mem = all_mem.get(user_id, {"profile": {}, "history": []})
    user_mem["profile"].update(profile or {})
    all_mem[user_id] = user_mem
    _save_all(all_mem)


def append_history(
    user_id: str,
    user_message: str,
    bot_answer: str,
):
    all_mem = _load_all()
    user_mem = all_mem.get(user_id, {"profile": {}, "history": []})
    user_mem.setdefault("history", [])
    user_mem["history"].append(
        {"user": user_message, "bot": bot_answer}
    )
    # keep last 30 turns only
    user_mem["history"] = user_mem["history"][-30:]
    all_mem[user_id] = user_mem
    _save_all(all_mem)


def get_recent_history(user_id: str, limit: int = 5) -> List[Dict[str, str]]:
    mem = get_user_memory(user_id)
    hist = mem.get("history", [])
    return hist[-limit:]
