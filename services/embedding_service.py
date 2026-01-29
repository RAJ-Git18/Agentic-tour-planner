from concurrent.futures import ThreadPoolExecutor
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:
    def __init__(self, model):
        self.model = model
        self.executor = ThreadPoolExecutor(max_workers=4)

    def get_embedding(self, text: str):
        return self.model.embed_query(text)

    async def get_embedding_async(self, text: str):
        """Asynchronous wrapper that runs in the thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.get_embedding, text)