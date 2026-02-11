# 슬라이드 01: Dify 설치와 RAG 도구 URL 설정

## 슬라이드 내용 (한 장)

**Dify 설치**  
• dify/ 디렉터리: Helm 차트·values. bootstrap 4단계로 설치 (RAG 다음). NS: dify  
• 설치 후 웹 UI 접속 → 로그인·앱(워크플로우) 생성·API Key 발급

**앱·워크플로우**  
• 챗봇 또는 워크플로우 형태의 “앱”을 Dify에서 생성. 각 앱은 프롬프트·LLM·도구(Tool) 조합  
• DrillQuiz용·CoinTutor용 앱 각각 생성 후, 각각에 RAG 도구 URL 연결

**RAG 도구 URL (K8s 내부)**  
• 워크플로우에 도구 노드 추가 → 타입 API(Http) → URL에 RAG Backend 검색 API 주소  
• CoinTutor: http://rag-backend.rag.svc.cluster.local:8000/query  
• DrillQuiz: http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query  
• Dify Pod가 rag NS의 Service에 접근 가능해야 함. 인증 필요 시 도구 설정에서 Header에 API 키 등 추가

**검증**: Dify에서 테스트 채팅 또는 실제 채팅으로 RAG 도구 호출·결과 반영 확인. API Key는 chat-gateway·chat-admin의 DIFY_API_KEY 등에 설정

---

## 발표 노트

Dify는 dify 폴더에 Helm 차트와 values가 있고, bootstrap.sh의 4단계에서 RAG 스택 다음에 설치됩니다. 네임스페이스는 dify입니다. 설치가 끝나면 웹 UI에 접속해서 로그인하고, 앱, 즉 워크플로우를 만들고 API Key를 발급합니다.

앱은 챗봇이나 워크플로우 형태로 하나씩 만듭니다. DrillQuiz용 앱, CoinTutor용 앱을 각각 만들고, 각 앱의 워크플로우에 RAG 도구를 연결합니다. 워크플로우 편집 화면에서 도구 노드를 추가하고, 타입을 API, Http 같은 걸로 선택한 뒤, URL에 RAG Backend의 검색 API 주소를 넣습니다. K8s 클러스터 안에서만 호출되기 때문에 외부 도메인이 아니라 서비스 DNS를 씁니다. CoinTutor용 Backend는 http://rag-backend.rag.svc.cluster.local:8000/query, DrillQuiz용은 http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query 를 넣으시면 됩니다. Dify Pod가 rag 네임스페이스의 Service에 네트워크로 접근할 수 있어야 하므로, 네트워크 정책이 막고 있지 않은지 확인하시면 됩니다. RAG Backend가 API Key를 요구하면 도구 설정에서 Header에 해당 키를 넣어 줄 수 있습니다.

검증은 Dify 웹 UI에서 해당 앱으로 테스트 채팅을 보내 보거나, 실제 chat-gateway 경유로 채팅해서 RAG 도구가 호출되고 결과가 LLM 답변에 반영되는지 보시면 됩니다. 발급한 API Key는 chat-gateway와 chat-admin의 DIFY_API_KEY나 앱별 DIFY_*_API_KEY에 설정해 두시면 됩니다.
