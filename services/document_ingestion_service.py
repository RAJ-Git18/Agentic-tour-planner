import json
import re
import uuid
from typing import List
from langchain_core.documents import Document
from pinecone_text.sparse import SpladeEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.logger import logger

sparse_encoder = SpladeEncoder()


class DocumentProcessor:
    """Handles parsing of different file types into standard Document objects."""

    @staticmethod
    def process_json(content_bytes: bytes, filename: str) -> List[Document]:
        try:
            data = json.loads(content_bytes)
            # Ensure data is a list; if it's a single dict, wrap it
            if isinstance(data, dict):
                data = [data]

            documents = []
            for i, item in enumerate(data):
                # Flatten dict to string
                content_str = " ".join([f"{k}: {v}" for k, v in item.items()])
                doc = Document(
                    page_content=content_str,
                    metadata={
                        **item,
                        "filename": filename,
                        "chunk_index": i,
                        "type": filename.replace(".json", ""),
                    },
                )
                documents.append(doc)
            return documents
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError("Invalid JSON file")

    @staticmethod
    def process_txt(content_bytes: bytes, filename: str) -> List[Document]:
        text = content_bytes.decode("utf-8")
        # Clean whitespace
        clean_text = re.sub(r"\s+", " ", text).strip()

        # Chunk text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_text(clean_text)

        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "filename": filename,
                    "type": "policy",
                    "chunk_index": i,
                    "content": chunk,
                },
            )
            documents.append(doc)
        return documents


class IngestDocumentService:
    def __init__(self, pc_index: str, emb_model, pc_service):
        self.pc_index = pc_index
        self.emb_model = emb_model
        self.pc_service = pc_service
        self.processor = DocumentProcessor()

    async def _process_and_upsert(self, documents: List[Document], filename: str):
        if not documents:
            logger.warning(f"No documents parsed from {filename}")
            return 0

        texts = [d.page_content for d in documents]
        dense_vectors = self.emb_model.embed_documents(texts)
        sparse_vectors = sparse_encoder.encode_documents(texts)

        data_to_upsert = []
        for doc, dv, sv in zip(documents, dense_vectors, sparse_vectors):
            # Deterministic ID: filename_chunkIndex
            doc_id = f"{doc.metadata['filename']}_{doc.metadata['chunk_index']}"

            data_to_upsert.append(
                {
                    "id": doc_id,
                    "values": dv,
                    "sparse_values": sv,
                    "metadata": doc.metadata,
                }
            )

        if not data_to_upsert:
            return 0

        try:
            index_handle = self.pc_service.get_index()
            index_handle.upsert(vectors=data_to_upsert)
            logger.info(
                f"Successfully upserted {len(data_to_upsert)} vectors for {filename}"
            )
            return len(data_to_upsert)
        except Exception as e:
            logger.error(f"Error upserting document: {e}")
            raise

    async def upsert_documents(self, file) -> int:
        content = await file.read()
        logger.info(f"Processing ingestion for file: {file.filename}")

        if file.filename.endswith(".json"):
            documents = self.processor.process_json(content, file.filename)
        elif file.filename.endswith(".txt"):
            documents = self.processor.process_txt(content, file.filename)
        else:
            raise ValueError("Unsupported file format. Use .json or .txt")

        return await self._process_and_upsert(documents, file.filename)
