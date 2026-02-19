# Chat Inference (Dify-free)

Classifier + RAG + LLM pipeline. **Uses same Qdrant (Dify's DB)** via RAG Backend API. No Dify for inference.

## Flow

1. **Question Classifier** (LLM): 3-way → `after_sales`, `products`, `other`
2. **Knowledge Retrieval**: RAG Backend POST /query → Qdrant (same DB Dify uses)
3. **LLM** (Gemini): context + prompt → answer
4. **Other branch**: fixed "Sorry, I can't help with these questions."

## Config

Copy `.env.example` → `.env` and set:

- `GEMINI_API_KEY`: Gemini API key (same as Dify)
- `RAG_BACKEND_URL`: RAG Backend URL (queries Qdrant)
  - K8s: `http://rag-backend.rag.svc.cluster.local:8000`
  - Local: `http://localhost:8000` (port-forward rag-backend)

## Run

```bash
./run.sh   # port 8090
```

## chat-gateway

Set `CHAT_INFERENCE_URL=http://chat-inference:8090` (K8s) or `http://localhost:8090` (local) in chat-gateway `.env`. Then `/v1/chat` calls chat-inference instead of Dify.

## Note

- **/conversations**, **/conversations/:id/messages**: chat-inference does not store them; chat-gateway still uses Dify for these if configured. For full Dify-free, add conversation storage to chat-inference or another service.
