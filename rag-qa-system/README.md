# RAG 知识库问答系统

基于 **FastAPI + LangChain + Chroma + DeepSeek** 的 RAG（检索增强生成）垂直领域问答系统。

## 技术栈

| 层级       | 技术选型                                                 |
| ---------- | -------------------------------------------------------- |
| Web 框架   | FastAPI                                                  |
| AI 编排    | LangChain                                                |
| 向量数据库 | Chroma（本地持久化）                                     |
| 大语言模型 | DeepSeek（OpenAI 兼容 API）                              |
| Embedding  | BAAI/bge-small-zh-v1.5（sentence-transformers 本地运行） |

## 快速开始

本项目分离了**开发环境**和**发布包**两个独立目录：

- **开发者**：直接打开 `src/` 目录，使用系统 Python 运行
- **最终用户**：拿到 `dist/rag-qa-system-release/` 发布包，双击 `run.bat` 即用

### 开发者（日常开发）

```bat
# 1. 编辑 src/.env，填入 API Key
# 2. pip install -r src/requirements.txt
# 3. 双击 src/dev.bat，或命令行：
cd src
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器访问 http://localhost:8000/docs

### 最终用户（拿到发布包的同学/老师）

```bat
# 1. 将 .env.example 重命名为 .env，填入 API Key
# 2. 双击 run.bat
```

一键启动，浏览器访问 http://localhost:8888/docs

> 发布包内置完整 Python 3.11.9 环境和所有依赖（含 PyTorch CPU 版），**无需安装任何软件**。

### 构建发布包（开发者执行）

```powershell
.\build_release.ps1
```

脚本自动完成：下载 Python embeddable → 安装 pip → 安装全部依赖（CPU 版 PyTorch + 清华源）→ 拷贝源码 → 生成 run.bat。产物输出到 `dist/rag-qa-system-release/`。

---

## API 接口

### POST /api/upload — 文档上传与索引

上传 PDF / Markdown / TXT 知识库文档，自动切分并存入向量库。

**请求：**

```
Content-Type: multipart/form-data
file: 知识库文档（.pdf / .md / .txt）
```

**响应示例：**

```json
{
  "status": "success",
  "filename": "RAG技术白皮书.pdf",
  "chunks_count": 42,
  "message": "文档已成功上传并索引，共切分为 42 个文本块"
}
```

### POST /api/chat — 知识库问答

基于已索引的知识库文档进行智能问答。

**请求：**

```json
{
  "question": "什么是检索增强生成？"
}
```

**响应示例：**

```json
{
  "answer": "检索增强生成（RAG）是一种结合信息检索与大语言模型的技术架构...",
  "sources": [
    {
      "content": "RAG 全称是 Retrieval-Augmented Generation...",
      "metadata": {
        "source": "RAG技术白皮书.pdf",
        "page": 3
      }
    }
  ]
}
```

---

## 操作流程

浏览器打开 Swagger 文档页（http://localhost:8000/docs 或 8888/docs）后，依次操作以下两个接口。

### 步骤一：上传知识库文档 `POST /api/upload`

| 操作 | 说明                                                                 |
| ---- | -------------------------------------------------------------------- |
| ①    | 在 Swagger 页面找到 `POST /api/upload`，点击展开                     |
| ②    | 点击右侧 **Try it out** 按钮                                         |
| ③    | 在 `file` 字段点击 **Choose File**                                   |
| ④    | 选择项目自带的 `RAG技术白皮书.md`（或任意 `.pdf` `.md` `.txt` 文档） |
| ⑤    | 点击下方 **Execute** 按钮                                            |

**期望返回：**

```json
{
  "status": "success",
  "filename": "RAG技术白皮书.md",
  "chunks_count": 5,
  "message": "文档已成功上传并索引，共切分为 5 个文本块"
}
```

### 步骤二：智能问答 `POST /api/chat`

| 操作 | 说明                                      |
| ---- | ----------------------------------------- |
| ①    | 找到 `POST /api/chat`，点击展开           |
| ②    | 点击 **Try it out** 按钮                  |
| ③    | 在 `Request body` 输入框中填入提问 JSON： |

```json
{
  "question": "什么是RAG？请用简洁的语言解释。"
}
```

| 操作 | 说明                  |
| ---- | --------------------- |
| ④    | 点击 **Execute** 按钮 |

**期望返回：**

```json
{
  "answer": "RAG（检索增强生成）是一种结合信息检索与大语言模型的技术架构...",
  "sources": [
    {
      "content": "RAG 全称为 Retrieval-Augmented Generation...",
      "metadata": { "source": "RAG技术白皮书.md" }
    }
  ]
}
```

> `sources` 数组展示了回答引用的原始文档片段——这是 RAG 相比直接调用大模型的核心优势。

### 步骤三（可选）：验证知识边界（兜底能力）

故意提一个知识库不包含的问题，验证系统不会瞎编：

```json
{
  "question": "今天北京的天气怎么样？"
}
```

**期望返回：** 类似 `"根据现有知识库无法回答该问题"`，而非编造天气信息。

> 这是 RAG 防幻觉的关键设计——Prompt 强制要求模型在背景知识不足时明确告知，而不是自由发挥。

### 终端测试（可选）

也可以直接运行测试脚本，无需启动 Web 服务：

```powershell
cd src
python test_rag.py
```

---

## 项目结构

```
rag-qa-system/                    ← Git 仓库根目录
├── src/                          ← 开发根目录（日常编辑入口）
│   ├── app/
│   │   ├── main.py               # FastAPI 应用入口
│   │   ├── config.py             # 全局配置，读取 .env
│   │   ├── __init__.py           # HF_ENDPOINT 镜像站配置
│   │   ├── api/
│   │   │   ├── upload.py         # POST /api/upload
│   │   │   └── chat.py           # POST /api/chat
│   │   ├── services/
│   │   │   ├── document_service.py   # 文档加载 + 文本切分
│   │   │   └── qa_service.py         # RAG 问答编排
│   │   ├── core/
│   │   │   ├── embeddings.py     # Embedding 模型封装
│   │   │   ├── llm.py            # DeepSeek 大模型封装
│   │   │   ├── vector_store.py   # Chroma 向量库操作
│   │   │   └── retriever.py      # 检索器配置
│   │   └── models/
│   │       └── schemas.py        # Pydantic 请求/响应模型
│   ├── data/
│   │   ├── chroma_db/            # 向量数据库持久化（.gitignore）
│   │   └── uploads/              # 上传文档暂存（.gitignore）
│   ├── .env                      # 环境变量（API Key 等，.gitignore）
│   ├── .env.example              # 环境变量模板（分发用占位符）
│   ├── dev.bat                   # 开发用启动脚本（--reload 热重载）
│   ├── requirements.txt          # Python 依赖清单
│   ├── test_rag.py               # 端到端测试脚本
│   ├── tune_experiment.py        # 参数调优实验脚本
│   ├── check_hf.py               # HuggingFace 端点诊断脚本
│   └── RAG技术白皮书.md           # 测试用知识库文档
├── build_release.ps1             # 一键构建发布包脚本
├── dist/                         # 打包产物（.gitignore，不进 Git）
│   └── rag-qa-system-release/
│       ├── src/                  # 拷贝的源代码（不含 .env、chroma_db、uploads）
│       ├── python-embed/         # 便携 Python 3.11.9 + 全部依赖
│       └── run.bat               # 最终用户双击启动脚本
├── README.md                     # 本文件
├── SETUP_EMBED.md                # 便携环境构建说明
└── .gitignore                    # Git 忽略规则
```

## RAG 管道流程

```
用户上传文档 → TextSplitter 切分 → BGE Embedding 向量化 → Chroma 入库
                                                              ↓
