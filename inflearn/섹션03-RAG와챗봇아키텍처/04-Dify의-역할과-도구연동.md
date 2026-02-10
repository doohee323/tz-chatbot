# 04. Dify의 역할과 도구 연동

## Dify란

- **LLM 오케스트레이션** 플랫폼: 대화 흐름, 프롬프트, **도구(Tool)** 호출을 조합해 챗봇·에이전트를 만듦
- 웹 UI로 앱(워크플로우) 생성·배포, API Key 발급
- tz-chatbot에서는 **K8s에 Helm으로** 설치, `dify` 네임스페이스

## Dify의 역할

- **챗봇 앱**: 사용자 메시지 수신 → LLM이 답변 생성 (필요 시 도구 호출)
- **RAG 도구 연동**: “지식 검색” 같은 **도구**의 URL을 **RAG Backend** 주소로 설정
  - 예: `http://rag-backend.rag.svc.cluster.local:8000/query` (CoinTutor), DrillQuiz용 Backend URL 별도
- 사용자 ID는 chat-gateway에서 `{system_id}_{user_id}` 형태로 Dify에 전달해, 앱별·사용자별로 구분

## 도구(Tool) URL

- Dify 워크플로우에서 “도구” 노드에 **HTTP URL**을 넣으면, Dify가 그 URL로 요청을 보냄
- RAG Backend는 `/query` 등에서 질의를 받아 Qdrant 검색 후 결과를 반환
- 따라서 **RAG Backend Service 주소**(K8s 내부: `http://rag-backend.rag.svc...`)를 Dify 도구 URL로 설정해야 함 (섹션 09에서 실습).
