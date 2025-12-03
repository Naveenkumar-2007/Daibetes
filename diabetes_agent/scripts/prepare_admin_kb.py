"""
Prepare Admin Knowledge Base

Put your cleaned diabetes .txt files in backend/data/raw_admin/
Then run: python scripts/prepare_admin_kb.py
"""

import os
import uuid
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.rag.vectorstore import add_admin_documents

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "backend" / "data" / "raw_admin"


def simple_chunk(text: str, size: int = 800, overlap: int = 200):
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= end:
            break
    return chunks


def main():
    if not RAW_DIR.exists():
        print(f"❌ Directory not found: {RAW_DIR}")
        print("Please create backend/data/raw_admin/ and add your .txt files")
        return

    texts = []
    metadatas = []
    ids = []

    txt_files = list(RAW_DIR.glob("*.txt"))
    if not txt_files:
        print(f"⚠️ No .txt files found in {RAW_DIR}")
        print("Please add your diabetes knowledge .txt files there")
        return

    for fname in txt_files:
        print(f"Processing: {fname.name}")
        with open(fname, "r", encoding="utf-8") as f:
            raw = f.read()
        chunks = simple_chunk(raw)
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append(
                {
                    "source": str(fname),
                    "title": fname.name,
                    "chunk_index": i,
                }
            )
            ids.append(str(uuid.uuid4()))

    print(f"\n✅ Adding {len(texts)} admin chunks to Chroma from {len(txt_files)} files...")
    add_admin_documents(texts, metadatas, ids)
    print("✅ Done! Knowledge base is ready.")


if __name__ == "__main__":
    main()
