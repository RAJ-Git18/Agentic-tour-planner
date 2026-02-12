from abc import ABC, abstractmethod
from typing import Any
from langchain_pinecone import PineconeVectorStore
from utils.logger import logger
from services.embedding_service import EmbeddingService
from services.redis_service import RedisService
from pinecone_text.sparse import SpladeEncoder


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

    async def hybrid_search(self, query: str, k: int = 3, filter: dict = None):
        """Common similarity search logic."""
        # Check Cache
        cached_data = await self.redis_service.get_emb_cache(query)

        if cached_data:
            logger.info("Embedding CACHE HIT")
            dense_embedding = cached_data.get("dense")
            sparse_embedding = cached_data.get("sparse")
        else:
            logger.info("Embedding CACHE MISS -> Generating")
            dense_embedding = await self.embedding_service.get_embedding_async(query)
            sparse_embedding = await self.embedding_service.get_sparse_embedding_async(
                query
            )
            embedding_vector = {
                "dense": dense_embedding,
                "sparse": sparse_embedding,
            }
            # Store in Cache
            await self.redis_service.set_emb_cache(query, embedding_vector)

        result = self.pc_index.query(
            top_k=k,
            vector=dense_embedding,
            sparse_vector=sparse_embedding,
            include_values=False,
            include_metadata=True,
        )
        logger.info(f"Hybrid Search Result completed sucessfully!!")

        return result

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        This is an abstract method.
        Any class that inherits from BaseRagService MUST implement this method.
        If they don't, Python will raise an error when you try to use them.
        """
        pass
