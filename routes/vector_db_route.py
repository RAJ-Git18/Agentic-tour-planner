from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from dependencies.dependency import (
    get_ingest_document,
    get_access_admin,
    get_pinecone_service,
)
from services.document_ingestion_service import IngestDocumentService
from services.pinecone_service import PineconeService
import os

router = APIRouter(prefix="/admin", tags=["vector store"])


@router.post("/ingest-file")
async def ingest_file(
    file: UploadFile = File(...),
    ingest_service: IngestDocumentService = Depends(get_ingest_document),
):
    try:
        chunks = await ingest_service.upsert_documents(file)
        return {"message": "Ingestion successful", "chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete-index")
async def delete_index(
    pinecone_service: PineconeService = Depends(get_pinecone_service),
):
    """
    Delele the index and create the new one
    """
    pinecone_service.delete_index()
    return {"message": "Index deleted successfully"}
