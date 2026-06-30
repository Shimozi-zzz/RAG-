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

> [!tip] 一键运行
> 仅需两步：**① 配置 API Key → ② 双击 `start.bat`**。脚本自动完成虚拟环境创建、依赖安装（清华源加速）、服务启动。

### 1. 配置 API Key

编辑项目根目录的 `.env` 文件，填入你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-v4-flash
```

> 申请地址：https://platform.deepseek.com
>
> 如果无法访问 HuggingFace 下载 Embedding 模型，`.env` 中已预设 `HF_ENDPOINT=https://hf-mirror.com` 镜像站。

其他参数（Chunk 大小、Top-K 等）已在 `.env` 中预设默认值，可按需调整。

### 2. 双击启动

**双击 `start.bat`**，脚本自动完成以下流程：

```
检测 .venv 是否存在
  ├── 不存在 → 自动创建虚拟环境 .venv
  └── 已存在 → 跳过创建
         ↓
激活虚拟环境 → 升级 pip（清华源）
         ↓
pip install -r requirements.txt（清华源 + --only-binary 强制二进制包）
         ↓
启动 uvicorn → http://localhost:8888/docs
```

> `start.bat` 已内置以下优化，确保他人电脑也能无缝运行：
>
> - **独立虚拟环境** `.venv`：与系统 Python 隔离开，不污染也不缺包
> - **清华镜像源**：国内下载加速
> - **`--only-binary :all:`**：强制下载预编译 wheel 包，**彻底避免** 因缺少 Visual Studio C++ 编译环境导致 chromadb / tokenizers 安装失败
> - **端口自适应**：8888 被占用时自动切换 9999

### 3. 打开 Swagger 交互文档

浏览器访问 **http://localhost:8888/docs** 如果8888无法访问，请将8888->9999

---

### 手动启动（备选）

如果不想用 `start.bat`，可手动操作：

```powershell
cd rag-qa-system
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

> 不要在其他目录执行，必须在 `rag-qa-system/` 目录下，否则报 `ModuleNotFoundError: No module named 'app'`。

### 6. 操作流程

浏览器打开 **http://localhost:8888/docs** 后，依次操作以下两个接口。

---

#### 步骤一：上传知识库文档 `POST /api/upload`

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

---

#### 步骤二：智能问答 `POST /api/chat`

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

> **Tips：** `sources` 数组展示了回答引用的原始文档片段，点击可查看完整检索来源——这是 RAG 相比直接调用大模型的核心优势。\*\*

#### 步骤三（可选）：验证知识边界（兜底能力）

故意提一个知识库不包含的问题，验证系统不会瞎编：

```json
{
  "question": "今天北京的天气怎么样？"
}
```

**期望返回：** 类似 `"根据现有知识库无法回答该问题"`，而非编造天气信息。

> 这是 RAG 防幻觉的关键设计——Prompt 强制要求模型在背景知识不足时明确告知，而不是自由发挥。

#### 终端测试（可选）

也可以直接运行测试脚本，无需启动 Web 服务：

```powershell
python test_rag.py
```

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

## 项目结构

```
rag-qa-system/
├── .env                      # 环境变量（API Key、模型参数等）
├── .gitignore                # Git 忽略规则（排除 .venv/、data/chroma_db/ 等）
├── requirements.txt          # Python 依赖清单（宽松版本范围）
├── README.md
├── start.bat                 # 一键启动（自动创建 .venv + 安装依赖 + 启动）
├── RAG技术白皮书.md           # 测试用知识库文档
├── test_rag.py               # 端到端测试脚本
├── tune_experiment.py        # 参数调优实验脚本
├── .venv/                    # 虚拟环境（start.bat 首次运行自动生成）
├── app/
│   ├── __init__.py           # 注入 HF_ENDPOINT 镜像站配置
│   ├── main.py               # FastAPI 应用入口
│   ├── config.py             # 全局配置，读取 .env
│   ├── api/
│   │   ├── upload.py         # /api/upload 文档上传
│   │   └── chat.py           # /api/chat  智能问答
│   ├── services/
│   │   ├── document_service.py   # 文档加载 + 文本切分
│   │   └── qa_service.py         # RAG 问答编排
│   ├── core/
│   │   ├── embeddings.py     # Embedding 模型封装
│   │   ├── llm.py            # DeepSeek 大模型封装
│   │   ├── vector_store.py   # Chroma 向量库操作
│   │   └── retriever.py      # 检索器配置
│   └── models/
│       └── schemas.py        # Pydantic 请求/响应模型
└── data/
    ├── uploads/              # 上传文档暂存
    └── chroma_db/            # 向量数据库持久化
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

**原因：** 当前终端工作目录不在项目根目录。

**解决：** 直接双击 `start.bat`（脚本内置 `cd /d "%~dp0"` 自动定位项目目录）。

### 启动报 `[WinError 10013]` 端口被占用

**原因：** 默认端口 8888 已被其他程序占用。

**解决：** `start.bat` 已内置自动降级（8888 → 9999），无需手动干预。

### 启动报 `AuthenticationError: 401` API Key 无效

**原因：** `.env` 中的 `DEEPSEEK_API_KEY` 未配置或填写错误。

**解决：** 检查 `.env` 文件第 5 行，确保填写了正确的 DeepSeek API Key。

### 首次运行卡在下载模型 / 依赖安装

**原因：** 网络访问 HuggingFace 或 PyPI 受限。

**解决：** `start.bat` 已默认使用 `hf-mirror.com`（模型下载）和清华源（pip），国内下载加速。若仍超时，检查是否需要关闭代理或切换网络。

### chromadb / tokenizers 编译报错

**原因：** Windows 缺少 Visual Studio C++ 编译环境，`chromadb` 和 `tokenizers` 依赖的 C 扩展无法编译。

**解决：** `start.bat` 已默认使用 `--only-binary :all:` 参数，强制 pip 下载预编译的 `.whl` 二进制包，**不触发本地编译**。同时 `requirements.txt` 已放宽版本限制，pip 可自动选择兼容的预编译版本。

### 首次启动慢（创建虚拟环境 + 下载依赖）

**说明：** 首次双击 `start.bat` 需要完成 `.venv` 创建 + 依赖安装 + Embedding 模型下载，约 5-10 分钟（取决于网速）。之后的每次启动都是秒级。

## 注意事项

- 首次运行会自动：创建 `.venv` 虚拟环境 → 安装依赖 → 下载 Embedding 模型（约 100MB），请保持网络畅通
- `.venv/`、`data/chroma_db/`、`__pycache__/` 均不应提交到 Git，建议配置 `.gitignore`
- `.env` 文件包含 API Key，请勿提交到 Git
- 向量库数据持久化在 `data/chroma_db/` 目录，删除该目录可清空知识库
- 答辩演示时直接**双击 `start.bat`**，无需任何手动操作
