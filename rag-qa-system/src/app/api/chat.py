from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, SourceItem
from app.services.qa_service import answer_question

router = APIRouter(prefix="/api", tags=["智能问答"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = answer_question(req.question)
        sources = [
            SourceItem(content=s["content"], metadata=s["metadata"])
            for s in result["sources"]
        ]
        return ChatResponse(answer=result["answer"], sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")