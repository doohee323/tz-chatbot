# 슬라이드 01: ingest 흐름과 LangChain·CronJob

## 슬라이드 내용 (한 장)

**ingest.py 흐름**  
• **저장소**: `rag/scripts/ingest.py` (install.sh가 ConfigMap `rag-ingestion-script`로 만들어 Pod `/config/ingest.py` 마운트)  
• 환경변수(MINIO_*, QDRANT_*, EMBEDDING_PROVIDER, GEMINI/OPENAI API Key, CHUNK_SIZE, MINIO_PREFIX, QDRANT_COLLECTION 등) → MinIO prefix 아래 객체 목록·다운로드 → **Loader**(PyPDFLoader, TextLoader) → **Splitter**(RecursiveCharacterTextSplitter) → **Embedding**(OpenAI/Gemini) → **QdrantVectorStore** upsert. (선택) INCREMENTAL=true 시 변경/삭제만 반영

**LangChain 구성**  
• Loader: langchain_community (PDF·TXT). MinIO 바이트→임시 파일→로더  
• Splitter: RecursiveCharacterTextSplitter (chunk_size, chunk_overlap)  
• Embedding: OpenAIEmbeddings 또는 GoogleGenerativeAIEmbeddings  
• VectorStore: QdrantVectorStore. requirements-ingest.txt 의존성, Job 내 pip install 후 실행

**CronJob·수동 실행**  
• CronJob: 토픽별 스케줄(예 02:00, 02:30). 수동 1회: `kubectl create job -n rag ingest-cointutor-1 --from=cronjob/rag-ingestion-cronjob-cointutor`. INCREMENTAL=false 또는 full CronJob으로 전체 재색인 가능. 관리 화면 재색인 버튼도 Job 생성 트리거

---

## 발표 노트

ingest.py는 MinIO의 지정 prefix 아래 파일을 읽어서 LangChain으로 로드·청킹·임베딩한 뒤 Qdrant에 넣는 스크립트입니다. 환경변수로 MinIO 접속 정보, Qdrant 접속 정보, 임베딩 제공자와 API 키, chunk_size·chunk_overlap, MINIO_PREFIX·QDRANT_COLLECTION 같은 걸 받습니다. MinIO에서 prefix 아래 객체 목록을 조회하고 파일을 다운로드한 뒤, Loader는 PDF면 PyPDFLoader, TXT·MD면 TextLoader를 씁니다. Splitter는 RecursiveCharacterTextSplitter로 문단·문장 경계를 고려해 청킹하고, Embedding은 OpenAI나 Gemini로 벡터를 만들고, QdrantVectorStore로 upsert합니다. INCREMENTAL이 true면 기존 doc_id·수정 시각과 비교해서 변경·삭제분만 반영합니다.

LangChain 구성은 이렇게 되어 있습니다. Loader는 langchain_community에서 가져오고, MinIO에서 받은 바이트를 임시 파일로 쓴 뒤 그 경로를 로더에 넘깁니다. Splitter는 RecursiveCharacterTextSplitter로 chunk_size와 chunk_overlap을 환경변수로 조정합니다. Embedding은 OpenAIEmbeddings나 GoogleGenerativeAIEmbeddings를 쓰고, VectorStore는 QdrantVectorStore입니다. 의존성은 requirements-ingest.txt에 있고, Job 안에서 pip install 한 뒤 ingest.py를 실행합니다.

CronJob은 토픽별로 스케줄이 잡혀 있어서, 예를 들어 CoinTutor는 매일 02:00, DrillQuiz는 02:30에 돌 수 있습니다. 수동으로 한 번만 돌리려면 kubectl create job으로 CronJob에서 Job을 생성하면 됩니다. 예를 들어 ingest-cointutor-1 같은 이름으로 만들면 됩니다. 전체 재색인을 하려면 INCREMENTAL을 false로 두거나 full용 CronJob에서 Job을 생성하면 됩니다. chat-admin 관리 화면의 재색인 버튼도 내부적으로 이런 Job을 생성하는 방식으로 구현될 수 있습니다.
