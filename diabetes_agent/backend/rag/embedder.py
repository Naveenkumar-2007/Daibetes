from typing import List
from sentence_transformers import SentenceTransformer

# Free HuggingFace embedding model
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=False)
    return [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]


def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]
