from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from dependencies.dependency import get_ingest_document, get_access_admin
from services.document_ingestion_service import IngestDocumentService
import os

router = APIRouter(prefix="/admin/ingestion", tags=["ingestion"])


@router.post("/ingest-file")
async def ingest_file(
    file: UploadFile = File(...),
    ingest_service: IngestDocumentService = Depends(get_ingest_document),
    admin=Depends(get_access_admin),
):
    # Save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    try:
        chunks = ingest_service.ingest_file(temp_path)
        os.remove(temp_path)
        return {"message": "Ingestion successful", "chunks": chunks}
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))
