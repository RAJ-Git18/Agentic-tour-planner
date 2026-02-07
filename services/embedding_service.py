from concurrent.futures import ThreadPoolExecutor
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:
    """
    This service does the embedding in thread pool to avoid the blocking of the event loop.
    """

    _executor = ThreadPoolExecutor(max_workers=4)

    def __init__(self, model):
        self.model = model

    def get_embedding(self, text: str):
        return self.model.embed_query(text)

    async def get_embedding_async(self, text: str):
        """Asynchronous wrapper that runs in the thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.get_embedding, text)