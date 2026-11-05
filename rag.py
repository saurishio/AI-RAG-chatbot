import chromadb

_client = chromadb.PersistentClient(path="chroma_db")
collection = _client.get_or_create_collection(
    name="docs",
    metadata={"hnsw:space": "cosine"},
)


def retrieve(query: str, k: int = 4):
    res = collection.query(query_texts=[query], n_results=k)
    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({"text": doc, "source": meta["source"], "distance": dist})
    return hits