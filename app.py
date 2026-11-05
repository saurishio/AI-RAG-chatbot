import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from rag import retrieve

from rag import collection

if collection.count() == 0:
    import ingest
    ingest.main()

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the context does not contain the answer, say you "
    "don't know based on the documents. Do not invent facts."
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a message."}), 400

    try:
        hits = retrieve(message, k=4)

        if hits:
            context = "\n\n".join(
                f"[{i + 1}] (source: {h['source']})\n{h['text']}"
                for i, h in enumerate(hits)
            )
        else:
            context = "No relevant documents found."

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=f"Context:\n{context}\n\nQuestion: {message}",
        )

        return jsonify({
            "reply": response.output_text,
            "sources": sorted({h["source"] for h in hits}),
        })

    except Exception:
        app.logger.exception("Error generating AI response")
        return jsonify({
            "error": "Unable to generate a response. Check the VS Code terminal."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)