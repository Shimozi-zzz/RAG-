from langchain_core.prompts import ChatPromptTemplate
from app.core.vector_store import similarity_search
from app.core.llm import get_llm

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的知识库问答助手。请严格基于以下提供的背景知识来回答用户的问题。

要求：
1. 如果背景知识足以回答问题，请组织语言清晰、准确地回答。
2. 如果背景知识不足，请明确告知用户"根据现有知识库无法回答该问题"。
3. 回答时不要编造背景知识中不存在的信息。

背景知识：
{context}"""),
    ("human", "{question}"),
])


def answer_question(question: str) -> dict:
    docs = similarity_search(question)
    context = "\n\n---\n\n".join(doc.page_content for doc in docs)

    llm = get_llm()
    chain = RAG_PROMPT | llm
    response = chain.invoke({"context": context, "question": question})

    sources = [
        {"content": doc.page_content[:200], "metadata": doc.metadata}
        for doc in docs
    ]

    return {
        "answer": response.content,
        "sources": sources,
    }