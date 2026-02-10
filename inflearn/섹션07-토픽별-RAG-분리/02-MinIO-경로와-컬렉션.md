# 02. MinIO 경로와 컬렉션

## MinIO 경로

- **버킷**: `rag-docs` (공통)
- **토픽별 prefix**:
  - CoinTutor: `raw/cointutor/`
  - DrillQuiz: `raw/drillquiz/`
- Ingestion Job/CronJob은 **MINIO_PREFIX** 환경변수로 이 경로를 지정하고, 해당 prefix 아래 파일만 읽어 Qdrant에 넣습니다.

## Qdrant 컬렉션

- **rag_docs_cointutor**: CoinTutor 전용 벡터
- **rag_docs_drillquiz**: DrillQuiz 전용 벡터
- 컬렉션 생성은 qdrant-collection-init Job에서 수행 (벡터 차원·거리 메트릭은 저장소 YAML 참고).
- **기존 `rag_docs`** (통합)는 사용하지 않고, 위 두 컬렉션만 사용하는 것을 권장합니다 (docs/rag-multi-topic).

## 매핑

- MinIO `raw/cointutor/` → Ingestion → **rag_docs_cointutor**
- MinIO `raw/drillquiz/` → Ingestion → **rag_docs_drillquiz**
- RAG Backend CoinTutor는 **rag_docs_cointutor**만 검색, DrillQuiz Backend는 **rag_docs_drillquiz**만 검색하도록 설정됩니다.
