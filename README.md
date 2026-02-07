# tz-chatbot

This repository sets up a **RAG (Retrieval-Augmented Generation)** and **Dify chatbot** demo environment on Kubernetes. It installs, in order: Ingress NGINX, MinIO, Qdrant, topic-specific RAG backends (CoinTutor / DrillQuiz), Dify, and TZ-Chat services.

## Project structure

| Directory | Description |
|-----------|-------------|
| `chat-admin/` | Admin UI (Vue + FastAPI): system CRUD, chat lookup, RAG file upload. Registers apps and issues JWT for chat. |
| `chat-gateway/` | Chat API gateway: proxies to Dify, manages conversations. Serves `/chat`, `/v1/chat`, `/v1/conversations`. |
| `rag/` | RAG stack: Qdrant, ingestion jobs, RAG backends (CoinTutor, DrillQuiz). |
| `dify/` | Dify Helm chart and app configs (DrillQuiz, CoinTutor). |
| `ingress-nginx/` | NGINX Ingress Controller, cert-manager, TLS. |
| `minio/` | MinIO for RAG document storage. |
| `docs/` | Design docs, integration guides. |

Flow: **Client app (DrillQuiz/CoinTutor)** → **chat-gateway** → **Dify** → **RAG Backend** → Qdrant/MinIO.

## Usage

**Prerequisite**: A Kubernetes cluster and `kubectl` (or `KUBECONFIG`) must be available.

```bash
# Set KUBECONFIG if needed
export KUBECONFIG=~/.kube/your-config

# Install everything (existing components are skipped)
./bootstrap.sh
```

### Install order

1. **Ingress NGINX** (default NS) — TLS routing for all services
2. **MinIO** (`devops` NS) — object store, `rag-docs` bucket
3. **RAG stack** (`rag` NS) — Qdrant, RAG backends, ingestion CronJobs
4. **Dify** (`dify` NS) — chatbot, RAG tool integration

chat-admin and chat-gateway are deployed separately (Jenkins/CI or `ci/k8s.sh`). They are not installed by `bootstrap.sh`.

### After install

| Component | Namespace | Notes |
|-----------|-----------|-------|
| Ingress NGINX | default | cert-manager for TLS |
| MinIO | devops | Create `rag-docs` bucket via console or minio-bucket-job |
| RAG | rag | Qdrant, rag-backend, rag-backend-drillquiz, CronJobs |
| Dify | dify | Configure tool URLs in Web UI for RAG |
| chat-admin | devops | Admin UI, system management |
| chat-gateway | devops | Chat API, `/chat` page |

**Required secrets** (or RAG Backend Pods fail): `rag-ingestion-secret-cointutor`, `rag-ingestion-secret-drillquiz`. See `rag/README.md` and `docs/rag-multi-topic.md`.

### Database setup (chat-admin / chat-gateway)

chat-admin and chat-gateway share the same PostgreSQL database `chat_admin`. The database must exist before the apps start.

```bash
# Get password from chat-admin Secret (same password the app uses)
DB_PASS=$(kubectl -n devops get secret chat-admin-secret-main -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d)
echo "Password length: ${#DB_PASS}"

# Create chat_admin database
kubectl exec -n devops devops-postgres-postgresql-0 -- env PGPASSWORD="$DB_PASS" psql -U postgres -c "CREATE DATABASE chat_admin;"
```

Use `chat-admin-secret-main` (or `chat-admin-secret-{branch}` for dev/qa) so the password matches. For `devops-dev` namespace, replace `devops` with `devops-dev`.

### Branches and namespaces

| Branch | Namespace | Secret suffix |
|--------|-----------|---------------|
| main | devops | `-main` |
| qa | devops (or devops-qa) | `-qa` |
| dev | devops-dev | `-dev` |

## Sub-project docs

- [chat-admin/README.md](chat-admin/README.md) — Admin UI, local run, env vars
- [chat-gateway/README.md](chat-gateway/README.md) — Chat API gateway, integration
- [rag/README.md](rag/README.md) — RAG install, ingestion, secrets
- [dify/README.md](dify/README.md) — Dify install

## Documentation

- `docs/rag-multi-topic.md` — Topic-based RAG separation (CoinTutor/DrillQuiz), MinIO paths, Dify tool URLs
- `docs/rag-requirements-and-plan.md` — Requirements and phase-by-phase execution plan
- `docs/additional-requirements.md` — Scale, control, traffic, iframe auth, tracking, F/U
- `docs/dify-drillquiz-embed-and-tracking.md` — DrillQuiz + Dify: user identity, tracking, embed / API proxy
- `docs/chat-admin-cointutor-integration.md` — CoinTutor + chat-admin integration
- `docs/chat-gateway-cointutor-integration.md` — CoinTutor + chat-gateway integration
