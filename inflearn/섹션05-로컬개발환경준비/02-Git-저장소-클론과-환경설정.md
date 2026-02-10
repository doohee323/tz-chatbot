# 02. Git 저장소 클론과 환경 설정

## 저장소 클론

```bash
git clone <tz-chatbot 저장소 URL>
cd tz-chatbot
```

- 실습·배포 시 사용할 **브랜치** 확인 (main / dev / qa 등). 브랜치에 따라 배포 네임스페이스·시크릿 접미사가 달라질 수 있음 (README 참고).

## 환경 설정

- **KUBECONFIG**: 클러스터 접속용. `export KUBECONFIG=~/.kube/...` 또는 셸 프로파일에 추가
- **chat-gateway / chat-admin 로컬 실행 시**:
  - 각 디렉터리에 `.env` 또는 환경변수 설정
  - 예: `DIFY_BASE_URL`, `DIFY_API_KEY`, `CHAT_GATEWAY_JWT_SECRET`, `DATABASE_URL` 등 (각 README 참고)
- **RAG Ingestion / Backend**: K8s에서는 Secret·ConfigMap으로 주입. 로컬에서 ingest.py를 돌릴 때는 MinIO/Qdrant/API Key 환경변수 필요

필요한 변수 목록은 `chat-gateway/README.md`, `chat-admin/README.md`, `rag/README.md`에 정리되어 있습니다.
