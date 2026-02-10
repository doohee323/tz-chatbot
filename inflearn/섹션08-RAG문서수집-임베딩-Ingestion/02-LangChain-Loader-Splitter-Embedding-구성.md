# 02. LangChain Loader / Splitter / Embedding 구성

## ingest.py 내 LangChain 사용처

### Loader (langchain_community)

- **PyPDFLoader**: PDF 파일
- **TextLoader**: .txt, .md 등 (encoding, autodetect_encoding 지원)
- MinIO에서 받은 바이트를 **임시 파일**로 쓰고, 해당 경로를 로더에 넘김

### Splitter (langchain_text_splitters)

- **RecursiveCharacterTextSplitter**
  - 분리 우선순위: `\n\n` → `\n` → `. ` → ` ` 등
  - **CHUNK_SIZE**, **CHUNK_OVERLAP** 환경변수로 크기·오버랩 조정 (기본 500, 50 등)
  - 문단·문장 경계를 고려해 잘라서 RAG 품질을 높임

### Embedding

- **OpenAIEmbeddings** (langchain-openai): OPENAI_API_KEY, EMBEDDING_MODEL
- **GoogleGenerativeAIEmbeddings** (langchain-google-genai): GEMINI_API_KEY, EMBEDDING_MODEL (예: gemini-embedding-001)
- **EMBEDDING_PROVIDER** 환경변수로 openai | gemini 선택

### VectorStore (langchain_qdrant)

- **QdrantVectorStore**: Qdrant 클라이언트·컬렉션 이름으로 연결, payload에 page_content, metadata(source, path, doc_id 등) 저장

## 의존성 (requirements-ingest.txt)

- langchain-core, langchain-community, langchain-text-splitters, langchain-openai, langchain-google-genai, langchain-qdrant, minio, qdrant-client 등
- Job 이미지 또는 Job 내부에서 `pip install -r requirements-ingest.txt` 후 ingest.py 실행
