# 슬라이드 01: 로깅과 Pod 상태 확인

## 슬라이드 내용 (한 장)

**Pod 상태**  
• `kubectl get pods -n rag` / `-n dify` / `-n devops`  
• **Running**이면 정상. **CrashLoopBackOff**, **ImagePullBackOff**, **Pending** 등은 원인 조사  
• `kubectl describe pod <name> -n <ns>`: 이벤트·상태 이유·이미지·리소스 확인

**로그 확인**  
• `kubectl logs -n rag deployment/rag-backend --tail=100`  
• `kubectl logs -n dify deployment/dify-api -f`  
• `kubectl logs -n devops deployment/chat-gateway --tail=50`  
• RAG Backend: API 키·Qdrant 연결 오류. Dify: 앱·도구 호출 오류. chat-gateway: Dify·DB 오류  
• Ingestion Job: `kubectl logs -n rag job/<job-name>` → MinIO·임베딩·Qdrant 오류 확인

**로그 수집·중앙화**  
• 운영 환경: **Loki**, **EFK** 등으로 Pod 로그 수집·검색. 구축 방법은 별도 문서 참고

---

## 발표 노트

운영 중에는 먼저 Pod 상태를 봅니다. kubectl get pods로 rag, dify, devops 네임스페이스를 확인하세요. Running이면 일단 정상이고, CrashLoopBackOff는 컨테이너가 계속 죽는 경우, ImagePullBackOff는 이미지를 못 가져온 경우, Pending은 스케줄이 안 된 경우라 원인을 봐야 합니다. kubectl describe pod로 해당 Pod의 이벤트, 상태 이유, 이미지, 리소스 요청·제한을 확인할 수 있습니다.

로그는 kubectl logs로 봅니다. rag-backend는 API 키나 Qdrant 연결 오류가 자주 나오고, dify-api는 앱 실행이나 도구 호출 관련 오류, chat-gateway는 Dify 호출이나 DB 오류를 확인하시면 됩니다. -f는 실시간 스트리밍, --tail=100은 마지막 100줄만 보는 옵션입니다. RAG Ingestion은 Job으로 돌기 때문에 job 이름으로 kubectl logs -n rag job/해당-job-name 하시면 MinIO 접근, 임베딩, Qdrant upsert 오류를 볼 수 있습니다.

운영 환경에서는 Loki나 EFK 같은 걸로 Pod 로그를 한곳에 모아서 검색하는 구성을 추천합니다. 구축 방법은 별도 문서를 참고하시면 됩니다.
