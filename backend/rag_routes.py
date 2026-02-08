from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from rag.rag_assistant import OperationsHandbookRAG
from pydantic import BaseModel

router = APIRouter(prefix="/api/rag", tags=["RAG Assistant"])

rag_assistant = None

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3

class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list
    context: str

@router.on_event("startup")
async def load_rag():
    global rag_assistant
    handbook_path = Path(__file__).parent.parent.parent / "docs" / "OPERATIONS_HANDBOOK.md"
    if handbook_path.exists():
        rag_assistant = OperationsHandbookRAG(str(handbook_path))
        rag_assistant.build_index()

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if rag_assistant is None:
        raise HTTPException(status_code=503, detail="RAG assistant not initialized")
    
    try:
        result = rag_assistant.answer_question(request.question, top_k=request.top_k)
        return AnswerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.get("/health")
async def rag_health():
    return {
        "status": "healthy" if rag_assistant is not None else "not_initialized",
        "chunks_indexed": len(rag_assistant.chunks) if rag_assistant else 0
    }
