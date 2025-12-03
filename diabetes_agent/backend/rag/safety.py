import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config import DISCLAIMER_TEXT

EMERGENCY_KEYWORDS = [
    "severe chest pain",
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "trouble breathing",
    "fainting",
    "unconscious",
    "unconsciousness",
    "confused and sweating",
    "very low sugar",
    "seizure",
    "stroke",
]


def is_emergency_like(message: str) -> bool:
    m = message.lower()
    return any(k in m for k in EMERGENCY_KEYWORDS)


def emergency_response() -> str:
    return (
        "Your description may indicate a serious or emergency condition.\n\n"
        "🚨 Please go to the nearest hospital or call your local emergency number immediately. "
        "Do NOT rely on this chatbot for emergency care."
        + DISCLAIMER_TEXT
    )


def should_block_medication_change(message: str) -> bool:
    m = message.lower()
    patterns = [
        "should i stop",
        "can i stop",
        "can i reduce my dose",
        "increase my insulin",
        "reduce my insulin",
        "change my medicine",
        "change my medication",
        "skip my dose",
        "double my dose",
    ]
    return any(p in m for p in patterns)


def med_change_response() -> str:
    return (
        "I cannot tell you to start, stop, or change any medication or insulin dose.\n"
        "You must discuss this with your doctor or healthcare provider."
        + DISCLAIMER_TEXT
    )
