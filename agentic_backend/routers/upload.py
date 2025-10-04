from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
import uuid
from auth.dependencies import get_current_user
from auth.decorators import require_org_admin
from database import get_async_db
from sqlalchemy.future import select
from models.app import FileUpload

from opensearchpy import OpenSearch
from langchain_community.embeddings import SentenceTransformerEmbeddings

router = APIRouter()

@router.get("/api/scrap-ui")
async def scrap_ui(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    return await require_org_admin(_scrap_ui)(db=db, current_user=current_user)

async def _scrap_ui(db, current_user):
    # ...scrap UI logic...
    return {"status": "visible", "user": current_user.username}


@router.post("/api/embeddings/upload")
async def upload_and_embed(file: UploadFile = File(...), db: AsyncSession = Depends(get_async_db), current_user = Depends(get_current_user)):
    """
    Accepts a document upload, splits into chunks, generates embeddings for each chunk, and stores them in OpenSearch.
    """
    import re
    # Save file to disk (optional)
    file_location = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    text = content.decode(errors="ignore")

    # Simple chunking: split by paragraphs or every 500 characters
    chunk_size = 500
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size) if text[i:i+chunk_size].strip()]

    # Save metadata to FileUpload table (embedding_status: processing)
    file_upload = FileUpload(
        user_id=str(current_user.id),
        file_name=file.filename,
        upload_time=datetime.utcnow(),
        embedding_status="processing"
    )
    db.add(file_upload)
    await db.commit()
    await db.refresh(file_upload)

    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Connect to OpenSearch
    client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}])
    index_name = "embeddings"
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body={
            "settings": {"index": {"knn": True}},
            "mappings": {
                "properties": {
                    "filename": {"type": "keyword"},
                    "chunk_id": {"type": "keyword"},
                    "content": {"type": "text"},
                    "embedding": {"type": "knn_vector", "dimension": 384}
                }
            }
        })

    # Index each chunk with its embedding
    results = []
    for idx, chunk in enumerate(chunks):
        embedding = embedder.embed_query(chunk)
        doc = {
            "filename": file.filename,
            "chunk_id": f"{file.filename}_{idx}",
            "content": chunk,
            "embedding": embedding
        }
        resp = client.index(index=index_name, body=doc)
        results.append({"chunk_id": doc["chunk_id"], "opensearch_id": resp.get("_id")})

    # Update metadata after embedding
    file_upload.embedding_status = "ready"
    file_upload.vector_count = len(chunks)
    db.add(file_upload)
    await db.commit()
    await db.refresh(file_upload)

    return {
        "file_id": str(file_upload.file_id),
        "filename": file.filename,
        "chunks": len(chunks),
        "indexed": results,
        "embedding_status": file_upload.embedding_status,
        "vector_count": file_upload.vector_count,
        "message": f"{len(chunks)} chunks embedded and stored in OpenSearch."
    }


@router.get("/api/files/status")
async def get_file_status(user_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(FileUpload).where(FileUpload.user_id == user_id))
    files = result.scalars().all()
    return [
        {
            "file_id": str(f.file_id),
            "file_name": f.file_name,
            "upload_time": f.upload_time.isoformat(),
            "embedding_status": f.embedding_status,
            "vector_count": f.vector_count
        }
        for f in files
    ]