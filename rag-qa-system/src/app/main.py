from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.config import settings

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

PLACEHOLDER_PATTERNS = [
    "你的 DeepSeek API Key",
    "你的 ",
    "sk-xxxxxxxx",
    "sk-xxxx",
    "sk-your-",
    "sk-test-",
    "在这里填入",
]

def _is_valid_api_key(key: str) -> bool:
    if not key:
        return False
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in key:
            return False
    if not key.startswith("sk-"):
        return False
    if len(key) < 15:
        return False
    return True


@app.on_event("startup")
async def startup_check_api_key():
    key = settings.DEEPSEEK_API_KEY
    if _is_valid_api_key(key):
        return
    print()
    print("=" * 55)
    print("  [警告] DEEPSEEK_API_KEY 未配置或无效！")
    print("=" * 55)
    print()
    print("  API Key 无效，AI 智能问答功能将无法使用。")
    print()
    print("  解决方法：")
    print("    1. 用记事本打开 .env 文件（没有则把 .env.example 改名）")
    print("    2. 将 DEEPSEEK_API_KEY= 后面替换为你的真实 Key")
    print("    3. 申请地址: https://platform.deepseek.com")
    print("    4. 修改保存后，重启服务即可")
    print()
    print("=" * 55)
    print()


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