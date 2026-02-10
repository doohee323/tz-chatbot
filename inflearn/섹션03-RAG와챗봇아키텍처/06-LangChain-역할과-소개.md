# 06. LangChain 역할과 소개

## LangChain이란

- **LLM·RAG 파이프라인**을 구성하기 위한 오픈소스 프레임워크
- “문서 로드 → 분할 → 임베딩 → 벡터 저장·검색” 같은 단계를 **추상화된 컴포넌트**로 제공
- tz-chatbot에서는 **Ingestion 스크립트(ingest.py)** 와 **RAG Backend**에서 LangChain 라이브러리를 사용합니다.

## 본 프로젝트에서의 역할

| 역할 | LangChain 컴포넌트 | 사용처 |
|------|--------------------|--------|
| **Loader** | PyPDFLoader, TextLoader (langchain_community) | ingest.py: MinIO에서 받은 바이트 → 임시 파일 → 로더로 문서 로드 |
| **Splitter** | RecursiveCharacterTextSplitter (langchain_text_splitters) | ingest.py: 문서를 chunk_size/chunk_overlap 기준으로 청킹 |
| **Embedding** | OpenAIEmbeddings, GoogleGenerativeAIEmbeddings | ingest.py·RAG Backend: 텍스트 → 벡터 |
| **VectorStore** | QdrantVectorStore (langchain_qdrant) | ingest.py: 벡터 upsert. RAG Backend에서 검색 시에도 사용 |

## 왜 쓰는가

- **Loader/Splitter**: PDF·TXT 등 형식별 로딩, 문단·문장 경계를 고려한 청킹을 **일관된 API**로 처리
- **Embedding/VectorStore**: OpenAI·Gemini 등 **모델 교체**가 쉬우며, Qdrant 연동이 라이브러리로 정리됨
- 직접 HTTP·SDK만으로 구현할 수도 있지만, 유지보수·확장 시 LangChain 조합이 편리합니다.

자세한 코드·환경변수는 **섹션 08** (RAG 문서 수집·임베딩·Ingestion)에서 다룹니다.
