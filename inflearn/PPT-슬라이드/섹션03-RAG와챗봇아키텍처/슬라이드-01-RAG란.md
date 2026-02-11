# 슬라이드 01: RAG란

## 슬라이드 내용 (한 장)

**RAG (Retrieval-Augmented Generation)**  
• 외부 지식(문서)을 **검색**해서 LLM 답변에 반영  
• 질의 → **검색(Retrieval)** 로 관련 문서 조각 → **생성(Generation)** 에 활용  
• 단순 LLM 대비 **최신·전문 지식** 반영, **환각 감소**에 유리

**tz-chatbot에서의 구현**  
MinIO(문서) → Ingestion(청킹·임베딩) → Qdrant(벡터 DB) → RAG Backend(검색 API) → Dify(LLM·도구 호출)

---

## 발표 노트

RAG는 Retrieval-Augmented Generation의 약자입니다. 말 그대로 검색으로 보강한 생성이에요. 외부 지식, 즉 회사 문서나 매뉴얼 같은 것을 검색해서 LLM 답변에 반영하는 방식입니다. 사용자 질의가 들어오면 먼저 검색, Retrieval 단계에서 관련 문서 조각을 찾고, 그 내용을 생성, Generation 단계에 넣어서 답을 만듭니다. LLM만 쓸 때는 학습 시점 이후 지식이나 내부 문서를 모르기 때문에 한계가 있는데, RAG를 쓰면 최신 정보나 전문 지식을 문서에서 가져와 반영할 수 있고, “이 문서에 있는 내용만 기준으로 답해라”처럼 출처를 제한할 수 있어서 환각을 줄이는 데도 유리합니다.

tz-chatbot에서는 이 흐름이 이렇게 구현됩니다. 문서는 MinIO에 두고, Ingestion 단계에서 청킹과 임베딩을 해서 Qdrant라는 벡터 DB에 넣습니다. RAG Backend가 검색 API를 제공하고, Dify가 LLM과 도구 호출을 할 때 이 Backend를 호출하는 구조입니다. 다음 슬라이드부터 임베딩, 벡터 DB, Dify 역할을 하나씩 자세히 보겠습니다.
