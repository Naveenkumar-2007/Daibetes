import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from backend.config import (
    GROQ_API_KEY,
    GROQ_API_URL,
    GROQ_MODEL,
    SYSTEM_PROMPT_ADMIN_RAG,
    SYSTEM_PROMPT_GENERAL_HEALTH,
    DISCLAIMER_TEXT,
)
from backend.rag.vectorstore import similarity_search_admin
from backend.vision.image_caption import caption_image
from backend.rag.safety import (
    is_emergency_like,
    emergency_response,
    should_block_medication_change,
    med_change_response,
)


def _call_groq(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 700,
    }
    resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def handle_image_node(image_path: str) -> Optional[str]:
    """
    Node: analyze user image -> return caption text.
    """
    caption = caption_image(image_path)
    if not caption:
        return None
    return caption


def admin_rag_node(
    message: str,
    user_profile: Dict[str, Any],
    history: List[Dict[str, str]],
) -> str:
    """
    Node: strictly admin-trained RAG, only diabetes KB docs.
    """

    # Safety double-check
    if is_emergency_like(message):
        return emergency_response()
    if should_block_medication_change(message):
        return med_change_response()

    docs = similarity_search_admin(message, k=4)
    if not docs:
        base = (
            "I don't have enough admin-approved diabetes content to answer that clearly."
        )
        return base + DISCLAIMER_TEXT

    context_parts = []
    for i, (text, meta) in enumerate(docs):
        title = meta.get("title", f"Doc {i+1}")
        source = meta.get("source", "admin")
        context_parts.append(
            f"[{i+1}] Title: {title} | Source: {source}\n{text.strip()}"
        )
    context_text = "\n\n".join(context_parts)

    profile_str = ""
    if user_profile:
        profile_str = (
            "User profile (may be partial): "
            + json.dumps(user_profile, ensure_ascii=False)
        )

    hist_str = ""
    if history:
        hist_lines = []
        for h in history[-5:]:
            hist_lines.append(f"User: {h['user']}\nAssistant: {h['bot']}")
        hist_str = "\n\nRecent conversation:\n" + "\n\n".join(hist_lines)

    user_prompt = (
        "Use ONLY the admin-approved diabetes context below to answer the user's question.\n"
        "If the answer is not clearly present, say you don't know or suggest talking to a doctor.\n\n"
        f"{profile_str}\n"
        f"{hist_str}\n\n"
        "=== ADMIN DIABETES CONTEXT START ===\n"
        f"{context_text}\n"
        "=== CONTEXT END ===\n\n"
        f"User question: {message}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_ADMIN_RAG},
        {"role": "user", "content": user_prompt},
    ]

    try:
        answer = _call_groq(messages, temperature=0.15)
    except Exception as e:
        print("Groq admin_rag error:", e)
        answer = (
            "I'm having trouble accessing the admin knowledge base right now. "
            "Please try again later."
        )

    return answer


def general_health_node(
    message: str,
    user_profile: Dict[str, Any],
    history: List[Dict[str, str]],
) -> str:
    """
    Node: general health LLM response (no RAG), safety-limited.
    """

    if is_emergency_like(message):
        return emergency_response()
    if should_block_medication_change(message):
        return med_change_response()

    profile_str = ""
    if user_profile:
        profile_str = (
            "User profile (may be partial): "
            + json.dumps(user_profile, ensure_ascii=False)
        )

    hist_str = ""
    if history:
        hist_lines = []
        for h in history[-5:]:
            hist_lines.append(f"User: {h['user']}\nAssistant: {h['bot']}")
        hist_str = "\n\nRecent conversation:\n" + "\n\n".join(hist_lines)

    user_prompt = (
        "Provide safe, general health information. Do NOT give diagnosis, treatment, "
        "or medication changes.\n\n"
        f"{profile_str}\n"
        f"{hist_str}\n\n"
        f"User question: {message}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_GENERAL_HEALTH},
        {"role": "user", "content": user_prompt},
    ]

    try:
        answer = _call_groq(messages, temperature=0.3)
    except Exception as e:
        print("Groq general_health error:", e)
        answer = (
            "I'm having trouble answering right now. Please try again later."
            + DISCLAIMER_TEXT
        )

    return answer
