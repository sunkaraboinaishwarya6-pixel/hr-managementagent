import os
from pypdf import PdfReader

from rag_database import store_chunks


HR_DOCUMENTS = "../sample_data/hr_documents"
PAPERS = "../sample_data/knowledge_base/papers"


def read_pdf(file_path):
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def load_documents(folder):
    documents = []

    for filename in os.listdir(folder):

        if filename.lower().endswith(".pdf"):

            file_path = os.path.join(folder, filename)

            text = read_pdf(file_path)

            documents.append({
                "file_name": filename,
                "text": text
            })

    return documents


def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def prepare_documents(documents):
    prepared_documents = []

    for document in documents:

        chunks = chunk_text(document["text"])

        prepared_documents.append({
            "file_name": document["file_name"],
            "chunks": chunks
        })

    return prepared_documents


if __name__ == "__main__":

    print("Loading HR documents...")

    hr_docs = load_documents(HR_DOCUMENTS)

    print("Loading research papers...")

    papers = load_documents(PAPERS)

    print("\nHR Documents:", len(hr_docs))
    print("Research Papers:", len(papers))

    print("\nCreating chunks...")

    hr_chunks = prepare_documents(hr_docs)
    paper_chunks = prepare_documents(papers)

    all_documents = hr_chunks + paper_chunks

    total_chunks = sum(
        len(document["chunks"])
        for document in all_documents
    )

    print("Total chunks:", total_chunks)

    print("\nCreating embeddings and storing in ChromaDB...")

    store_chunks(all_documents)

    print("\nRAG knowledge base created successfully!")