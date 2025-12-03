from typing import List, Dict, Any, Tuple
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import chromadb
from chromadb.config import Settings

from backend.rag.embedder import embed_texts, embed_query
from backend.config import CHROMA_ADMIN_DIR, ADMIN_COLLECTION_NAME


def get_admin_client():
    client = chromadb.Client(
        Settings(
            persist_directory=str(CHROMA_ADMIN_DIR),
            anonymized_telemetry=False,
        )
    )
    return client


def get_admin_collection():
    client = get_admin_client()
    collection = client.get_or_create_collection(name=ADMIN_COLLECTION_NAME)
    return collection


def add_admin_documents(
    texts: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str],
):
    collection = get_admin_collection()
    embeddings = embed_texts(texts)
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings,
    )


def similarity_search_admin(
    query: str,
    k: int = 4,
) -> List[Tuple[str, Dict[str, Any]]]:
    collection = get_admin_collection()
    q_emb = embed_query(query)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return list(zip(docs, metas))