用户提问 → BGE Embedding 向量化 → Chroma 检索 Top-K 相似片段
                                                              ↓
拼接上下文 Prompt → DeepSeek 生成回答 → 返回答案 + 来源
```

## 可调参数（.env）

| 参数            | 默认值                 | 说明                               |
| --------------- | ---------------------- | ---------------------------------- |
| CHUNK_SIZE      | 500                    | 文本切分块大小                     |
| CHUNK_OVERLAP   | 50                     | 相邻块重叠字符数                   |
| TOP_K           | 5                      | 检索返回的最相关文档数             |
| EMBEDDING_MODEL | BAAI/bge-small-zh-v1.5 | Embedding 模型（首次运行自动下载） |
| HF_ENDPOINT     | https://hf-mirror.com  | HuggingFace 镜像站（国内加速）     |

## 参数调优

运行调优实验脚本，对比不同参数组合的检索效果：

```powershell
cd src
python tune_experiment.py
```

### 实测数据（以 RAG技术白皮书.md 为测试文档）

| 配置 | Chunk Size | Overlap | 切分块数 | Top-K=3 召回率 | Top-K=5 召回率 | Top-K=10 召回率 |
| ---- | ---------- | ------- | -------- | -------------- | -------------- | --------------- |
| A    | 200        | 0       | 14       | 56%            | 56%            | 83%             |
| B    | 500        | 50      | 5        | 67%            | **100%**       | 100%            |
| C    | 800        | 100     | 3        | **100%**       | 100%           | 100%            |

### 调优建议

| 参数               | 推荐值             | 理由                                              |
| ------------------ | ------------------ | ------------------------------------------------- |
| **Chunk Size**     | 500                | 太小（200）→ 语义碎片化；太大（800+）→ 单块噪声多 |
| **Chunk Overlap**  | Chunk Size x 10%   | 保护跨块边界的完整语义，不显著增加存储            |
| **Top-K**          | 5                  | 小文档可用 3；多文档知识库建议 5~7                |
| **Embedding 模型** | bge-large 精度更高 | 答辩时可展示切换对比（small vs large）            |

---

## 常见问题

### 启动报 `ModuleNotFoundError: No module named 'app'`

**原因：** 当前工作目录不在 `src/` 下。

**解决：** 开发时 `cd src` 后运行，或直接双击 `dev.bat`；发布包直接双击 `run.bat`。

### 启动报 `AuthenticationError: 401` API Key 无效

**原因：** `.env` 中的 `DEEPSEEK_API_KEY` 未配置或填写错误。

**解决：** 编辑 `.env` 文件，确保填写了正确的 DeepSeek API Key。

### 首次运行卡在下载 Embedding 模型

**原因：** 首次运行需要从 HuggingFace 下载 Embedding 模型（约 100MB）。

**解决：** 已默认使用 `hf-mirror.com` 镜像加速。若仍超时，检查网络代理设置。

### 端口被占用（发布包用户）

**现象：** `run.bat` 启动后报 `[WinError 10013]`。

**自动处理：** `run.bat` 会先从 `.env` 读取 `PORT`（默认 8888），失败后自动切换到 9999。

**如果两个端口都失败：** 屏幕上会显示排查指引，按以下步骤操作：

1. 用记事本打开 `.env`，找到 `PORT=8888`，改成 `PORT=3000`
2. 如果 3000 也不行，尝试 3001、5000、8080 等
3. 保存后重新双击 `run.bat`

> **根本原因：** Windows 的 Hyper-V、WSL 或 IIS 可能会预留一段端口范围（含 8888）。运行 `netsh interface ipv4 show excludedportrange protocol=tcp` 可查具体哪些端口被系统锁定了。

### 端口被占用（开发者）

**现象：** `dev.bat` 报 `[WinError 10013]`。

**解决：** `dev.bat` 默认使用 `127.0.0.1:3000`（避开常见冲突端口）。如需修改：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload
```

> 如果 PID 4（System 进程）占用了端口，说明被 Windows 预留。换端口是最快的方式。

## 注意事项

- **发布包免安装**：`dist/` 产物内置完整 Python 环境和全部依赖，解压即用
- **首次启动**：需要联网下载 Embedding 模型（约 100MB），后续启动秒级
- **数据目录**：向量库持久化在 `data/chroma_db/`，删除该目录可清空知识库
- **隐私安全**：`.env` 包含 API Key，分发时使用 `.env.example` 占位符，切勿提交到 Git
- **修改端口**：编辑 `.env` 中的 `PORT` 值，`run.bat` 会自动读取
- **Git 忽略**：`dist/`、`data/chroma_db/`、`data/uploads/`、`.env`、`__pycache__/` 均不应提交
- **答辩演示**：直接**双击 `run.bat`**，无需任何手动操作