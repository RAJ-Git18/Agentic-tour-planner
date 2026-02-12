import time
from pinecone import ServerlessSpec, Pinecone
from config import settings
from utils.logger import logger


class PineconeService:
    def __init__(self):
        self.index_name = settings.PINECONE_INDEX
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        if not self.pc.has_index(self.index_name):
            logger.info("Creating index for pinecone vector")
            self.pc.create_index(
                name=self.index_name,
                dimension=settings.EMBEDDING_DIMENSION,
                metric="dotproduct",
                spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_REGION),
            )
        self.index = self.pc.Index(self.index_name)

    def get_index(self):
        # Optimistic: Return the index handle immediately (no API call)
        return self.pc.Index(self.index_name)

    def delete_index(self):
        """Delete and recreate the index with a fresh state."""
        logger.info("Deleting index for pinecone vector")
        self.pc.delete_index(self.index_name)

        # Wait a moment for deletion to propagate
        time.sleep(1)

        # Recreate the index
        self.pc.create_index(
            name=self.index_name,
            dimension=settings.EMBEDDING_DIMENSION,
            metric="dotproduct",
            spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_REGION),
        )
        logger.info("Index recreated successfully")


pc_service = PineconeService()
