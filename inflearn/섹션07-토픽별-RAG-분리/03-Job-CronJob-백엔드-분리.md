# 03. Job / CronJob / Backend 분리

## Job (수동 1회 실행)

- **CoinTutor**: `rag-ingestion-job-cointutor.yaml` → Job 이름 예: `rag-ingestion-job-cointutor`
- **DrillQuiz**: `rag-ingestion-job-drillquiz.yaml` → Job 이름 예: `rag-ingestion-job-drillquiz`
- 각 Job은 **MINIO_PREFIX**, **QDRANT_COLLECTION** 환경변수로 토픽을 구분하고, 같은 ingest.py·ConfigMap을 사용합니다.

## CronJob (주기 실행)

- **CoinTutor**: `rag-ingestion-cronjob-cointutor.yaml` (예: 매일 02:00)
- **DrillQuiz**: `rag-ingestion-cronjob-drillquiz.yaml` (예: 매일 02:30)
- CronJob에서 한 번 실행하려면:  
  `kubectl create job -n rag ingest-cointutor-1 --from=cronjob/rag-ingestion-cronjob-cointutor`

## Backend 분리

- **rag-backend** (Deployment): CoinTutor — 환경변수로 **QDRANT_COLLECTION=rag_docs_cointutor**
- **rag-backend-drillquiz** (Deployment): DrillQuiz — **QDRANT_COLLECTION=rag_docs_drillquiz**
- Dify에서는 앱별로 “RAG 도구 URL”을 각 Backend Service 주소로 설정합니다  
  (예: `http://rag-backend.rag.svc.cluster.local:8000/query`, `http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query`).

이렇게 Job/CronJob/Backend를 토픽별로 분리해 두면, 문서 추가·재색인도 토픽 단위로 안전하게 할 수 있습니다.
