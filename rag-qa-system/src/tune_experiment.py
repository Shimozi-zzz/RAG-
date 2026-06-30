"""RAG 参数调优实验脚本 —— 对比不同 Chunk Size / Overlap / Top-K 的检索效果

使用方法：
  $env:PYTHONPATH = "."
  python tune_experiment.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.document_service import load_and_split
from app.core.vector_store import add_documents_to_store, get_vector_store, similarity_search
from app.core.embeddings import get_embeddings
from app.config import settings

TEST_FILE = os.path.join(os.path.dirname(__file__), "RAG技术白皮书.md")


def eval_retrieval(question: str, expected_keywords: list[str], k: int):
    """评估检索质量：检查 Top-K 结果中是否包含预期关键词"""
    docs = similarity_search(question, k=k)
    hits = 0
    for keyword in expected_keywords:
        for doc in docs:
            if keyword in doc.page_content:
                hits += 1
                break
    return {
        "question": question,
        "k": k,
        "hits": hits,
        "total_keywords": len(expected_keywords),
        "recall_rate": f"{hits / len(expected_keywords) * 100:.0f}%",
        "retrieved_docs": len(docs),
    }


def run_experiment(config_label: str, chunk_size: int, chunk_overlap: int, top_k_values: list[int]):
    """用指定参数重建向量库，评估不同 Top-K 下的检索效果"""
    print(f"\n{'=' * 60}")
    print(f"实验配置：{config_label}")
    print(f"  Chunk Size = {chunk_size}, Overlap = {chunk_overlap}")
    print(f"{'=' * 60}")

    # 修改全局配置
    settings.CHUNK_SIZE = chunk_size
    settings.CHUNK_OVERLAP = chunk_overlap

    # 重建向量库
    chunks = load_and_split(TEST_FILE)
    print(f"  切分结果：{len(chunks)} 个文本块")

    store = get_vector_store()
    try:
        store.reset_collection()
    except Exception:
        pass
    add_documents_to_store(chunks)
    print(f"  向量库已重建")

    # 测试问题 + 预期关键词
    test_cases = [
        ("什么是RAG？", ["Retrieval-Augmented", "检索增强", "向量数据库"]),
        ("Chunk Size 应该设置多大？", ["Chunk Size", "300", "500"]),
        ("有哪些高级RAG技术？", ["Self-Querying", "HyDE", "Rerank", "Multi-Vector"]),
    ]

    for k in top_k_values:
        print(f"\n  --- Top-K = {k} ---")
        for q, keywords in test_cases:
            result = eval_retrieval(q, keywords, k)
            bar = "█" * result["hits"] + "░" * (result["total_keywords"] - result["hits"])
            print(f"    Q: {q}")
            print(f"       召回: {result['recall_rate']}  [{bar}]  ({result['hits']}/{result['total_keywords']})")

    return len(chunks)


if __name__ == "__main__":
    print("=" * 60)
    print("RAG 参数调优对比实验")
    print("=" * 60)

    experiments = [
        ("A: 小 Chunk + 无 Overlap", 200, 0),
        ("B: 中等 Chunk + 小 Overlap（默认）", 500, 50),
        ("C: 大 Chunk + 大 Overlap", 800, 100),
    ]

    top_k_values = [3, 5, 10]
    results = {}

    for label, chunk_size, overlap in experiments:
        n_chunks = run_experiment(label, chunk_size, overlap, top_k_values)
        results[label] = n_chunks

    print(f"\n{'=' * 60}")
    print("总结")
    print(f"{'=' * 60}")
    print(f"\n{'配置':<35} {'切分块数':>10}")
    print("-" * 47)
    for label, n in results.items():
        print(f"{label:<35} {n:>10}")
    print("\n建议：")
    print("  - Chunk Size 过小 → 语义碎片化，召回率下降")
    print("  - Chunk Size 过大 → 块数少但噪声多，检索精度下降")
    print("  - Overlap 适中 → 保护块边界关键信息，不显著增加存储")
    print("  - Top-K=5 → 大多数场景的最佳平衡点")
    print("  - Top-K=10 → 适合复杂问题，但 Token 消耗加倍")