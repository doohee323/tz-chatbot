# 01. ingest.py 흐름

## 역할

- **MinIO** 버킷(`rag-docs`)의 지정 prefix(`raw/cointutor/`, `raw/drillquiz/` 등) 아래 파일을 읽어
- **LangChain**으로 로드·청킹·임베딩한 뒤
- **Qdrant** 컬렉션에 upsert하는 스크립트입니다.
- K8s에서는 **Job/CronJob** 안에서 이 스크립트를 실행합니다 (ConfigMap으로 스크립트·requirements 제공).

## 흐름 요약

1. **환경변수** 읽기: MINIO_*, QDRANT_*, EMBEDDING_PROVIDER, GEMINI_API_KEY(또는 OPENAI_API_KEY), CHUNK_SIZE, CHUNK_OVERLAP, MINIO_PREFIX, QDRANT_COLLECTION 등
2. **MinIO**에서 prefix 아래 객체 목록 조회 → 파일 다운로드
3. **Loader**: 확장자에 따라 PyPDFLoader, TextLoader 등으로 문서 로드 (LangChain)
4. **Splitter**: RecursiveCharacterTextSplitter로 청킹
5. **Embedding**: OpenAI 또는 Gemini 임베딩 모델로 벡터화
6. **Qdrant**: QdrantVectorStore에 upsert (payload에 source, path 등 메타데이터)
7. (선택) **증분**: INCREMENTAL=true면 기존 doc_id·수정 시각과 비교해 변경/삭제만 반영

자세한 LangChain 조합은 다음 파일(02)에서 다룹니다.
