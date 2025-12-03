import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Groq LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY not set in .env")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"  # or llama3-70b-8192 if allowed

# Chroma paths
CHROMA_ADMIN_DIR = BASE_DIR / "data" / "chroma_admin"

# Admin KB collection name
ADMIN_COLLECTION_NAME = "diabetes_admin_kb"

# RAG config
TOP_K_ADMIN = 4

# Memory file
MEMORY_FILE_PATH = BASE_DIR / "memory_store.json"

# Prompts

SYSTEM_PROMPT_ADMIN_RAG = """
You are a diabetes information assistant that answers strictly from trusted admin-approved diabetes
guidelines and education content provided in the context.

RULES:
- You are NOT a doctor.
- You do NOT give diagnosis or treatment.
- Do NOT prescribe, start, stop, or change any medication or insulin dose.
- Do NOT give exact drug names or doses as instructions.
- You provide general education only, and always suggest speaking with a doctor.
- If the context does not contain enough information, say you don't know.
- If something sounds like an emergency (severe chest pain, trouble breathing, confusion, etc.),
  instruct the user to seek emergency care immediately.
- Prefer short, clear explanations that a patient can understand.
"""

SYSTEM_PROMPT_GENERAL_HEALTH = """
You are a safe, general health information assistant.

RULES:
- You are NOT a doctor.
- Do NOT give diagnosis or treatment.
- Do NOT prescribe, start, stop, or change any medication or insulin dose.
- Do NOT give specific treatment plans.
- Provide only general health education and encourage users to consult a doctor.
- If the user describes emergency-like symptoms, tell them to seek urgent/emergency care immediately.
- If you are not sure about something, say so.
"""

DISCLAIMER_TEXT = (
    "\n\n⚠️ Disclaimer: I am an AI assistant, not a doctor. This is general information, "
    "not medical advice. Always consult your doctor before making any medical decisions."
)
