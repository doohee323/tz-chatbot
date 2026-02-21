# 슬라이드 02: LangChain Loader / Splitter / Embedding

## 슬라이드 내용 (한 장)

**Loader (문서 읽기)**
• PyPDFLoader: PDF 파일
• TextLoader: .txt, .md 등 (encoding 자동감지)
• MinIO에서 받은 바이트 → 임시 파일 → 로더 처리

**Splitter (청킹)**
• RecursiveCharacterTextSplitter: 문단·문장 경계 고려
• CHUNK_SIZE (기본 500), CHUNK_OVERLAP (기본 50) 환경변수로 조정
• 우선순위: `\n\n` → `\n` → `. ` → ` ` 순으로 분리

**Embedding (벡터화)**
• OpenAI: OPENAI_API_KEY, EMBEDDING_MODEL (text-embedding-3-small 등)
• Google Gemini: GEMINI_API_KEY, EMBEDDING_MODEL (gemini-embedding-001 등)
• EMBEDDING_PROVIDER 환경변수로 openai | gemini 선택

**VectorStore (저장)**
• QdrantVectorStore: 컬렉션·클라이언트로 연결
• Payload: page_content, metadata(source, path, doc_id 등)

---

## 발표 노트

Ingestion 파이프라인은 LangChain의 여러 컴포넌트로 이루어집니다. 먼저 Loader가 MinIO에서 받은 파일을 읽습니다. PDF면 PyPDFLoader, 텍스트 파일이면 TextLoader를 씁니다. MinIO에서는 바이트 형태로 파일을 받으니까 일단 임시 파일로 저장한 뒤, 그 경로를 로더에 넘기는 방식입니다.

로더가 문서 전체를 읽고 나면, 다음 단계인 Splitter가 청킹을 합니다. RecursiveCharacterTextSplitter를 쓰는데, 문단 끝(`\n\n`), 문장 끝(`\n`이나 `. `), 공백(` `) 순서로 경계를 찾아서 자릅니다. 그래서 원문이 훼손되지 않고 자연스럽게 청크가 만들어집니다. CHUNK_SIZE는 한 청크가 얼마나 클지, CHUNK_OVERLAP은 청크들이 얼마나 겹칠지를 정합니다. 기본값은 각각 500과 50이고, 환경변수로 바꿀 수 있습니다.

청크가 만들어지면 Embedding 단계에서 벡터로 변환합니다. OpenAI나 Google Gemini의 임베딩 API를 사용합니다. OpenAI면 OPENAI_API_KEY를 설정하고 text-embedding-3-small 같은 모델을 쓰고, Gemini면 GEMINI_API_KEY를 설정해서 gemini-embedding-001을 씁니다. EMBEDDING_PROVIDER 환경변수로 둘 중 어느 것을 쓸지 선택합니다.

마지막으로 벡터는 Qdrant에 저장됩니다. QdrantVectorStore라는 LangChain 클래스를 써서 Qdrant 클라이언트와 컬렉션 이름으로 연결하고, 벡터와 함께 metadata(어느 파일에서 왔는지, 경로, 문서 ID 등)를 payload로 저장합니다. 이렇게 하면 나중에 검색할 때 답변의 출처를 추적할 수 있습니다.
