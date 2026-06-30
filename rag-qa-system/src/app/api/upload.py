import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse
from app.services.document_service import load_and_split
from app.core.vector_store import add_documents_to_store

router = APIRouter(prefix="/api", tags=["文档上传"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，仅支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        chunks = load_and_split(file_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="文档解析后无有效内容")

        add_documents_to_store(chunks)

        return UploadResponse(
            status="success",
            filename=file.filename or "unknown",
            chunks_count=len(chunks),
            message=f"文档已成功上传并索引，共切分为 {len(chunks)} 个文本块",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")