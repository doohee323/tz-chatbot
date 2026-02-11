# 슬라이드 01: 필수 도구와 Git·환경 설정

## 슬라이드 내용 (한 장)

**필수: kubectl, KUBECONFIG**  
• kubectl: K8s 클러스터와 통신하는 CLI. `kubectl get nodes` 로 확인  
• KUBECONFIG: 클러스터·인증 설정. 기본 ~/.kube/config. 다른 설정 시 `export KUBECONFIG=경로`  
• bootstrap·install.sh 등은 이 환경변수 사용 (미설정 시 기본값)

**Git 저장소·환경 설정**  
• `git clone <tz-chatbot URL>` 후 사용 브랜치 확인 (main/dev/qa → 배포 NS·시크릿 접미사)  
• 로컬 실행 시: chat-gateway·chat-admin 각 디렉터리 .env 또는 환경변수 (DIFY_BASE_URL, DIFY_API_KEY, CHAT_GATEWAY_JWT_SECRET, DATABASE_URL 등. 각 README 참고)  
• RAG Ingestion 로컬 실행 시: MinIO·Qdrant·API Key 환경변수

**최소 확인**: `kubectl get nodes`, `kubectl get ns` 성공 시 실습 진행 가능

---

## 발표 노트

로컬·개발 환경 준비에서 먼저 필요한 것은 kubectl과 KUBECONFIG입니다. kubectl은 Kubernetes 클러스터와 통신하는 CLI이고, 버전 확인은 kubectl version --client로 하시면 됩니다. KUBECONFIG는 어떤 클러스터에 접속할지, 인증 정보는 무엇인지 담긴 설정 파일입니다. 기본 경로는 ~/.kube/config이고, 다른 설정 파일을 쓰려면 export KUBECONFIG=경로 로 지정하시면 됩니다. bootstrap.sh나 install.sh는 이 환경변수를 따르고, 없으면 기본값을 씁니다. 최소한 kubectl get nodes와 kubectl get ns가 성공하면 실습을 진행하실 수 있습니다.

Git 저장소는 clone 하신 뒤에 사용하실 브랜치를 확인하세요. main, dev, qa에 따라 배포 네임스페이스나 시크릿 접미사가 달라질 수 있어서 README에 나온 Branches and namespaces 표를 보시면 됩니다. 로컬에서 chat-gateway나 chat-admin을 실행하실 때는 각 디렉터리에 .env 파일을 두거나 환경변수로 DIFY_BASE_URL, DIFY_API_KEY, CHAT_GATEWAY_JWT_SECRET, DATABASE_URL 같은 값을 설정하시면 됩니다. 필요한 변수 목록은 chat-gateway README, chat-admin README에 정리되어 있습니다. RAG Ingestion을 로컬에서 돌리실 때는 MinIO 접속 정보, Qdrant, API Key를 환경변수로 넣어 주셔야 합니다.
