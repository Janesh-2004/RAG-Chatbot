"""
FastAPI Backend for RAG Chatbot
"""
import logging
import os
import shutil
import uuid
from threading import Lock
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_indexer import RAGIndexer

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0",
    description="Production-ready RAG Chatbot with Azure OpenAI and Azure AI Search"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rag-backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy Indexer Init
rag_indexer: Optional[RAGIndexer] = None
rag_indexer_error: Optional[str] = None
rag_indexer_lock = Lock()


def _initialise_indexer() -> None:
    global rag_indexer, rag_indexer_error
    try:
        logger.info("Initialising RAG indexer...")
        rag_indexer = RAGIndexer()
        rag_indexer_error = None
        logger.info("RAG indexer ready.")
    except (ValueError, RuntimeError, KeyError) as exc:
        rag_indexer = None
        rag_indexer_error = str(exc)
        logger.exception("Failed to initialise RAG indexer: %s", exc)


_initialise_indexer()

# Upload directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "30"))
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']


# Pydantic Models
class QueryRequest(BaseModel):
    question: str
    chat_id: str
    chat_name: str = None  # Optional chat name for index lookup


class QueryResponse(BaseModel):
    success: bool
    answer: str
    sources: list


class StatusResponse(BaseModel):
    has_documents: bool
    ready: bool
    message: str


class ResetRequest(BaseModel):
    chat_id: str


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG Chatbot API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "chat": "/chat",
            "query": "/query",
            "status": "/status",
            "reset": "/reset"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns the health status of the API and its dependencies
    """
    health_status = {
        "status": "ok",
        "service": "RAG Chatbot API",
        "version": "1.0.0"
    }
    
    # Check if RAG indexer is initialized
    if rag_indexer is None:
        health_status["status"] = "degraded"
        health_status["rag_indexer"] = "not initialized"
        if rag_indexer_error:
            health_status["error"] = rag_indexer_error
    else:
        health_status["rag_indexer"] = "ready"
    
    return health_status


def _require_indexer() -> RAGIndexer:
    global rag_indexer
    if rag_indexer is None:
        with rag_indexer_lock:
            if rag_indexer is None:
                _initialise_indexer()

    if rag_indexer is None:
        message = "RAG indexer unavailable. Check Azure credentials."
        if rag_indexer_error:
            message += f" Details: {rag_indexer_error}"
        raise HTTPException(status_code=503, detail=message)

    return rag_indexer


def _ensure_chat_upload_dir(chat_id: str) -> str:
    safe = chat_id.replace("..", "").replace("/", "_").replace("\\", "_")
    chat_dir = os.path.join(UPLOAD_DIR, safe)
    os.makedirs(chat_dir, exist_ok=True)
    return chat_dir


def _delete_chat_uploads(chat_id: str):
    safe = chat_id.replace("..", "").replace("/", "_").replace("\\", "_")
    chat_dir = os.path.join(UPLOAD_DIR, safe)
    if os.path.isdir(chat_dir):
        shutil.rmtree(chat_dir, ignore_errors=True)


# ================================================================
#  UPLOAD DOCUMENT
# ================================================================
@app.post("/upload")
async def upload_file(
    chat_id: str = Form(...), 
    chat_name: str = Form(None),
    file: UploadFile = File(...)
):
    try:
        indexer = _require_indexer()

        if not chat_id.strip():
            raise HTTPException(status_code=400, detail="chat_id is required")

        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)

        if size / (1024 * 1024) > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Limit: {MAX_FILE_SIZE_MB}MB",
            )

        upload_dir = _ensure_chat_upload_dir(chat_id)
        unique_name = uuid.uuid4().hex + ext
        path = os.path.join(upload_dir, unique_name)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = indexer.process_document(path, file.filename, chat_id, chat_name)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return {
            "success": True,
            "message": result["message"],
            "filename": file.filename,
            "chunks": result["chunks"],
            "chat_id": chat_id,
            "has_documents": True,
        }

    except (ValueError, RuntimeError, IOError) as e:
        logger.exception("Upload problem: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================================================
#  CHAT ENDPOINT (Alias for query, supports future streaming)
# ================================================================
@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest = Body(...)):
    """
    Chat endpoint - currently aliases to query endpoint
    Future: Will support streaming responses
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if not request.chat_id.strip():
            raise HTTPException(status_code=400, detail="chat_id is required")

        result = _require_indexer().query(request.question, request.chat_id, request.chat_name)

        return QueryResponse(
            success=result["success"],
            answer=result["answer"],
            sources=result["sources"],
        )

    except (ValueError, RuntimeError, KeyError) as e:
        logger.exception("Chat error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================================================
#  FIXED QUERY ENDPOINT (MAIN ISSUE)
# ================================================================
@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest = Body(...)):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if not request.chat_id.strip():
            raise HTTPException(status_code=400, detail="chat_id is required")

        result = _require_indexer().query(request.question, request.chat_id, request.chat_name)

        return QueryResponse(
            success=result["success"],
            answer=result["answer"],
            sources=result["sources"],
        )

    except (ValueError, RuntimeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================================================
#  STATUS
# ================================================================
@app.get("/status", response_model=StatusResponse)
async def get_status(chat_id: Optional[str] = Query(default=None)):
    try:
        try:
            indexer = _require_indexer()
        except HTTPException as exc:
            return StatusResponse(
                has_documents=False,
                ready=False,
                message=str(exc.detail),
            )

        status = indexer.get_status(chat_id)
        return StatusResponse(**status)

    except (ValueError, RuntimeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================================================
#  RESET CHAT
# ================================================================
@app.post("/reset")
async def reset_system(request: ResetRequest):
    try:
        if not request.chat_id.strip():
            raise HTTPException(status_code=400, detail="chat_id is required")

        indexer = _require_indexer()
        result = indexer.reset(request.chat_id)

        _delete_chat_uploads(request.chat_id)

        return result

    except Exception as e:
        logger.exception("Reset error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
