from pathlib import Path
from pypdf import PdfReader
from rag import collection

DOCS_DIR = Path("docs")
CHUNK_SIZE = 800
OVERLAP = 150


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def chunk_text(text: str):
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - OVERLAP
    return chunks


def main():
    for path in sorted(DOCS_DIR.iterdir()):
        if path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue

        chunks = chunk_text(read_file(path))
        if not chunks:
            continue

        # remove old chunks for this file so re-running doesn't leave stale data
        collection.delete(where={"source": path.name})
        collection.upsert(
            ids=[f"{path.name}-{i}" for i in range(len(chunks))],
            documents=chunks,
            metadatas=[{"source": path.name, "chunk": i} for i in range(len(chunks))],
        )
        print(f"Ingested {path.name}: {len(chunks)} chunks")


if __name__ == "__main__":
    main()