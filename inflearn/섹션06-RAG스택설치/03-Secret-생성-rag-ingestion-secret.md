# 03. Secret 생성: rag-ingestion-secret

## 왜 필요한가

- RAG Backend와 Ingestion Job/CronJob은 **MinIO 접근 키**와 **임베딩 API 키**(Gemini 또는 OpenAI)가 필요합니다.
- 이 값들을 **K8s Secret**으로 만들어 두고, Deployment·Job에서 환경변수로 주입합니다.
- Secret이 없으면 Backend Pod가 기동하지 않거나, 검색 시 "API key not valid" 등 오류가 납니다.

## 토픽별 Secret 이름

- **CoinTutor**: `rag-ingestion-secret-cointutor` (namespace: `rag`)
- **DrillQuiz**: `rag-ingestion-secret-drillquiz` (namespace: `rag`)

두 Secret에 **같은 값**을 써도 됩니다 (MinIO·API 키를 공유하는 경우).

## 생성 예시 (rag/README.md 기준)

```bash
MINIO_USER=$(kubectl get secret minio -n devops -o jsonpath='{.data.rootUser}' | base64 -d)
MINIO_PASS=$(kubectl get secret minio -n devops -o jsonpath='{.data.rootPassword}' | base64 -d)
GEMINI_KEY='your_valid_Gemini_API_key_here'   # 실제 키로 교체

kubectl create secret generic rag-ingestion-secret-cointutor -n rag \
  --from-literal=MINIO_ACCESS_KEY="$MINIO_USER" \
  --from-literal=MINIO_SECRET_KEY="$MINIO_PASS" \
  --from-literal=GEMINI_API_KEY="$GEMINI_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic rag-ingestion-secret-drillquiz -n rag \
  --from-literal=MINIO_ACCESS_KEY="$MINIO_USER" \
  --from-literal=MINIO_SECRET_KEY="$MINIO_PASS" \
  --from-literal=GEMINI_API_KEY="$GEMINI_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

- **GEMINI_API_KEY**: [Google AI Studio](https://aistudio.google.com/apikey)에서 발급. OpenAI를 쓰면 해당 키 이름으로 Secret 항목을 맞추고 Backend/Ingestion 설정을 OpenAI용으로 변경해야 합니다.
- Secret 수정 후에는 Backend Pod를 재시작해야 반영됩니다:  
  `kubectl rollout restart deployment/rag-backend deployment/rag-backend-drillquiz -n rag`
