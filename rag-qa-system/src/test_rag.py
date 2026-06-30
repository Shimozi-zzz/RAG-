import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.services.document_service import load_and_split
from app.core.vector_store import add_documents_to_store, similarity_search
from app.services.qa_service import answer_question

test_file = os.path.join(os.path.dirname(__file__), "RAG技术白皮书.md")

print("=" * 60)
print("【步骤 1】文档加载与切分")
print("=" * 60)
chunks = load_and_split(test_file)
print(f"文档切分完成，共 {len(chunks)} 个文本块")
for i, chunk in enumerate(chunks[:3]):
    preview = chunk.page_content[:80].replace("\n", " ")
    print(f"  Chunk {i+1}: {preview}...")

print()
print("=" * 60)
print("【步骤 2】向量化并存入 Chroma 向量库")
print("=" * 60)
add_documents_to_store(chunks)
print("向量化入库完成！")

print()
print("=" * 60)
print("【步骤 3】语义检索测试")
print("=" * 60)
queries = [
    "什么是RAG？",
    "Chunk Size 应该设置为多少？",
    "有哪些高级RAG技术？",
]
for q in queries:
    docs = similarity_search(q, k=3)
    print(f"\n  Q: {q}")
    for j, doc in enumerate(docs):
        preview = doc.page_content[:60].replace("\n", " ")
        print(f"    检索 #{j+1}: {preview}...")

print()
print("=" * 60)
print("【步骤 4】RAG 问答测试（调用 DeepSeek）")
print("=" * 60)
result = answer_question("什么是RAG？请用简洁的语言解释。")
print(f"\n  Q: 什么是RAG？请用简洁的语言解释。")
print(f"  A: {result['answer']}")
print(f"  引用来源数: {len(result['sources'])}")

print()
print("=" * 60)
print("端到端验证完成！")
print("=" * 60)