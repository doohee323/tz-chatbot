# tz-chatbot

This repository sets up a **RAG (Retrieval-Augmented Generation)** and **Dify chatbot** demo environment on Kubernetes. It installs, in order: Ingress NGINX, MinIO, Qdrant, topic-specific RAG backends (CoinTutor / DrillQuiz), and Dify.

## Usage

**Prerequisite**: A Kubernetes cluster and `kubectl` (or `KUBECONFIG`) must be available.

```bash
# Set KUBECONFIG if needed
export KUBECONFIG=~/.kube/your-config

# Install everything (existing components are skipped)
./bootstrap.sh
```

### Database setup (chat-admin / chat-gateway)

chat-admin and chat-gateway share the same PostgreSQL database `chat_admin`. The database must exist before the apps start.

```bash
# Get password from chat-admin Secret (same password the app uses)
DB_PASS=$(kubectl -n devops get secret chat-admin-secret-main -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d)
echo "Password length: ${#DB_PASS}"

# Create chat_admin database
kubectl exec -n devops devops-postgres-postgresql-0 -- env PGPASSWORD="$DB_PASS" psql -U postgres -c "CREATE DATABASE chat_admin;"
```

Use `chat-admin-secret-main` (or `chat-admin-secret-{branch}` for dev/qa) so the password matches what the app uses. For `devops-dev` namespace, replace `devops` with `devops-dev`.

Install order: **Ingress NGINX** → **MinIO** → **RAG stack** → **Dify**.  
After install, create `rag-ingestion-secret-cointutor` and `rag-ingestion-secret-drillquiz` (MinIO, Gemini, etc.) for the RAG Backend to start. See `rag/README.md` and `docs/rag-multi-topic.md` for steps and checklists.

## Documentation

- `docs/rag-multi-topic.md` — Topic-based RAG separation (CoinTutor/DrillQuiz), MinIO paths, Dify tool URLs
- `docs/rag-requirements-and-plan.md` — Requirements and phase-by-phase execution plan
- `docs/additional-requirements.md` — Scale, control, traffic, iframe auth, tracking, F/U, and other operational considerations
- `docs/dify-drillquiz-embed-and-tracking.md` — DrillQuiz + Dify chat: user identity, tracking, F/U (embed / API proxy)
