# 03. chat-admin 관리 화면

## 역할

- **시스템(앱) CRUD**: 새 챗봇 앱(system_id) 등록, Dify URL·API Key·챗봇 토큰 설정, 수정·삭제
- **채팅 조회**: system_id·user_id 기준으로 대화 목록·메시지 조회 (Dify 또는 DB 캐시)
- **RAG 문서 업로드**: 토픽(system_id)별로 MinIO `raw/{system_id}/` 에 파일 업로드
- **재색인 트리거**: 업로드 후 해당 토픽의 RAG Ingestion Job을 수동 실행
- **테스트 토큰 발급**: 관리자가 해당 시스템용 JWT를 발급해 채팅 페이지 바로 열기

## 기술 스택

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Vue (채팅 페이지·관리 UI)
- **DB**: 로컬은 SQLite, K8s는 PostgreSQL(chat_admin)
- **인증**: 관리자 회원가입/로그인, JWT로 채팅 페이지 접근

## 관리자 회원가입/로그인

chat-admin은 **관리자**만 접근 가능하도록 인증을 요구합니다:

### 1단계: 회원가입
```bash
# K8s 환경: Ingress 접근
# 또는 로컬: ./admin.sh 후 http://localhost:8000 접근

# UI에서 우측 상단 "회원가입" 클릭
# username, password 입력 후 가입
```

### 2단계: 로그인
- 가입한 username/password로 로그인
- access_token 발급 (DB에 저장)
- 관리 화면(시스템 CRUD, 채팅 조회, RAG 업로드) 접근 가능

## 접근

- **K8s 배포**: Ingress로 `https://<admin-host>/` 제공
- **로컬 테스트**: `cd chat-admin && ./admin.sh` 후 `http://localhost:8000/` (또는 환경변수로 포트 변경)
- **chat-gateway와의 관계**: chat-admin과 chat-gateway는 **같은 PostgreSQL DB(chat_admin)**를 공유
  - chat-admin: 시스템 등록·관리, 채팅 조회
  - chat-gateway: 실제 채팅 API, 대화·메시지 저장

## chat-gateway 제공 API (관리자 토큰 발급)

chat-admin에서 특정 사용자를 위한 테스트 토큰을 발급할 때:

```bash
# chat-gateway의 JWT 발급 API 호출
curl -X GET \
  "http://localhost:8088/v1/chat-token?system_id=drillquiz&user_id=user123" \
  -H "X-API-Key: <CHAT_GATEWAY_API_KEY>"

# 응답: JWT 토큰 → chat page URL에 붙여서 제공
```
