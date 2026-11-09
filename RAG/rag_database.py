import os
import uuid

import requests

try:
    import chromadb  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    chromadb = None


# Project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ChromaDB storage location
CHROMA_PATH = os.path.join(
    PROJECT_ROOT,
    "rag",
    "chroma_db"
)


# Ollama embedding API
OLLAMA_URL = "http://localhost:11434/api/embeddings"

EMBEDDING_MODEL = "nomic-embed-text"


def _require_chromadb():
    if chromadb is None:
        raise RuntimeError(
            "chromadb is not installed. Install it with: pip install chromadb"
        )


_require_chromadb()


# Create ChromaDB client
client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# Create or open our knowledge collection
collection = client.get_or_create_collection(
    name="hr_knowledge_base"
)


def create_embedding(text):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["embedding"]


def store_chunks(documents):

    for document in documents:

        file_name = document["file_name"]

        chunks = document["chunks"]

        for index, chunk in enumerate(chunks):

            embedding = create_embedding(chunk)

            collection.add(
                ids=[str(uuid.uuid4())],

                embeddings=[embedding],

                documents=[chunk],

                metadatas=[{
                    "file_name": file_name,
                    "chunk_index": index
                }]
            )

            print(
                f"Stored: {file_name} | "
                f"Chunk: {index + 1}/{len(chunks)}"
            )


def search_knowledge(question, results=3):

    question_embedding = create_embedding(question)

    result = collection.query(
        query_embeddings=[question_embedding],
        n_results=results
    )

    return result


if __name__ == "__main__":

    print("ChromaDB collection ready!")

    print(
        "Collection:",
        collection.name
    )

    print(
        "Existing chunks:",
        collection.count()
    )