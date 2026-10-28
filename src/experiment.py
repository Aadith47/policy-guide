import json

import chromadb

from ingest import BASE_DIR, build_chunks

TEST_FILE = BASE_DIR / "data" / "test_questions.json"
CHUNK_SIZES = (400, 600, 800, 1000)
TOP_K = 3


def load_cases():
    cases = json.loads(TEST_FILE.read_text(encoding="utf-8"))
    # Only cases with an expected page can be judged on retrieval
    return [case for case in cases if case.get("expected_page") is not None]


def hit_rate(max_chars, cases):
    chunks = build_chunks(max_chars=max_chars)

    # In-memory index per size, so the real db folder is never touched
    client = chromadb.EphemeralClient()
    collection = client.create_collection(name=f"size_{max_chars}")
    collection.add(
        ids=[str(chunk.id) for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[{"page": chunk.page} for chunk in chunks],
    )

    hits = 0
    for case in cases:
        result = collection.query(query_texts=[case["question"]], n_results=TOP_K)
        pages = [meta["page"] for meta in result["metadatas"][0]]
        if case["expected_page"] in pages:
            hits += 1

    client.delete_collection(name=f"size_{max_chars}")
    return len(chunks), hits


if __name__ == "__main__":
    cases = load_cases()
    print(f"Top {TOP_K}, {len(cases)} questions with an expected page\n")
    print("chunk size | chunks | right page found")
    for size in CHUNK_SIZES:
        count, hits = hit_rate(size, cases)
        print(f"{size:>10} | {count:>6} | {hits}/{len(cases)}")
