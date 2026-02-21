# 슬라이드 05: DB 설정 (chat_admin)

## 슬라이드 내용 (한 장)

**chat_admin DB 생성**
• PostgreSQL DB 이름: `chat_admin`
• **bootstrap.sh에 포함 안됨** — 수동 생성 필요
• 예: `kubectl exec` 로 postgres Pod 접속 후 `CREATE DATABASE chat_admin;`
• Secret에서 비밀번호 가져오기: `chat-admin-secret-main` (또는 -qa, -dev)

**환경변수 설정 (K8s)**
• POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB=chat_admin
• Secret 또는 ConfigMap으로 전달 (app 배포 시)
• 같은 비밀번호를 chat-gateway·chat-admin이 공유 (Secret 동일)

**배포 순서**
1. 인프라 (bootstrap.sh)
2. PostgreSQL이 있는 NS에서 chat_admin DB 생성
3. Secret (chat-admin-secret-*, chat-gateway-secret) 생성
4. chat-admin·chat-gateway Deployment 배포 (k8s.sh 또는 ci.sh)

---

## 발표 노트

chat_admin은 chat-gateway와 chat-admin이 공유하는 PostgreSQL DB입니다. 이름은 그냥 `chat_admin`이고, bootstrap.sh 스크립트에는 DB 생성이 포함되어 있지 않습니다. 그래서 수동으로 만들어야 합니다.

생성 방법은 PostgreSQL이 설치되어 있는 Pod에 `kubectl exec`으로 접속해서 `CREATE DATABASE chat_admin;`이라고 명령을 내리면 됩니다. 비밀번호는 chat-admin-secret-main 같은 Secret에 POSTGRES_PASSWORD로 저장되어 있으니까 그걸 Base64 디코딩해서 가져오면 됩니다. 브랜치가 main이면 -main, qa면 -qa, dev면 -dev 이런 식으로 Secret 이름이 달라집니다.

앱을 배포할 때는 POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB 같은 환경변수를 전달해야 합니다. 이건 Secret이나 ConfigMap으로 Deployment에 주입합니다. 중요한 건 chat-gateway와 chat-admin이 같은 비밀번호를 써야 한다는 것입니다. 같은 Secret을 참조하도록 설정하면 됩니다.

배포 순서는 먼저 bootstrap.sh로 인프라를 올리고, PostgreSQL이 있는 네임스페이스에서 chat_admin DB를 생성한 뒤, 필요한 Secret들을 만들고, 마지막으로 k8s.sh나 ci.sh로 chat-admin과 chat-gateway를 배포합니다. Secret의 비밀번호가 DB 생성 시 사용한 비밀번호와 일치해야 앱이 정상적으로 연결됩니다.
