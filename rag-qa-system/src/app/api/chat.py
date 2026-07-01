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
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Authentication" in error_msg or "api key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="API Key 无效，请检查 .env 文件中的 DEEPSEEK_API_KEY 是否正确配置",
            )
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"问答处理失败: {error_msg}")