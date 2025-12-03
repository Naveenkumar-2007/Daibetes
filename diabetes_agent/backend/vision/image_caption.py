from typing import Optional, Union
from pathlib import Path

from PIL import Image
from transformers import pipeline

# Lazy init global pipeline
_image_caption_pipeline = None


def _get_pipeline():
    global _image_caption_pipeline
    if _image_caption_pipeline is None:
        # Free HF model (works on CPU, slower)
        _image_caption_pipeline = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base"
        )
    return _image_caption_pipeline


def caption_image(image_path: Union[str, Path]) -> Optional[str]:
    try:
        pipe = _get_pipeline()
        img = Image.open(image_path).convert("RGB")
        result = pipe(img, max_new_tokens=50)
        if result and isinstance(result, list):
            return result[0].get("generated_text", "").strip()
        return None
    except Exception as e:
        print("Image caption error:", e)
        return None
