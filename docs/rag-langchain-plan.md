# RAG LangChain 도입 계획

## 1. 목표

- **청킹 품질 개선**: 문자 수 기반 단순 슬라이싱 → LangChain `RecursiveCharacterTextSplitter`로 문맥 경계 존중
- **일괄 프로비저닝·배포 통합**: `bootstrap.sh` → `install.sh` → RAG Job/CronJob까지 기존 흐름 유지
- **호환성 유지**: MinIO/Qdrant/OpenAI/Gemini 파이프라인 동일, 기존 컬렉션 스키마 유지

---

## 2. 현재 구조 요약

| 구성요소 | 경로 | 역할 |
|---------|------|------|
| 인제스트 스크립트 | `rag/scripts/ingest.py` | MinIO raw/ → chunk → embed → Qdrant upsert |
| 의존성 | pip (Job 내부) | minio, qdrant-client, openai, pypdf, google-genai |
| ConfigMap | `rag-ingestion-script` | ingest.py 마운트 |
| CronJob | cointutor, drillquiz | MINIO_PREFIX, QDRANT_COLLECTION별 분리 |

**한계**:
- `chunk_text()`: 문자 단위 고정 슬라이스, 문장/단락 경계 무시
- full sync: 컬렉션 삭제 후 전체 재생성

---

## 3. LangChain 도입 범위

### 3.1 Phase 1 (적용 완료)

- **Loader**: `PyPDFLoader`, `TextLoader` (langchain_community) — MinIO 바이트 → 임시 파일 → 로더
- **Splitter**: `RecursiveCharacterTextSplitter` (langchain_text_splitters)
  - 기본 분리 순서: `\n\n` → `\n` → `. ` → ` ` → ``
  - CHUNK_SIZE, CHUNK_OVERLAP 환경변수 계속 사용
- **Embedding**: `OpenAIEmbeddings`, `GoogleGenerativeAIEmbeddings` (langchain-openai, langchain-google-genai)
- **VectorStore**: QdrantVectorStore (langchain-qdrant), payload: page_content, metadata{source, path, ...}
- **의존성**: langchain-core, langchain-community, langchain-text-splitters, langchain-openai, langchain-google-genai, langchain-qdrant

**주의**: VectorStore 적용 후 기존 컬렉션은 재인덱싱 필요. Job 실행으로 다시 인덱싱 후 백엔드 사용.

### 3.2 Phase 2 (적용 완료)

- 증분 인덱싱: doc_id + created_at 기반 변경 감지. 변경/삭제된 문서만 갱신. `INCREMENTAL=true` (기본)
- 하이브리드 검색: BM25 + 벡터 재랭킹

---

## 4. 통합 프로비저닝 흐름

```
bootstrap.sh
  → install_ingress
  → install_minio
  → install_rag  ──→ rag/install.sh
  │                   → Qdrant, collections, backend, frontend
  │                   → ConfigMap (ingest.py + requirements-ingest.txt)
  │                   → CronJob (cointutor, drillquiz)
  → install_dify
```

- **일괄성**: `./bootstrap.sh` 한 번으로 Ingress → MinIO → RAG → Dify 순차 배포
- **LangChain 반영**: `rag/install.sh`가 ConfigMap에 `ingest.py`, `requirements-ingest.txt` 포함, Job/CronJob에서 `pip install -r` 사용

---

## 5. 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `rag/scripts/ingest.py` | `chunk_text` → `RecursiveCharacterTextSplitter` |
| `rag/requirements-ingest.txt` | 신규, pip 의존성 명시 |
| `rag/install.sh` | ConfigMap에 requirements-ingest.txt 추가 |
| `rag/rag-ingestion-job.yaml` | pip install -r 사용 |
| `rag/cointutor/rag-ingestion-job-cointutor.yaml` | 동일 |
| `rag/cointutor/rag-ingestion-cronjob-cointutor.yaml` | 동일 |
| `rag/drillquiz/rag-ingestion-job-drillquiz.yaml` | 동일 |
| `rag/drillquiz/rag-ingestion-cronjob-drillquiz.yaml` | 동일 |
| `rag/Dockerfile.ingest` | (선택) 미리 빌드된 이미지용, pip 생략으로 CronJob 시작 속도 향상 |

---

## 6. 환경변수 (기존 유지)

| 변수 | 설명 | 기본값 |
|------|------|--------|
| CHUNK_SIZE | 청크 최대 문자 수 | 500 |
| CHUNK_OVERLAP | 청크 간 겹침 | 50 |
| EMBEDDING_PROVIDER | openai \| gemini | openai |
| EMBEDDING_MODEL | 모델명 | text-embedding-3-small / gemini-embedding-001 |
