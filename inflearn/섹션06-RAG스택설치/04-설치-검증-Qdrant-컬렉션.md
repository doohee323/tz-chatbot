# 04. 설치 검증: Qdrant 컬렉션

## 확인할 것

1. **rag 네임스페이스·Pod**
   - `kubectl get pods -n rag`
   - Qdrant, rag-backend, rag-backend-drillquiz 등이 Running인지

2. **Qdrant 컬렉션**
   - install.sh에 포함된 **qdrant-collection-init** Job이 성공하면 `rag_docs_cointutor`, `rag_docs_drillquiz` 컬렉션이 생성됩니다.
   - Qdrant API에 직접 질의하거나, RAG Backend의 `/query` 등으로 검색 테스트해 볼 수 있습니다.

3. **RAG Backend 동작**
   - Backend Service에 (클러스터 내부 또는 port-forward로) 요청을 보내 검색이 되는지 확인
   - Secret이 없거나 잘못되면 Pod가 CrashLoopBackOff 되거나 검색 시 401/403 등이 날 수 있음

## 자주 하는 검증

```bash
# Pod 상태
kubectl get pods -n rag

# Backend 로그 (에러 확인)
kubectl logs -n rag deployment/rag-backend --tail=50

# Secret 존재 여부
kubectl get secret -n rag | grep rag-ingestion-secret
```

컬렉션이 있고 Backend가 정상 응답하면, 다음 단계(토픽별 문서 업로드·Ingestion 실행, Dify 도구 URL 설정)로 진행할 수 있습니다.
