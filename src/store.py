import chromadb

from ingest import build_chunks

DB_PATH = "db"
COLLECTION_NAME = "handbook"


def get_collection():
    # Build and search share this function so both use the same embedder.
    # Chroma's default embedder is all-MiniLM-L6-v2 (free, runs on your CPU).
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def build_index():
    collection = get_collection()
    chunks = build_chunks()
    # upsert, not add, so running the script twice does not crash on old ids
    collection.upsert(
        ids=[str(chunk.id) for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[{"page": chunk.page} for chunk in chunks],
    )
    return len(chunks)


if __name__ == "__main__":
    print(f"Indexed {build_index()} chunks")