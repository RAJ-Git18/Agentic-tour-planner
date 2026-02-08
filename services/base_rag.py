from abc import ABC, abstractmethod
from typing import Any
from langchain_pinecone import PineconeVectorStore
from utils.logger import logger
from services.embedding_service import EmbeddingService
from services.redis_service import RedisService


class BaseRagService(ABC):
    def __init__(
        self,
        pc_index: Any,
        llm,
        embedding_service: EmbeddingService,
        redis_service: RedisService,
        ranking_service=None,
    ):
        self.pc_index = pc_index
        self.llm = llm
        self.embedding_service = embedding_service
        self.ranking_service = ranking_service
        self.redis_service = redis_service
        self.vector_store = PineconeVectorStore(
            index=self.pc_index,
            embedding=self.embedding_service.get_embedding_async,
        )

    async def similarity_search(self, query: str, k: int = 3, filter: dict = None):
        """Common similarity search logic."""
        # Check Cache
        embedding_vector = await self.redis_service.get_emb_cache(query)

        if embedding_vector:
            logger.info("Embedding CACHE HIT")
        else:
            logger.info("Embedding CACHE MISS -> Generating")
            embedding_vector = await self.embedding_service.get_embedding_async(query)
            # Store in Cache
            await self.redis_service.set_emb_cache(query, embedding_vector)

        return self.vector_store.similarity_search_by_vector_with_score(
            embedding=embedding_vector, k=k, filter=filter
        )

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        This is an abstract method.
        Any class that inherits from BaseRagService MUST implement this method.
        If they don't, Python will raise an error when you try to use them.
        """
        pass
