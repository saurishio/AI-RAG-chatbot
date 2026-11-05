# AI RAG Chatbot

A retrieval-augmented generation (RAG) chatbot that answers questions **only from your own documents**. Drop PDFs, Markdown or text files into a folder, and chat with them through a simple web interface. Every answer comes with the source files it was drawn from, and the bot says "I don't know" instead of making things up.

Built with **Flask**, **ChromaDB** and the **Groq API** (via the OpenAI-compatible SDK).

<!-- Add a screenshot or GIF here: ![Demo](static/demo.png) -->

## Features

- **Chat with your documents**: supports `.pdf`, `.md` and `.txt` files
- **Grounded answers**: the model is instructed to answer strictly from retrieved context and to decline when the documents don't contain the answer
- **Source attribution**: each reply lists the files used to produce it
- **Vector search**: documents are split into overlapping chunks and stored in a persistent ChromaDB collection using cosine similarity
- **Safe re-ingestion**: re-running ingestion replaces a file's old chunks, so you never get stale or duplicate data
- **Auto-ingest on first run**: if the vector store is empty at startup, the app indexes everything in `docs/` automatically
- **Production-ready server**: Gunicorn included for deployment

## How it works

```
 docs/ (PDF, MD, TXT)
        │
        ▼
   ingest.py ── extract text → chunk (800 chars, 150 overlap) → ChromaDB
                                                                   │
 User question ──► Flask /chat ──► rag.py: top-4 similar chunks ◄──┘
                                        │
                                        ▼
                     Prompt = system rules + retrieved context + question
                                        │
                                        ▼
                         Groq LLM (openai/gpt-oss-20b)
                                        │
                                        ▼
                         Answer + list of source files
```

1. **Ingest**: `ingest.py` reads each file in `docs/`, normalizes whitespace, and splits the text into 800-character chunks with a 150-character overlap so context isn't lost at chunk boundaries. Chunks are upserted into ChromaDB with their source filename.
2. **Retrieve**: `rag.py` queries the collection for the 4 most similar chunks (cosine distance). ChromaDB handles embedding with its default embedding function.
3. **Generate**: `app.py` builds a prompt from the retrieved chunks and sends it to the Groq-hosted model with a strict system prompt: use only the provided context, and say so if the answer isn't there.
4. **Respond**: the API returns the answer plus the sorted list of source files.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, Flask, Gunicorn |
| Vector database | ChromaDB (persistent, cosine similarity) |
| LLM | Groq API (`openai/gpt-oss-20b`) via the OpenAI Python SDK |
| Document parsing | pypdf |
| Config | python-dotenv |
| Frontend | HTML templates + static assets |

## Project structure

```
AI-RAG-chatbot/
├── app.py            # Flask app: routes, prompt building, LLM call
├── rag.py            # ChromaDB client, collection and retrieval function
├── ingest.py         # Document loading, chunking and indexing
├── docs/             # Put your PDF / MD / TXT files here
├── templates/        # HTML templates (chat UI)
├── static/           # CSS / JS assets
├── requirements.txt
└── chroma_db/        # Vector store, created automatically on first run
```

## Getting started

### Prerequisites

- Python 3.9+
- A free [Groq API key](https://console.groq.com/keys)

### 1. Clone the repository

```bash
git clone https://github.com/saurishio/AI-RAG-chatbot.git
cd AI-RAG-chatbot
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
FLASK_SECRET_KEY=any_long_random_string
```

### 4. Add your documents

Place your `.pdf`, `.md` or `.txt` files in the `docs/` folder.

### 5. Index the documents (optional)

```bash
python ingest.py
```

This step is optional on a fresh setup because the app indexes `docs/` automatically if the vector store is empty. Run it manually whenever you add or change documents after the first run.

### 6. Start the app

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser and start asking questions.

For production, use Gunicorn instead of the Flask development server:

```bash
gunicorn app:app
```

## API reference

### `POST /chat`

Send a question and get a grounded answer.

**Request**

```json
{ "message": "What does the document say about refund policy?" }
```

**Response**

```json
{
  "reply": "According to the documents, ...",
  "sources": ["policy.pdf"]
}
```

**Errors**

| Status | Meaning |
|---|---|
| `400` | Empty or invalid message |
| `500` | Failed to generate a response (check the server logs) |

## Configuration

| Setting | Where | Default |
|---|---|---|
| Chunk size | `ingest.py` → `CHUNK_SIZE` | 800 characters |
| Chunk overlap | `ingest.py` → `OVERLAP` | 150 characters |
| Passages retrieved | `rag.py` → `retrieve(k=...)` | 4 |
| LLM model | `app.py` → `MODEL` | `openai/gpt-oss-20b` |
| Vector store location | `rag.py` → `PersistentClient(path=...)` | `chroma_db/` |

Tip: smaller chunks give more precise matches, larger chunks give more context per match. Tune `CHUNK_SIZE` and `k` for your documents.

## Limitations and ideas for improvement

- Answers are only as good as the documents provided; scanned PDFs without a text layer won't be readable
- No conversation memory yet: each question is answered independently
- Possible next steps: chat history, streaming responses, a re-ranking step, support for `.docx` files, and a document upload button in the UI

## License

This project is licensed under the [MIT License](LICENSE).

## Author

**Saurish Chanda** · [GitHub](https://github.com/saurishio)
