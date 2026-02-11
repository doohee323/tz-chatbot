# 슬라이드 02: Secret 생성과 설치 검증

## 슬라이드 내용 (한 장)

**Secret이 필요한 이유**  
• RAG Backend·Ingestion은 MinIO 접근 키 + 임베딩 API 키(Gemini 또는 OpenAI) 필요  
• K8s Secret으로 만들어 Deployment·Job에서 환경변수로 주입. 없으면 Backend 기동 실패·검색 오류

**토픽별 Secret 이름 (NS: rag)**  
• rag-ingestion-secret-cointutor, rag-ingestion-secret-drillquiz (같은 값 써도 됨)

**생성 예 (README 기준)**  
• MinIO rootUser·rootPassword를 devops NS의 minio Secret에서 꺼냄  
• GEMINI_API_KEY는 Google AI Studio에서 발급 후 실제 키로 교체  
• kubectl create secret generic ... --from-literal=MINIO_ACCESS_KEY=... MINIO_SECRET_KEY=... GEMINI_API_KEY=... (cointutor·drillquiz 각각)  
• Secret 수정 후: `kubectl rollout restart deployment/rag-backend deployment/rag-backend-drillquiz -n rag`

**검증**: kubectl get pods -n rag (Qdrant·Backend Running), kubectl logs deployment/rag-backend, Secret 존재 확인. 컬렉션·검색 테스트는 다음 단계(토픽 분리·Ingestion) 후 진행.

---

## 발표 노트

RAG Backend와 Ingestion은 MinIO에 접근할 수 있어야 하고, 임베딩을 만들기 위해 Gemini나 OpenAI API 키가 필요합니다. 이 값들을 K8s Secret으로 만들어 두고, Deployment나 Job에서 환경변수로 주입합니다. Secret이 없으면 Backend Pod가 기동하지 않거나, 검색할 때 API key not valid 같은 오류가 납니다.

토픽별로 Secret 이름이 rag-ingestion-secret-cointutor, rag-ingestion-secret-drillquiz이고, 둘 다 rag 네임스페이스에 만듭니다. MinIO와 API 키를 공유하시면 같은 값으로 두 개 만들어도 됩니다.

생성 방법은 rag/README에 나와 있습니다. MinIO의 rootUser와 rootPassword는 devops 네임스페이스의 minio Secret에서 jsonpath로 꺼내서 쓰시고, GEMINI_API_KEY는 Google AI Studio에서 발급한 뒤 실제 키로 넣으시면 됩니다. kubectl create secret generic으로 MINIO_ACCESS_KEY, MINIO_SECRET_KEY, GEMINI_API_KEY를 from-literal로 넣어서 cointutor용, drillquiz용 각각 만드시면 됩니다. 나중에 Secret을 수정하셨다면 Backend가 새 값을 읽도록 kubectl rollout restart deployment/rag-backend deployment/rag-backend-drillquiz -n rag 로 재시작하시면 됩니다.

검증은 kubectl get pods -n rag로 Qdrant랑 Backend가 Running인지 보시고, kubectl logs로 Backend 로그에 에러가 없는지 보시면 됩니다. Secret이 있는지도 get secret으로 확인하시고, 컬렉션과 실제 검색 테스트는 토픽 분리와 Ingestion을 한 뒤에 진행하시면 됩니다.
