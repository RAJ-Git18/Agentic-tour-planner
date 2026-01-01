import json
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from utils.logger import logger


class IngestDocumentService:
    def __init__(self, pc_index: str, emb_model):
        self.pc_index = pc_index
        self.emb_model = emb_model

    def ingest_json_file(self, file_path: str):
        logger.info(f"Ingesting JSON from {file_path}")
        with open(file_path, "r") as f:
            data = json.load(f)

        documents = []
        for item in data:
            # Flattening the dictionary into a string for embedding,
            # while keeping metadata for filtering
            content = " ".join([f"{k}: {v}" for k, v in item.items()])
            doc = Document(page_content=content, metadata=item)
            documents.append(doc)

        vector_store = PineconeVectorStore.from_documents(
            documents, self.emb_model, index_name=self.pc_index
        )
        return len(documents)

    def ingest_txt_file(self, file_path: str):
        with open(file_path, "r") as f:
            content = f.read()

        # Simple policy doc ingestion
        doc = Document(
            page_content=content,
            metadata={"filename": "company_info.txt", "type": "policy"},
        )

        vector_store = PineconeVectorStore.from_documents(
            [doc], self.emb_model, index_name=self.pc_index
        )
        return 1
