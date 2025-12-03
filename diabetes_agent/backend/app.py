from pathlib import Path
import shutil
import uuid
import sys
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.graphs import GraphState, run_graph
import backend.nodes as nodes_module

app = FastAPI(
    title="Diabetes Agentic RAG Chatbot",
    description="Admin-trained RAG + general health fallback + memory + image support",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_id: str
    message: str
    profile: Optional[Dict[str, Any]] = None  # e.g. {age, bmi, hba1c, risk_score}


class ChatResponse(BaseModel):
    answer: str
    route_reason: str
    intent: Optional[str]


@app.post("/chat", response_model=ChatResponse)
def chat_text(payload: ChatRequest):
    state = GraphState(
        user_id=payload.user_id,
        message=payload.message,
        profile=payload.profile or {},
    )
    final_state = run_graph(state, nodes_module=nodes_module)
    return ChatResponse(
        answer=final_state.answer or "",
        route_reason=final_state.route_reason or "",
        intent=final_state.intent,
    )


@app.post("/chat-with-image", response_model=ChatResponse)
async def chat_with_image(
    user_id: str = Form(...),
    message: str = Form(""),
    profile_json: str = Form("{}"),
    image: UploadFile = File(...),
):
    # Save uploaded image to temp folder
    tmp_dir = Path("tmp_images")
    tmp_dir.mkdir(exist_ok=True)
    img_id = str(uuid.uuid4())
    img_path = tmp_dir / f"{img_id}_{image.filename}"
    with img_path.open("wb") as f:
        shutil.copyfileobj(image.file, f)

    try:
        import json as _json
        profile = _json.loads(profile_json or "{}")
    except Exception:
        profile = {}

    state = GraphState(
        user_id=user_id,
        message=message or "Please analyze this image in the context of my diabetes.",
        profile=profile,
        image_path=str(img_path),
    )
    final_state = run_graph(state, nodes_module=nodes_module)

    # (optional) clean up images later with a cron, etc.

    return ChatResponse(
        answer=final_state.answer or "",
        route_reason=final_state.route_reason or "",
        intent=final_state.intent,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
