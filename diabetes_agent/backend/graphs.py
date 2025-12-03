import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import DISCLAIMER_TEXT
from backend.rag.safety import (
    is_emergency_like,
    emergency_response,
    should_block_medication_change,
    med_change_response,
)
from backend.memory.store import (
    upsert_user_profile,
    append_history,
    get_recent_history,
)


@dataclass
class GraphState:
    user_id: str
    message: str
    profile: Dict[str, Any] = field(default_factory=dict)
    image_path: Optional[str] = None
    image_caption: Optional[str] = None
    intent: Optional[str] = None  # "admin_rag" | "general_health"
    answer: Optional[str] = None
    route_reason: Optional[str] = None


def classify_intent(message: str) -> str:
    """
    Simple router for now.
    If question looks diabetes-specific or about your model, use admin RAG.
    Else, general health LLM.
    """
    m = message.lower()

    diabetes_keywords = [
        "diabetes",
        "blood sugar",
        "glucose",
        "hba1c",
        "insulin",
        "metformin",
        "neuropathy",
        "retinopathy",
        "diabetic",
        "type 2",
        "type ii",
        "type 1",
        "type i",
        "risk score",
        "prediction",
        "bmi",
    ]

    if any(k in m for k in diabetes_keywords):
        return "admin_rag"

    # If user directly asks about your website prediction, also admin_rag
    if "your prediction" in m or "risk score" in m or "model result" in m:
        return "admin_rag"

    return "general_health"


def run_graph(
    state: GraphState,
    nodes_module,
) -> GraphState:
    """
    nodes_module is backend.nodes (we inject to avoid circular import).
    """

    # 1) Update / merge profile first
    if state.profile:
        upsert_user_profile(state.user_id, state.profile)

    # 2) Safety checks first
    if is_emergency_like(state.message):
        state.answer = emergency_response()
        state.route_reason = "emergency"
        append_history(state.user_id, state.message, state.answer)
        return state

    if should_block_medication_change(state.message):
        state.answer = med_change_response()
        state.route_reason = "med_change_block"
        append_history(state.user_id, state.message, state.answer)
        return state

    # 3) If image provided, analyze & enrich message
    if state.image_path:
        caption = nodes_module.handle_image_node(state.image_path)
        state.image_caption = caption
        if caption:
            state.message = (
                state.message
                + f"\n\n[Image description from the user image: {caption}]"
            )

    # 4) Load recent memory (history) to provide continuity
    recent_hist = get_recent_history(state.user_id, limit=5)

    # 5) Intent classification
    state.intent = classify_intent(state.message)

    # 6) Dispatch
    if state.intent == "admin_rag":
        state.answer = nodes_module.admin_rag_node(
            message=state.message,
            user_profile=state.profile,
            history=recent_hist,
        )
        state.route_reason = "admin_rag"
    else:
        state.answer = nodes_module.general_health_node(
            message=state.message,
            user_profile=state.profile,
            history=recent_hist,
        )
        state.route_reason = "general_health"

    # 7) Always attach disclaimer if not already there
    if state.answer and DISCLAIMER_TEXT.strip() not in state.answer:
        state.answer += DISCLAIMER_TEXT

    # 8) Save in memory
    append_history(state.user_id, state.message, state.answer)

    return state
