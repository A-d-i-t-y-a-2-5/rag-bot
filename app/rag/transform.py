import re

from sentence_transformers import SentenceTransformer

def clean(text: str) -> str:
    t = text.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\. ,", "", t)
    t = t.replace("..", ".")
    t = t.replace(". .", ".")
    cleaned_text = t.replace("\n", " ").strip()
    return cleaned_text


def embed(text: str, model: SentenceTransformer) -> list[float]:
    return model.encode(text).tolist()
