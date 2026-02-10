# 04. RAG와 챗봇 시스템 개요

## RAG란

- **RAG (Retrieval-Augmented Generation)**: 외부 지식(문서)을 검색해서 LLM 답변에 반영하는 방식
- 사용자 질의 → **검색(Retrieval)** 으로 관련 문서 조각을 찾고 → 그 내용을 **생성(Generation)** 에 활용
- 단순 LLM만 쓸 때보다 **최신·전문 지식**, **환각 감소**에 유리

## 챗봇 시스템에서의 위치

- **클라이언트 앱**(DrillQuiz, CoinTutor 등) → **chat-gateway** → **Dify** → (필요 시) **RAG Backend** → **Qdrant / MinIO**
- Dify: 대화 흐름·프롬프트·도구 호출을 담당하는 LLM 오케스트레이션
- RAG Backend: 문서를 벡터로 저장해 두고, 질의와 유사한 청크를 검색해 Dify에 전달
- 이 전체가 **K8s 위**에서 Pod·Service·Ingress로 구성됩니다.

## tz-chatbot에서의 역할

- **RAG 스택**: MinIO(문서 저장) → Ingestion(청킹·임베딩·Qdrant 저장) → RAG Backend(검색 API)
- **Dify**: 챗봇 앱별 워크플로우, RAG 도구 URL로 Backend 호출
- **chat-gateway**: 여러 앱의 채팅을 한 API로 받아 Dify로 전달, 대화·사용자 관리
- **chat-admin**: 시스템(앱) 등록, 채팅 조회, RAG 문서 업로드·재색인 등 관리

이후 섹션에서 RAG·임베딩·Vector DB·Dify·LangChain을 자세히 다룹니다.
