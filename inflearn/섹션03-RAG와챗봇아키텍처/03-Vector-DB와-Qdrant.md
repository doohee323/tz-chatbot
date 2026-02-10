# 03. Vector DB와 Qdrant

## Vector DB란

- **벡터(임베딩)** 를 저장하고, “이 벡터와 유사한 벡터들”을 **빠르게 검색**하는 DB
- 일반 RDB의 “키·인덱스 검색”이 아니라 “**유사도 검색**”(ANN, approximate nearest neighbor)에 최적화

## Qdrant

- 오픈소스 **벡터 DB**. tz-chatbot에서는 **K8s에 Helm으로** 설치하며, `rag` 네임스페이스에서 동작
- **컬렉션(collection)**: 토픽별로 구분 (예: `rag_docs_cointutor`, `rag_docs_drillquiz`)
- 벡터 차원·거리 메트릭(코사인 등)을 컬렉션 생성 시 지정
- RAG Backend·Ingestion 스크립트가 Qdrant API로 **upsert·search** 수행

## tz-chatbot에서의 역할

- **Ingestion**: MinIO에서 문서 읽기 → 청킹·임베딩 → Qdrant 컬렉션에 **upsert**
- **RAG Backend**: 사용자 질의 임베딩 → Qdrant에서 **search** → 상위 k개 청크 반환 → Dify에 전달
- 토픽별로 **컬렉션을 나누어** CoinTutor/DrillQuiz 검색이 서로 섞이지 않도록 함 (섹션 07).
