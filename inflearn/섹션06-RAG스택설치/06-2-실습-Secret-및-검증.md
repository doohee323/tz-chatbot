# 06-2. 실습: Secret 및 검증

## 목표

- 토픽별 RAG Secret(`rag-ingestion-secret-cointutor`, `rag-ingestion-secret-drillquiz`)을 생성하고, RAG Backend가 정상 동작하는지 검증합니다.

## 단계

### 1. MinIO 접근 정보 확인

```bash
MINIO_USER=$(kubectl get secret minio -n devops -o jsonpath='{.data.rootUser}' | base64 -d)
MINIO_PASS=$(kubectl get secret minio -n devops -o jsonpath='{.data.rootPassword}' | base64 -d)
echo "MinIO user length: ${#MINIO_USER}"
```

- MinIO가 devops NS에 있어야 함

### 2. Gemini API 키 준비

- [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키 발급
- 변수에 넣기: `GEMINI_KEY='실제키값'`

### 3. Secret 생성 (rag/README.md 예시 참고)

```bash
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

### 4. Backend 재시작 (이미 기동 중이었다면)

```bash
kubectl rollout restart deployment/rag-backend deployment/rag-backend-drillquiz -n rag
kubectl get pods -n rag -w   # Running 될 때까지 확인
```

### 5. 검증

- `kubectl logs -n rag deployment/rag-backend --tail=30`: 에러 없이 기동했는지 확인
- (선택) RAG Backend에 port-forward 후 `/query` 등 검색 API 호출해 보기

이후 섹션 07(토픽별 RAG 분리), 08(Ingestion)에서 문서 업로드·재색인을 진행할 수 있습니다.
