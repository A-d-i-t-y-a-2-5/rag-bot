import logging
import os

from sentence_transformers import SentenceTransformer

from app.rag.database import VectorDatabase
from app.rag.extractor import pdf_text_extractor
from app.rag.transform import clean, embed
from app.utils.io import load_file

logger = logging.getLogger(__name__)

class RAGService(VectorDatabase):
    def __init__(self):
        super().__init__()

    async def ingest_document(self, filepath: str, collection_name: str, model: SentenceTransformer) -> None:
        logger.info(f"Inserting {filepath} content into database")
        filename = os.path.basename(filepath)
        async for chunk in load_file(filepath):
            cleaned = clean(chunk)
            embedding_vector = embed(cleaned, model)
            await self.insert(collection_name, embedding_vector, chunk, filename)