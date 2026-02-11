# 슬라이드 04: RAG와 챗봇 시스템 개요

## 슬라이드 내용 (한 장)

**RAG (Retrieval-Augmented Generation)**
• 외부 지식(문서)을 검색해서 LLM 답변에 반영
• 질의 → 검색(Retrieval)으로 관련 문서 조각 → 생성(Generation)에 활용
• 단순 LLM 대비 최신·전문 지식 반영, 환각 감소에 유리

**챗봇에서의 흐름 (K8s 위)**  
클라이언트 앱 → **chat-gateway** → **Dify** → (필요 시) **RAG Backend** → Qdrant / MinIO  
• Dify: 대화 흐름·프롬프트·도구 호출(LLM 오케스트레이션)  
• RAG Backend: 문서 벡터 저장·유사 청크 검색 후 Dify에 전달

**tz-chatbot에서의 역할**
• RAG 스택: MinIO → Ingestion(청킹·임베딩) → Qdrant → RAG Backend(검색 API)
• Dify: 앱별 워크플로우, RAG 도구 URL로 Backend 호출
• chat-gateway: 여러 앱의 채팅을 한 API로 받아 Dify로 전달
• chat-admin: 시스템(앱) 등록, 채팅 조회, RAG 문서 업로드·재색인

---

## 발표 노트

RAG는 Retrieval-Augmented Generation의 약자로, 외부 지식, 즉 문서를 검색해서 LLM 답변에 반영하는 방식입니다. 사용자 질의가 들어오면 먼저 검색, Retrieval로 관련 문서 조각을 찾고, 그 내용을 생성, Generation 단계에 넣어서 답을 만듭니다. LLM만 쓸 때보다 최신 정보나 전문 지식 반영이 쉽고, 환각을 줄이는 데 유리합니다.

챗봇 시스템에서의 흐름은 이렇게 됩니다. DrillQuiz나 CoinTutor 같은 클라이언트 앱에서 요청이 나오면, 먼저 chat-gateway로 갑니다. gateway에서 Dify로 넘기고, Dify가 필요할 때 RAG Backend를 호출합니다. RAG Backend는 Qdrant나 MinIO와 연동되어 있습니다. 이 전체가 K8s 위에서 Pod, Service, Ingress로 구성된다고 보시면 됩니다. Dify는 대화 흐름과 프롬프트, 도구 호출을 담당하는 LLM 오케스트레이션 역할을 하고, RAG Backend는 문서를 벡터로 저장해 두었다가 질의와 유사한 청크를 검색해서 Dify에 전달합니다.

tz-chatbot에서 각 컴포넌트의 역할을 정리하면 이렇습니다. RAG 스택은 MinIO에 문서를 두고, Ingestion으로 청킹과 임베딩을 한 뒤 Qdrant에 넣고, RAG Backend가 검색 API를 제공합니다. Dify는 앱별 워크플로우를 갖고 있고, RAG 도구 URL을 통해 Backend를 호출합니다. chat-gateway는 여러 앱의 채팅을 한 API로 받아서 Dify로 넘기고, chat-admin은 시스템, 즉 앱 등록, 채팅 조회, RAG 문서 업로드와 재색인 트리거 같은 관리 기능을 담당합니다. 이후 섹션에서 RAG, 임베딩, Vector DB, Dify, LangChain을 더 자세히 다룹니다.
