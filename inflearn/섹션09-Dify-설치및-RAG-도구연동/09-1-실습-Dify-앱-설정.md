# 09-1. 실습: Dify 앱 설정

## 목표

- Dify 웹 UI에 접속해 챗봇 앱을 만들고, RAG 도구 URL을 설정합니다.

## 단계

### 1. Dify 접속

- Ingress로 노출했다면: `https://<dify-domain>/` 등으로 접속
- 또는 `kubectl port-forward -n dify svc/dify-api 80:80` 후 `http://localhost` (실제 Service 이름·포트는 values 확인)

### 2. 로그인·앱 생성

- 최초 설정 시 관리자 계정 생성
- **앱 생성** → **챗봇** 또는 **워크플로우** 선택
- DrillQuiz용, CoinTutor용 각각 앱을 만들거나, 하나의 앱에서 도구만 두 개 쓰는 방식은 설계에 따름

### 3. RAG 도구 추가

- 워크플로우에 **도구** 노드 추가
- 타입: API(Http) 등
- URL:  
  - CoinTutor: `http://rag-backend.rag.svc.cluster.local:8000/query`  
  - DrillQuiz: `http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query`
- 필요 시 메서드·헤더·바디 형식은 RAG Backend API 스펙에 맞게 설정

### 4. API Key 발급

- 앱 설정에서 **API Key** 발급
- 이 키를 chat-gateway·chat-admin의 **DIFY_API_KEY** 또는 앱별 **DIFY_*_API_KEY** 에 넣습니다

다음 실습(09-2)에서 실제로 RAG 질의가 되는지 채팅으로 확인합니다.
