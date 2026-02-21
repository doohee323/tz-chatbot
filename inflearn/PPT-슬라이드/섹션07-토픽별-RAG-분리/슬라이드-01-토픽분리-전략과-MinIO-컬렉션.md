# 슬라이드 01: 토픽 분리 전략과 MinIO·컬렉션

## 슬라이드 내용 (한 장)

**왜 토픽을 나누는가**  
• CoinTutor와 DrillQuiz는 지식 베이스·용도가 다름. 한 컬렉션에 섞이면 검색 시 무관한 문서 포함·앱별 지식 구분 어려움 → **토픽별 MinIO 경로·Qdrant 컬렉션·RAG Backend·Ingestion 분리**

**분리 전략 요약 (docs/rag-multi-topic)**

| 항목 | CoinTutor | DrillQuiz |
|------|-----------|-----------|
| MinIO 경로 | rag-docs/raw/cointutor/ | rag-docs/raw/drillquiz/ |
| Qdrant 컬렉션 | rag_docs_cointutor | rag_docs_drillquiz |
| Ingestion Job/CronJob | MINIO_PREFIX·QDRANT_COLLECTION 별도 YAML | 동일 |
| RAG Backend | rag-backend (Deployment) | rag-backend-drillquiz |
| Dify 도구 URL | Backend Service URL (CoinTutor) | Backend Service URL (DrillQuiz) |

• 한 버킷(rag-docs) 안 경로만 나누고, 컬렉션·Backend는 토픽별 완전 분리. Job/CronJob은 같은 ingest.py·ConfigMap, 환경변수만 토픽별로 다름. **전체 재색인**: `*-full` CronJob(rag-ingestion-cronjob-cointutor-full, -drillquiz-full)에서 Job 생성.

---

## 발표 노트

CoinTutor와 DrillQuiz는 서로 다른 지식 베이스와 용도를 가집니다. 한 컬렉션에 다 넣으면 검색할 때 서로 무관한 문서가 나올 수 있고, Dify 앱별로 “어떤 지식만 쓸지” 구분하기 어렵습니다. 그래서 토픽별로 MinIO 경로, Qdrant 컬렉션, RAG Backend, Ingestion을 분리합니다.

분리 전략은 docs/rag-multi-topic에 정리되어 있습니다. MinIO는 한 버킷 rag-docs를 쓰고, 그 안에 raw/cointutor, raw/drillquiz처럼 토픽별 경로만 둡니다. Qdrant 컬렉션은 rag_docs_cointutor, rag_docs_drillquiz로 완전히 나누고, 기존 rag_docs 통합 컬렉션은 쓰지 않는 걸 권장합니다. Ingestion은 Job과 CronJob을 토픽별 YAML로 두고, MINIO_PREFIX와 QDRANT_COLLECTION 환경변수만 다르게 줍니다. RAG Backend도 Deployment를 두 개 두고, 하나는 CoinTutor용 rag-backend, 하나는 DrillQuiz용 rag-backend-drillquiz입니다. Dify에서는 앱별로 RAG 도구 URL을 해당 Backend Service 주소로 설정합니다. 한 버킷 안에서 경로만 나누고, 컬렉션과 Backend는 토픽별로 완전 분리하는 방식입니다. Job과 CronJob은 같은 ingest.py와 ConfigMap을 쓰고, 환경변수만 토픽에 맞게 다르게 넣습니다.
