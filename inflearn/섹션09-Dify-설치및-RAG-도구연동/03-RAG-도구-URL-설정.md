# 03. RAG 도구 URL 설정

## 도구(Tool) 추가

- Dify 워크플로우 편집 화면에서 **도구** 노드를 추가하고, 타입을 **API(Http)** 등으로 선택
- **URL**에 RAG Backend의 검색 API 엔드포인트를 넣습니다.

## K8s 내부 URL (같은 클러스터)

- **CoinTutor**: `http://rag-backend.rag.svc.cluster.local:8000/query` (또는 실제 경로에 맞게)
- **DrillQuiz**: `http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query`
- Dify Pod가 **rag** 네임스페이스의 Service에 접근할 수 있어야 하므로, 네트워크 정책이 막고 있지 않은지 확인

## 인증

- RAG Backend가 API Key를 요구하면, Dify 도구 설정에서 **Header**에 해당 키를 넣어 줄 수 있습니다.  
  (현재 tz-chatbot Backend는 Secret의 API 키를 사용하므로, Dify → Backend 호출 시 별도 키가 필요할 수도 있고 없을 수도 있음. 저장소 구현 확인.)

## 프로젝트에서의 두 가지 방식

- **방식 1 (단순 URL)**: 도구 노드에 **API(Http)** 타입으로 RAG Backend URL만 설정 (위 K8s 내부 URL 참고).
- **방식 2 (커스텀 도구·OpenAPI)**: Dify 웹 UI에서 **Tools → Custom → Create custom tool**로 등록 후, **Schema**에 OpenAPI 스키마를 붙여넣는 방법입니다. tz-chatbot 저장소에는 다음 파일이 포함되어 있습니다.
  - **CoinTutor**: `dify/cointutor/cointutor-rag-openapi.yaml` — 내용을 복사해 Dify 커스텀 도구 Schema 필드에 붙여넣기
  - **DrillQuiz**: `dify/drillquiz/drillquiz-rag-openapi.yaml` — 동일
- 앱 워크플로우를 YAML로 가져온 경우(예: `dify/cointutor/CoinTutor.yml`)에는, Tool 노드에서 방금 만든 "CoinTutor RAG" 또는 "DrillQuiz RAG" 커스텀 도구를 다시 선택해 주어야 합니다 (dify/README.md 참고).

## 확인

- Dify에서 “테스트” 또는 실제 채팅으로 질의를 보내 RAG 도구가 호출되고 결과가 LLM에 전달되는지 확인합니다.
