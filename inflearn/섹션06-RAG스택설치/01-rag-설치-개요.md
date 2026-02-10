# 01. RAG 설치 개요

## RAG 스택이란

- **Qdrant**: 벡터 DB (RAG 컬렉션)
- **RAG Backend**: 검색 API (토픽별 Deployment: CoinTutor, DrillQuiz)
- **RAG Frontend**: 정적 UI (선택)
- **RAG Ingestion**: Job/CronJob — MinIO 문서 → 청킹·임베딩 → Qdrant
- **Ingress**: RAG·RAG-UI 도메인 라우팅 (install.sh에서 도메인 치환)

## 설치 진입점

- **rag/install.sh**: RAG 관련만 설치 (Qdrant, Backend, Frontend, Ingestion, Ingress)
- **bootstrap.sh**: Ingress NGINX → MinIO → **RAG(install.sh 호출)** → Dify 순으로 전체 설치

## 설치 후 필수

- **토픽별 Secret** 생성: `rag-ingestion-secret-cointutor`, `rag-ingestion-secret-drillquiz`
  - MinIO 접근 키, Gemini(또는 OpenAI) API Key
  - 없으면 RAG Backend Pod가 기동하지 않거나 검색 시 "API key not valid" 오류 가능
- **Qdrant 컬렉션**: install.sh에 포함된 qdrant-collection-init Job으로 `rag_docs_cointutor`, `rag_docs_drillquiz` 생성

다음 파일에서 install.sh 실행·Secret 생성·검증을 단계별로 다룹니다.
