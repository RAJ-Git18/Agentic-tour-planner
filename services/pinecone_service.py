from pinecone import ServerlessSpec, Pinecone
from config import settings


class PineconeService:
    def __init__(self):
        self.index_name = settings.PINECONE_INDEX
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        if not self.pc.has_index(self.index_name):
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
        self.pc.delete_index(self.index_name)


pc_service = PineconeService()
