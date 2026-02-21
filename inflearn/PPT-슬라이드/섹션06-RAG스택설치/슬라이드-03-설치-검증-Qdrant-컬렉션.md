# 슬라이드 03: 설치 검증 (Qdrant 컬렉션)

## 슬라이드 내용 (한 장)

**Pod 상태 확인**
• `kubectl get pods -n rag` — Qdrant, rag-backend, rag-backend-drillquiz Running 확인
• Pod 상태 이상: `kubectl describe pod <name> -n rag` 로 이벤트 확인
• Backend 로그: `kubectl logs -n rag deployment/rag-backend --tail=50` (에러 메시지)

**Qdrant 컬렉션 생성 확인**
• install.sh의 qdrant-collection-init Job이 성공해야 컬렉션 생성됨
• 토픽별 컬렉션: `rag_docs_cointutor`, `rag_docs_drillquiz`
• Qdrant API 직접 질의 또는 RAG Backend `/query` 로 검색 테스트

**Secret 확인**
• `kubectl get secret -n rag | grep rag-ingestion-secret`
• Secret 없으면 Backend Pod CrashLoopBackOff 또는 검색 시 401/403 에러

**다음 단계**
• 컬렉션·Pod 정상 → 토픽별 문서 업로드, Ingestion 실행, Dify 도구 URL 설정

---

## 발표 노트

RAG 설치가 끝나면 정상적으로 설치되었는지 검증해야 합니다. 먼저 rag 네임스페이스의 Pod 상태를 봅니다. kubectl get pods -n rag로 Qdrant, rag-backend, rag-backend-drillquiz 등이 Running 상태인지 확인하세요. Pod가 다른 상태면 kubectl describe pod로 이벤트를 보고, kubectl logs로 로그를 확인하면 문제를 파악할 수 있습니다.

Qdrant 컬렉션은 install.sh에 포함된 qdrant-collection-init이라는 Job이 성공할 때 생성됩니다. 성공하면 rag_docs_cointutor와 rag_docs_drillquiz 두 개의 컬렉션이 생성됩니다. 이건 토픽별로 벡터를 분리해서 저장하기 위함입니다. Qdrant API에 직접 질의하거나, RAG Backend의 /query 엔드포인트로 검색을 테스트해서 제대로 작동하는지 확인할 수 있습니다.

Secret도 확인해야 합니다. kubectl get secret -n rag | grep rag-ingestion-secret으로 토픽별 Secret이 있는지 보세요. Secret이 없거나 API Key가 잘못되면 Backend Pod가 CrashLoopBackOff 상태가 되거나, 검색할 때 401이나 403 오류가 발생합니다.

이 모든 게 정상이면, 다음으로 토픽별로 문서를 업로드하고, Ingestion Job을 실행해서 벡터로 임베딩한 뒤, Dify 도구 URL을 설정하는 단계로 진행합니다.
