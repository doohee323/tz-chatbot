# 슬라이드 01: chat-gateway 역할과 복수 앱 지원

## 슬라이드 내용 (한 장)

**chat-gateway 역할**
• **채팅 API 단일 진입점**: DrillQuiz·CoinTutor 등 여러 클라이언트 앱이 각각 Dify에 붙지 않고 gateway로만 요청
• system_id에 따라 해당 Dify 앱·API Key 선택 후 Dify API 호출
• 대화·메시지 DB 저장, JWT로 사용자·앱 구분

**API 엔드포인트**
• 채팅: `/chat` (페이지), `/chat-api` (별칭), `/v1/chat` (메시지 전송)
• 대화 조회: `/v1/conversations`, `/v1/conversations/{id}/messages`
• 토큰: `/v1/chat-token` (JWT 발급), `/v1/chat-token-guest` (guest 토큰)
• 캐시: `/cache` (히스토리 UI), `/v1/cache/conversations`, `/v1/cache/conversations/{id}/messages`
• 관리: `/v1/admin/register`, `/v1/admin/login` (관리자 회원가입/로그인)
• 동기화: `/v1/sync` (Dify→DB 동기화)

**복수 앱 지원: DB·배치**  
• **chat_admin DB**: chat-gateway·chat-admin 공유. 시스템(앱) 등록·설정, 대화·메시지 저장·조회. system_id 단위로 Dify URL·API Key 저장  
• **배치**: POST /v1/sync으로 Dify→DB 주기 동기화(cron). 토픽별 RAG Ingestion CronJob. 관리 화면에서 재색인 트리거(Job 생성)

**chat-admin 관리 화면**  
• 시스템(앱) CRUD, 채팅 조회(system_id·user_id), RAG 문서 업로드·재색인 트리거, 테스트 JWT 발급. Vue+FastAPI, 로컬 SQLite / K8s PostgreSQL(chat_admin)

---

## 발표 노트

chat-gateway는 채팅 API의 단일 진입점입니다. DrillQuiz나 CoinTutor 같은 여러 클라이언트 앱이 각각 Dify에 직접 붙지 않고, gateway 한 곳으로만 요청을 보냅니다. gateway는 system_id를 보고 해당 Dify 앱과 API Key를 선택해서 Dify API를 호출합니다. 대화와 메시지는 DB에 저장하고, JWT로 사용자와 앱을 구분합니다. /chat은 채팅 페이지, /v1/chat은 메시지 전송, /v1/conversations는 대화 목록, /v1/chat-token은 앱에서 채팅 페이지 링크를 만들 때 쓸 JWT 발급 API입니다.

복수 앱을 지원하려면 DB와 배치가 필요합니다. chat_admin이라는 PostgreSQL DB를 chat-gateway와 chat-admin이 같이 씁니다. 시스템, 즉 앱 등록과 설정, 그리고 대화·메시지를 저장하고 조회합니다. system_id 단위로 Dify URL이랑 API Key를 저장해 두고, gateway가 그걸 보고 Dify를 호출합니다. 배치로는 chat-gateway의 POST /v1/sync을 cron 등으로 주기 호출해서 Dify 쪽 대화·메시지를 DB로 가져옵니다. 토픽별 RAG Ingestion은 CronJob으로 이미 다뤘고, 관리 화면에서 재색인 버튼을 누르면 해당 토픽의 Ingestion Job을 한 번 생성하는 식으로 트리거합니다.

chat-admin은 관리 화면입니다. 시스템, 즉 앱 CRUD, system_id·user_id로 채팅 조회, RAG 문서 업로드와 재색인 트리거, 테스트용 JWT 발급을 할 수 있습니다. Vue와 FastAPI로 되어 있고, 로컬에서는 SQLite, K8s에서는 PostgreSQL의 chat_admin DB를 쓰도록 설정합니다.
