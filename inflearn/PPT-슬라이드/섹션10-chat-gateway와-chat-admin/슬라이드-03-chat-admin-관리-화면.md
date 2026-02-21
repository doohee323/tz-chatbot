# 슬라이드 03: chat-admin 관리 화면

## 슬라이드 내용 (한 장)

**chat-admin 역할**
• **시스템(앱) CRUD**: 새 챗봇 앱(system_id) 등록, Dify URL·API Key·챗봇 토큰 설정, 수정·삭제
• **채팅 조회**: system_id·user_id 기준으로 대화 목록·메시지 조회
• **RAG 관리**: 토픽별 MinIO에 파일 업로드, 재색인 Job 수동 실행
• **관리자 인증**: 회원가입/로그인 후 관리 화면 접근. chat-gateway와 같은 PostgreSQL DB(chat_admin) 공유

**기술 스택**
• Backend: FastAPI (Python 3.11+)
• Frontend: Vue
• DB: 로컬 SQLite / K8s PostgreSQL (chat_admin)

**포트**: 로컬 8000 (또는 `CHAT_ADMIN_PORT` 환경변수로 변경)

---

## 발표 노트

chat-admin은 이 전체 시스템의 관리 화면입니다. 시스템, 즉 새로운 챗봇 앱을 등록하고 관리할 수 있습니다. DrillQuiz나 CoinTutor 같은 앱을 system_id로 추가할 때, Dify URL과 API Key, 챗봇 토큰 같은 것들을 설정하는 거죠. 수정이나 삭제도 여기서 합니다.

채팅 조회 기능은 system_id와 user_id를 기준으로 그동안 나눈 대화를 보는 것입니다. chat-gateway에서 저장한 대화들을 여기서 조회합니다.

RAG 관리는 문서를 MinIO에 업로드하고, 필요할 때 재색인 Job을 수동으로 돌릴 수 있다는 뜻입니다. 토픽별로 DrillQuiz 문서와 CoinTutor 문서를 분리해서 올릴 수 있습니다.

관리자 인증은 중요한 부분입니다. 관리 화면에 들어가려면 먼저 회원가입을 해서 username과 password를 만든 뒤, 로그인해야 합니다. 그럼 access_token을 받고 관리 화면에 접근할 수 있습니다.

기술 스택으로는 Backend는 FastAPI로 Python 3.11 이상을 씁니다. Frontend는 Vue입니다. DB는 로컬에서는 SQLite를 쓰고, K8s 환경에서는 PostgreSQL의 chat_admin DB를 쓰도록 설정합니다. 이 chat_admin DB는 chat-gateway도 함께 씁니다.

로컬에서는 기본 포트 8000으로 떠있으니까, ./admin.sh로 띄운 뒤 http://localhost:8000으로 접속하시면 됩니다. 포트를 바꾸고 싶으면 CHAT_ADMIN_PORT 환경변수로 설정할 수 있습니다.
