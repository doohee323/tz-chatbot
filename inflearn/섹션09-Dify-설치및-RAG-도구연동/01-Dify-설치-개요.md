# 01. Dify 설치 개요

## Dify란

- **LLM 오케스트레이션** 플랫폼: 대화형 챗봇·에이전트·워크플로우를 웹 UI로 설계하고 API로 서비스
- tz-chatbot에서는 **챗봇 앱**(DrillQuiz, CoinTutor 등)을 Dify에서 만들고, **RAG 도구**로 우리 RAG Backend URL을 연결합니다

## K8s 설치

- **dify/** 디렉터리: Helm 차트와 values (dify/README.md, values.yaml)
- **설치 순서**: bootstrap.sh 기준으로 Ingress·MinIO·RAG **다음**에 Dify 설치 (RAG Backend URL을 Dify에서 설정해야 하므로)
- **네임스페이스**: `dify`
- 설치 후 Dify 웹 UI에 접속해 로그인·앱 생성·도구 URL 설정

## 설치 후 할 일

- Dify 웹 UI에서 **앱(워크플로우)** 생성
- **도구(Tool)** 노드에 RAG Backend URL 설정:  
  `http://rag-backend.rag.svc.cluster.local:8000/query` (CoinTutor),  
  `http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query` (DrillQuiz)
- API Key 발급 후 chat-gateway·chat-admin에서 DIFY_BASE_URL, DIFY_API_KEY로 사용
