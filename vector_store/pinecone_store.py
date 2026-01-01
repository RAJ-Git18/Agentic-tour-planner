import os
from pinecone import Pinecone


class PineconeStore:
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name

    def get_index(self):
        if self.index_name not in [idx.name for idx in self.pc.list_indexes()]:
            # This is a simplified version; in reality, you might want to create it
            raise ValueError(f"Index {self.index_name} does not exist in Pinecone")
        return self.pc.Index(self.index_name)
