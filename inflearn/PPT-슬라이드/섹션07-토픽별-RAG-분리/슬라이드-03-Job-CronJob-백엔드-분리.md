# 슬라이드 03: Job / CronJob / 백엔드 분리

## 슬라이드 내용 (한 장)

**RAG Ingestion Job/CronJob**
• 토픽별 Job: `rag-ingestion-cointutor`, `rag-ingestion-drillquiz`
• CronJob: 정기적으로 재색인 (예: 매일 자정)
• MinIO prefix → LangChain → Qdrant 자동 처리

**RAG Backend Deployment (토픽별)**
• `rag-backend` (기본, 또는 `rag-backend-cointutor`)
• `rag-backend-drillquiz`
• 각각 해당하는 Qdrant 컬렉션만 검색하도록 환경변수 설정

**Dify 도구 연동**
• chat-gateway의 Dify 앱에서 토픽별 RAG Backend URL 지정
• `/query` 엔드포인트로 검색 API 호출
• 섹션09에서 상세히 설정

---

## 발표 노트

RAG Ingestion은 Job과 CronJob으로 관리합니다. Job은 일회성 작업이고, CronJob은 정기적으로 같은 작업을 반복합니다. 토픽별로 다른 Job을 만들어서, rag-ingestion-cointutor는 CoinTutor 문서를, rag-ingestion-drillquiz는 DrillQuiz 문서를 각각 처리합니다. CronJob을 설정하면 매일 자정에 자동으로 문서를 다시 임베딩해서 Qdrant에 업데이트할 수 있습니다.

Job/CronJob이 실행될 때는 MinIO에서 토픽별 prefix 경로에 있는 파일들을 읽고, LangChain을 써서 로드·청킹·임베딩한 뒤 Qdrant에 저장합니다. 이 모든 과정이 자동으로 진행됩니다.

RAG Backend Deployment도 토픽별로 분리됩니다. rag-backend는 기본이고, rag-backend-drillquiz 같은 별도 Deployment를 만들 수도 있습니다. 각 Backend는 환경변수로 어느 Qdrant 컬렉션을 쓸지 지정합니다. 예를 들어 rag-backend-drillquiz는 QDRANT_COLLECTION=rag_docs_drillquiz으로 설정해서, rag_docs_drillquiz 컬렉션하고만 검색합니다.

Dify 도구 연동은 섹션09에서 상세히 다루는데, chat-gateway가 사용하는 Dify 앱에서 각 토픽별로 RAG Backend URL을 지정합니다. Dify가 필요할 때 해당 Backend의 /query 엔드포인트를 호출해서 검색 결과를 받습니다.
