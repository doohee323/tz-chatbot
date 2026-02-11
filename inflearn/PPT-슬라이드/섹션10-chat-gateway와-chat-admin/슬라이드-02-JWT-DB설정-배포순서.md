# 슬라이드 02: JWT·DB 설정·배포 순서

## 슬라이드 내용 (한 장)

**JWT·대화 관리**  
• /chat 접근: /chat?token=<JWT>. JWT payload: system_id, user_id, exp. 같은 CHAT_GATEWAY_JWT_SECRET으로 앱 백엔드가 서명해 발급 → 사용자를 채팅 페이지로 보냄  
• 대화: gateway가 Dify로 보낸/받은 메시지 DB 저장(설정에 따라). /v1/conversations, /v1/conversations/{id}/messages로 조회. POST /v1/sync으로 Dify→DB 동기화

**DB 설정 (chat_admin)**  
• PostgreSQL DB 이름: chat_admin. bootstrap에 DB 생성 없음 → 수동 생성  
• 예: kubectl exec로 postgres Pod 접속 후 CREATE DATABASE chat_admin; (비밀번호는 chat-admin Secret에서). 앱 배포 시 POSTGRES_* 환경변수 또는 Secret으로 접속 정보 전달

**배포 순서**  
1. 인프라(bootstrap.sh) 2. DB(chat_admin) 생성 3. Secret(chat-admin·chat-gateway용) 4. 앱 배포(k8s.sh 또는 ci.sh, Jenkins 없이 로컬 가능) 5. Ingress(admin·gateway 호스트)  
• 서버 배포 방법 상세( k8s.sh, Jenkins, ci.sh·k8s.sh만·다른 CI)는 이전 “서버 배포 방법” 슬라이드 참고

---

## 발표 노트

JWT는 채팅 페이지 접근용입니다. 사용자가 /chat을 쓸 때는 query에 token=<JWT>를 붙입니다. JWT 안에는 system_id, user_id, exp가 들어 있고, 클라이언트 앱 백엔드가 CHAT_GATEWAY_JWT_SECRET으로 서명해서 발급합니다. 그래서 사용자를 채팅 페이지로 리다이렉트하거나 링크를 줄 때 이 JWT URL을 넘기면 됩니다. 대화 관리는 gateway가 Dify로 보내고 받은 메시지를 설정에 따라 DB에 저장하고, /v1/conversations나 /v1/conversations/{id}/messages로 조회합니다. Dify 쪽과 맞추려면 POST /v1/sync을 주기적으로 호출해서 Dify에서 DB로 동기화합니다.

DB는 chat_admin이라는 PostgreSQL DB를 쓰고, chat-gateway와 chat-admin이 같이 씁니다. bootstrap.sh에는 DB 생성이 없으니까 수동으로 만드셔야 합니다. 예를 들어 PostgreSQL이 들어 있는 Pod에 kubectl exec로 접속해서 CREATE DATABASE chat_admin; 하시면 되고, 비밀번호는 chat-admin Secret에서 가져와서 같은 걸 쓰시면 앱과 맞습니다. 앱 배포할 때는 POSTGRES_HOST, POSTGRES_PORT 같은 환경변수나 Secret으로 이 접속 정보를 넘깁니다.

배포 순서는 인프라를 bootstrap으로 올린 뒤, chat_admin DB를 만들고, chat-admin·chat-gateway용 Secret을 만든 다음, k8s.sh나 ci.sh로 앱을 배포하고, admin·gateway용 Ingress 규칙을 적용하시면 됩니다. Jenkins 없이 로컬에서 ci.sh나 k8s.sh만 쓰는 방법을 포함한 서버 배포 방법 상세는 앞에서 다룬 “서버 배포 방법” 슬라이드를 참고하시면 됩니다.
