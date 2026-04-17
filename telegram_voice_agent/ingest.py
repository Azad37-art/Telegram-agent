import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from app.config import GEMINI_API_KEY, EMBEDDING_MODEL, DOCS_DIR, VECTORSTORE_DIR
from app.utils import ensure_dir


def load_all_pdfs(docs_dir: str):
    documents = []

    pdf_files = list(Path(docs_dir).glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {docs_dir}")

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        # Add cleaner source metadata
        for doc in docs:
            doc.metadata["source"] = os.path.basename(pdf_path)

        documents.extend(docs)

    return documents


def main():
    ensure_dir(DOCS_DIR)
    ensure_dir(VECTORSTORE_DIR)

    print("Loading PDFs...")
    documents = load_all_pdfs(DOCS_DIR)
    print(f"Loaded {len(documents)} page-level documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY,
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_DIR)

    print(f"Vector store saved to: {VECTORSTORE_DIR}")


if __name__ == "__main__":
    main()