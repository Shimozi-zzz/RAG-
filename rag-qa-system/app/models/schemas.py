from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., description="用户提问内容", min_length=1)


class SourceItem(BaseModel):
    content: str = Field(..., description="检索到的文档片段前200字")
    metadata: dict = Field(default_factory=dict, description="文档元数据")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="模型生成的回答")
    sources: list[SourceItem] = Field(default_factory=list, description="检索到的背景知识来源")


class UploadResponse(BaseModel):
    status: str = Field(..., description="处理状态")
    filename: str = Field(..., description="上传的文件名")
    chunks_count: int = Field(..., description="切分后的文档块数量")
    message: str = Field(default="", description="附加说明")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="错误详情")