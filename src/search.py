from store import get_collection

TOP_K = 5


def search(question, top_k=TOP_K):
    result = get_collection().query(query_texts=[question], n_results=top_k)

    # Chroma returns one list per question, we only sent one, so take [0]
    hits = []
    for text, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append({"text": text, "page": meta["page"], "distance": distance})
    return hits


if __name__ == "__main__":
    question = input("Ask a policy question: ")
    for hit in search(question):
        print(f"\npage {hit['page']} | distance {hit['distance']:.3f}")
        print(hit["text"][:300])