import os
from typing import List, Tuple

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import GEMINI_API_KEY, CHAT_MODEL, EMBEDDING_MODEL, VECTORSTORE_DIR


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY,
    )


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
    )


def load_vectorstore() -> FAISS:
    if not os.path.exists(VECTORSTORE_DIR):
        raise FileNotFoundError(
            "Vector store not found. Run ingest.py first to index your PDFs."
        )

    embeddings = get_embeddings()
    return FAISS.load_local(
        VECTORSTORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def clean_page_number(doc: Document) -> int:
    """
    PyPDFLoader page metadata is usually zero-based.
    Convert it to human-readable page numbers.
    """
    return int(doc.metadata.get("page", 0)) + 1


def deduplicate_docs(docs: List[Document]) -> List[Document]:
    seen = set()
    unique_docs = []

    for doc in docs:
        key = (
            doc.metadata.get("source", ""),
            doc.metadata.get("page", ""),
            doc.page_content.strip()[:120],
        )
        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    return unique_docs


def format_context(docs: List[Document]) -> str:
    blocks = []

    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        page = clean_page_number(doc)
        text = doc.page_content.strip()

        blocks.append(
            f"[Chunk {i}] Source: {source} | Page: {page}\n{text}"
        )

    return "\n\n".join(blocks)


def format_page_list(docs: List[Document]) -> str:
    pages = sorted({clean_page_number(doc) for doc in docs})
    return " | ".join([f"page {p}" for p in pages])


def ask_pdf(question: str, k: int = 3) -> Tuple[str, str]:
    """
    Retrieve relevant chunks with MMR, answer from context,
    and return a clean page list.
    """
    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 12},
    )

    docs = retriever.invoke(question)
    docs = deduplicate_docs(docs)

    if not docs:
        return "I could not find that in the PDF.", ""

    context = format_context(docs)

    prompt = f"""
You are a PDF question-answering assistant.

Use the retrieved context below to answer the user's question.

Rules:
- Answer using the retrieved context.
- If the context is relevant but split across multiple chunks, combine it into one clear answer.
- Prefer a natural, direct answer instead of saying "not found" too quickly.
- Only say "I could not find that in the PDF." if the retrieved context is clearly unrelated.
- If the user asks for "one line", answer in one concise sentence.
- Do not mention chunk numbers.
- Do not copy long raw text from the PDF.
- Keep the answer clean and human-readable.

Retrieved context:
{context}

User question:
{question}
"""

    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    pages = format_page_list(docs)
    return answer.strip(), pages
