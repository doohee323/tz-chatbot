# 슬라이드 01: tz-chatbot 플로우와 컴포넌트

## 슬라이드 내용 (한 장)

**요청 플로우**  
클라이언트 앱 → Ingress → chat-gateway(devops) → Dify(dify) → (필요 시) RAG Backend(rag) → Qdrant / MinIO  
• 채팅 메시지는 gateway로 들어오고 Dify가 LLM·도구 호출  
• RAG 필요 시 Dify가 RAG Backend 호출 → Backend가 Qdrant 검색

**K8s 컴포넌트 요약**

| 컴포넌트 | NS | 역할 |
|----------|-----|------|
| Ingress NGINX | default | HTTPS·도메인 라우팅 |
| MinIO | devops | rag-docs 버킷 |
| Qdrant | rag | 벡터 DB |
| RAG Backend | rag | 토픽별 검색 API |
| RAG Ingestion | rag | Job/CronJob |
| Dify | dify | 챗봇·RAG 도구 연동 |
| chat-gateway | devops | /chat, /v1/chat, /v1/conversations |
| chat-admin | devops | 시스템 CRUD, 채팅 조회, RAG 업로드·재색인 |

**bootstrap.sh 순서**: 1) Ingress 2) MinIO 3) RAG 스택 4) Dify. chat-admin·chat-gateway는 별도 배포(CI/k8s.sh 또는 Jenkins).

---

## 발표 노트

tz-chatbot에서 한 번의 채팅 요청이 어떻게 흐르는지 보겠습니다.

클라이언트 앱, 예를 들어 DrillQuiz나 CoinTutor에서 요청이 나오면 먼저 Ingress를 통과합니다. TLS와 도메인 라우팅이 여기서 이뤄지고, 그다음 devops 네임스페이스의 chat-gateway Pod로 갑니다. gateway에서 dify 네임스페이스의 Dify로 넘기고, Dify가 LLM과 도구 호출을 담당합니다. RAG가 필요하면 Dify가 rag 네임스페이스의 RAG Backend를 호출하고, Backend는 Qdrant에서 벡터 검색을 하고, 원문은 MinIO 등에서 참조합니다. 즉 채팅 메시지는 gateway로 들어오고, Dify가 실제 LLM과 도구 호출을 하고, RAG가 필요할 때만 RAG Backend를 거칩니다.

K8s 관점에서 컴포넌트를 정리하면 이렇습니다. Ingress NGINX는 default 네임스페이스에서 HTTPS와 도메인 라우팅을 담당합니다. MinIO는 devops에 있고 rag-docs 버킷을 제공합니다. Qdrant는 rag 네임스페이스에 벡터 DB로 있고, RAG Backend도 rag에 토픽별로 Deployment가 있습니다. RAG Ingestion은 Job과 CronJob으로 같은 rag 네임스페이스에서 MinIO에서 읽어 임베딩 후 Qdrant에 넣는 작업을 합니다. Dify는 dify 네임스페이스에 챗봇과 RAG 도구 연동을 담당하고, chat-gateway와 chat-admin은 devops에 있습니다. gateway는 채팅 API, 즉 /chat, /v1/chat, /v1/conversations를 제공하고, admin은 시스템 CRUD, 채팅 조회, RAG 문서 업로드와 재색인 트리거를 담당합니다.

설치 순서는 bootstrap.sh 기준으로, 1번 Ingress, 2번 MinIO, 3번 RAG 스택, 4번 Dify입니다. chat-admin과 chat-gateway는 bootstrap에 포함되지 않고, CI의 k8s.sh나 Jenkins로 별도 배포합니다.
