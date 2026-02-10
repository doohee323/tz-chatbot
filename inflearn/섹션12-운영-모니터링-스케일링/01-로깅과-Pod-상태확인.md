# 01. 로깅과 Pod 상태 확인

## Pod 상태

```bash
kubectl get pods -n rag
kubectl get pods -n dify
kubectl get pods -n devops
```

- **Running**이어야 정상. **CrashLoopBackOff**, **ImagePullBackOff**, **Pending** 등은 원인 조사 필요
- `kubectl describe pod <name> -n <ns>` 로 이벤트·상태 이유 확인

## 로그

```bash
kubectl logs -n rag deployment/rag-backend --tail=100
kubectl logs -n dify deployment/dify-api -f
kubectl logs -n devops deployment/chat-gateway --tail=50
```

- **RAG Backend**: API 키·Qdrant 연결 오류 등
- **Dify**: 앱 실행·도구 호출 오류
- **chat-gateway**: Dify 호출·DB 오류
- **Ingestion Job**: `kubectl logs -n rag job/<job-name>` 으로 MinIO·임베딩·Qdrant 오류 확인

## 로그 수집·중앙화

- 운영 환경에서는 **Loki**, **EFK** 등으로 Pod 로그를 수집·검색할 수 있습니다. 구축 방법은 별도 문서를 참고하세요.
