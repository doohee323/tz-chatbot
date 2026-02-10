# 01. tz-chatbot 플로우와 컴포넌트

## 요청 플로우 (K8s 위 컴포넌트 기준)

```
클라이언트 앱 (DrillQuiz / CoinTutor 등)
    → Ingress (TLS, 라우팅)
    → chat-gateway (Pod, devops NS)
    → Dify (Pod, dify NS)
    → RAG Backend (Pod, rag NS) — 필요 시
    → Qdrant / MinIO (rag NS, devops NS)
```

- 사용자 채팅 메시지는 **chat-gateway**로 들어오고, **Dify**가 LLM·도구 호출을 담당합니다.
- RAG가 필요하면 Dify가 **RAG Backend**를 호출하고, Backend는 **Qdrant**에서 벡터 검색, 원문은 **MinIO** 등에서 참조합니다.

## K8s 관점 컴포넌트

| 컴포넌트 | 네임스페이스 | 역할 |
|----------|--------------|------|
| Ingress NGINX | default | HTTPS·도메인 라우팅 |
| MinIO | devops | 객체 저장소, `rag-docs` 버킷 |
| Qdrant | rag | 벡터 DB (RAG 컬렉션) |
| RAG Backend (CoinTutor/DrillQuiz) | rag | 검색 API, 토픽별 Deployment |
| RAG Ingestion | rag | Job/CronJob, MinIO → 임베딩 → Qdrant |
| Dify | dify | 챗봇·워크플로우·RAG 도구 연동 |
| chat-gateway | devops | 채팅 API, `/chat`, `/v1/chat`, `/v1/conversations` |
| chat-admin | devops | 관리 UI: 시스템 CRUD, 채팅 조회, RAG 업로드·재색인 |

## 설치 순서 (bootstrap.sh 기준)

1. Ingress NGINX (default NS)
2. MinIO (devops NS)
3. RAG 스택 (rag NS): Qdrant, RAG Backends, Ingestion Job/CronJob
4. Dify (dify NS)

chat-admin과 chat-gateway는 **bootstrap.sh에 포함되지 않으며**, CI(k8s.sh) 또는 Jenkins로 별도 배포합니다.
