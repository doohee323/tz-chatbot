# 슬라이드 01: RAG 설치 개요와 install.sh

## 슬라이드 내용 (한 장)

**RAG 스택 구성**  
• Qdrant(벡터 DB), RAG Backend(토픽별 Deployment), RAG Frontend(선택), RAG Ingestion(Job/CronJob), Ingress  
• 설치 진입점: rag/install.sh (RAG만) 또는 bootstrap.sh(전체 중 3단계로 호출)

**install.sh**  
• namespace rag 생성 → Qdrant Helm → 컬렉션 생성 Job → RAG Backend·Frontend·Ingress → Ingestion Job/CronJob(토픽별)  
• MinIO가 devops에 있어야 함. Ingress NGINX 있으면 RAG Ingress 동작  
• 실행: `cd tz-chatbot/rag && bash install.sh` (KUBECONFIG 설정 후)

**설치 후 필수**  
• 토픽별 Secret 생성: rag-ingestion-secret-cointutor, rag-ingestion-secret-drillquiz (MinIO 접근 키, Gemini 또는 OpenAI API Key). 없으면 Backend Pod 기동 실패·검색 시 "API key not valid"  
• Qdrant 컬렉션: qdrant-collection-init Job으로 rag_docs_cointutor, rag_docs_drillquiz 생성

---

## 발표 노트

RAG 스택은 Qdrant라는 벡터 DB, RAG Backend가 토픽별로 Deployment로 있고, RAG Frontend는 선택이고, RAG Ingestion은 Job과 CronJob으로 되어 있으며, Ingress로 노출합니다. 설치 진입점은 rag 폴더의 install.sh입니다. RAG만 설치할 때는 이걸 실행하고, bootstrap.sh를 쓰면 전체 설치의 3단계에서 이 스크립트를 호출합니다.

install.sh가 하는 일을 보면, 먼저 namespace rag를 만들고, Qdrant를 Helm으로 설치하고, 컬렉션 생성 Job으로 rag_docs_cointutor, rag_docs_drillquiz를 만듭니다. 그다음 RAG Backend와 Frontend, Ingress를 적용하고, 토픽별 Ingestion Job·CronJob을 넣습니다. ingest 스크립트나 requirements는 ConfigMap으로 올라가서 Job 안에서 사용됩니다. 실행할 때는 MinIO가 이미 devops 네임스페이스에 설치되어 있어야 하고, Ingress NGINX가 있으면 RAG용 Ingress가 동작합니다. KUBECONFIG를 설정한 뒤 tz-chatbot/rag로 가서 bash install.sh 하시면 됩니다.

설치가 끝난 뒤에는 반드시 토픽별 Secret을 만들어 두셔야 합니다. rag-ingestion-secret-cointutor, rag-ingestion-secret-drillquiz가 필요하고, MinIO 접근 키와 Gemini 또는 OpenAI API Key를 넣습니다. 이게 없으면 RAG Backend Pod가 기동하지 않거나 검색할 때 API key not valid 같은 오류가 납니다. Qdrant 컬렉션은 install.sh에 포함된 qdrant-collection-init Job이 성공하면 rag_docs_cointutor, rag_docs_drillquiz가 생성됩니다. Secret 생성 예시는 rag/README에 나와 있으니 그대로 따라 하시면 됩니다.
