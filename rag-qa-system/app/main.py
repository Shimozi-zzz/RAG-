from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="RAG 知识库问答系统",
    description="基于 LangChain + Chroma + DeepSeek 的 RAG 垂直领域问答系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "service": "RAG 知识库问答系统",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "chat": "/api/chat",
            "docs": "/docs",
        },
    }