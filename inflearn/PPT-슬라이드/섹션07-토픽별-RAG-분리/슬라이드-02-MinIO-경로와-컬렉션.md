# 슬라이드 02: MinIO 경로와 Qdrant 컬렉션

## 슬라이드 내용 (한 장)

**MinIO 토픽별 경로**
• 버킷: `rag-docs` (공통)
• CoinTutor: `raw/cointutor/`
• DrillQuiz: `raw/drillquiz/`
• Ingestion Job이 MINIO_PREFIX 환경변수로 경로 지정, 해당 경로의 파일만 읽기

**Qdrant 컬렉션 (토픽별)**
• `rag_docs_cointutor` — CoinTutor 전용 벡터
• `rag_docs_drillquiz` — DrillQuiz 전용 벡터
• qdrant-collection-init Job에서 생성 (벡터 차원·메트릭은 저장소 YAML 참고)
• 통합 `rag_docs` 사용 권장 안 함

**토픽별 매핑**
• MinIO `raw/cointutor/` → Ingestion → `rag_docs_cointutor`
• MinIO `raw/drillquiz/` → Ingestion → `rag_docs_drillquiz`
• RAG Backend: 토픽별로 해당 컬렉션만 검색하도록 설정

---

## 발표 노트

RAG 스택에서 여러 토픽을 지원하려면 MinIO와 Qdrant 모두에서 경로와 컬렉션을 분리해야 합니다. MinIO는 rag-docs라는 공통 버킷을 쓰지만, 그 안에서 토픽별로 다른 경로를 씁니다. CoinTutor 문서는 raw/cointutor/ 아래에, DrillQuiz 문서는 raw/drillquiz/ 아래에 올립니다.

Ingestion Job이 실행될 때, MINIO_PREFIX 환경변수로 어느 경로의 파일을 읽을지 지정합니다. 예를 들어 CoinTutor용 Ingestion Job은 MINIO_PREFIX=cointutor로 설정해서, raw/cointutor/ 아래의 파일들만 읽어 벡터로 만듭니다.

Qdrant 쪽도 마찬가지입니다. rag_docs_cointutor와 rag_docs_drillquiz 두 개의 컬렉션을 따로 만들어서, 각 토픽의 벡터를 분리해서 저장합니다. qdrant-collection-init Job이 이걸 생성합니다. 벡터 차원이나 유사도 계산 방식(메트릭)은 저장소의 YAML 파일을 참고하면 됩니다.

매핑 관계는 이렇습니다. raw/cointutor의 문서들이 Ingestion을 거쳐서 rag_docs_cointutor 컬렉션에 벡터로 저장되고, raw/drillquiz의 문서들이 rag_docs_drillquiz에 저장됩니다. RAG Backend는 CoinTutor와 DrillQuiz로 구분되어 있고, 각각 해당하는 컬렉션만 검색하도록 설정합니다. 그래서 사용자가 CoinTutor에서 채팅할 때는 CoinTutor 문서에서만 답변을 찾고, DrillQuiz에서 채팅할 때는 DrillQuiz 문서에서만 찾습니다.
