from abc import ABC, abstractmethod
from typing import Any
from langchain_pinecone import PineconeVectorStore
from utils.logger import logger


class BaseRagService(ABC):
    def __init__(self, pc_index: Any, llm, emb_model, cross_encoder=None):
        self.pc_index = pc_index
        self.llm = llm
        self.emb_model = emb_model
        self.cross_encoder = cross_encoder
        self.vector_store = PineconeVectorStore(
            index=self.pc_index, embedding=self.emb_model
        )

    def similarity_search(self, query: str, k: int = 3, filter: dict = None):
        """Common similarity search logic."""
        return self.vector_store.similarity_search_by_vector_with_score(
            embedding=self.emb_model.embed_query(query), k=k, filter=filter
        )

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        This is an abstract method.
        Any class that inherits from BaseRagService MUST implement this method.
        If they don't, Python will raise an error when you try to use them.
        """
        pass
