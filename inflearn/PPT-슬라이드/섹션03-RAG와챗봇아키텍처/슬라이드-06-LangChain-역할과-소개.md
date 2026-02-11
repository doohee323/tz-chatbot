# 슬라이드 06: LangChain 역할과 소개

## 슬라이드 내용 (한 장)

**LangChain**  
• LLM·RAG 파이프라인을 만들기 위한 오픈소스 프레임워크  
• “문서 로드 → 분할 → 임베딩 → 벡터 저장·검색” 단계를 **추상화된 컴포넌트**로 제공  
• tz-chatbot: **ingest.py**, **RAG Backend**에서 사용

**본 프로젝트에서의 역할**

| 역할 | LangChain 컴포넌트 | 사용처 |
|------|-------------------|--------|
| Loader | PyPDFLoader, TextLoader (langchain_community) | ingest.py: MinIO 바이트→임시 파일→로더 |
| Splitter | RecursiveCharacterTextSplitter | ingest.py: chunk_size/overlap 청킹 |
| Embedding | OpenAIEmbeddings, GoogleGenerativeAIEmbeddings | ingest.py·RAG Backend |
| VectorStore | QdrantVectorStore (langchain_qdrant) | ingest.py: upsert; Backend: 검색 |

**이점**: 형식별 로딩·문맥 고려 청킹·모델 교체·Qdrant 연동을 일관된 API로 처리 (섹션 08에서 코드·환경변수 상세)

---

## 발표 노트

LangChain은 LLM과 RAG 파이프라인을 구성하기 위한 오픈소스 프레임워크입니다. 문서를 로드하고, 분할하고, 임베딩하고, 벡터 저장과 검색을 하는 단계를 추상화된 컴포넌트로 제공해서, 직접 HTTP나 SDK만으로 구현할 때보다 유지보수와 확장이 쉽습니다. tz-chatbot에서는 ingest 스크립트와 RAG Backend에서 LangChain 라이브러리를 사용합니다.

본 프로젝트에서의 역할을 표로 정리하면 이렇습니다. Loader는 langchain_community의 PyPDFLoader, TextLoader를 씁니다. ingest.py에서 MinIO에서 받은 바이트를 임시 파일로 쓴 뒤 해당 경로를 로더에 넘겨서 문서를 로드합니다. Splitter는 RecursiveCharacterTextSplitter로, chunk_size와 chunk_overlap을 환경변수로 두고 문단·문장 경계를 고려해 청킹합니다. Embedding은 OpenAIEmbeddings나 GoogleGenerativeAIEmbeddings를 쓰고, ingest.py와 RAG Backend 둘 다에서 사용합니다. VectorStore는 langchain_qdrant의 QdrantVectorStore를 쓰고, ingest.py에서는 벡터를 upsert하고, RAG Backend에서는 검색할 때 사용합니다.

이렇게 쓰는 이유는, PDF·TXT 같은 형식별 로딩이랑 문맥을 고려한 청킹을 일관된 API로 처리할 수 있고, 임베딩 모델을 OpenAI에서 Gemini로 바꾸는 것도 설정만 바꾸면 되며, Qdrant 연동이 라이브러리로 정리되어 있기 때문입니다. 각 컴포넌트의 코드나 환경변수는 섹션 8 RAG 문서 수집·임베딩·Ingestion에서 자세히 다룹니다.
