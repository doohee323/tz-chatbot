# 01. chat-gateway 역할

## 역할

- **채팅 API의 단일 진입점**: DrillQuiz, CoinTutor 등 **여러 클라이언트 앱**이 각각 Dify에 직접 붙지 않고, **chat-gateway** 한 곳으로만 요청을 보냅니다.
- gateway가 **system_id**(앱 구분)에 따라 해당 Dify 앱·API Key를 선택해 Dify API를 호출합니다.
- 대화·메시지를 **DB에 저장**하고, **JWT**로 사용자·앱을 구분해 채팅 페이지(`/chat`) 또는 API(`/v1/chat`, `/v1/conversations`)를 제공합니다.

## 제공 API 예

### 채팅 API
- **POST /v1/chat**: 메시지 전송 (body: system_id, user_id, message)
- **GET /v1/conversations**: 대화 목록 (query: system_id, user_id)
- **GET /v1/conversations/{id}/messages**: 특정 대화의 메시지 목록

### 채팅 페이지 및 토큰
- **GET /chat**: 쿼리 `token=<JWT>` — 채팅 UI 페이지 (Vue SPA)
- **GET /chat-api**: `/chat`의 별칭
- **GET /v1/chat-token**: system_id, user_id로 JWT 발급 (외부 앱이 채팅 페이지 링크를 만들 때 사용)
- **POST /v1/chat-token-guest**: guest 토큰 발급 (origin 제한 사용, API Key 불필요)

### 대화 캐시 및 히스토리
- **GET /cache**: 대화 히스토리 웹 UI (쿼리: api_key, system_id, user_id, date range)
- **GET /v1/cache/conversations**: 캐시된 대화 목록 (X-API-Key 필수)
- **GET /v1/cache/conversations/{id}/messages**: 캐시된 메시지 조회

### 관리자 기능
- **POST /v1/admin/register**: 관리자 회원가입 (body: username, password)
- **POST /v1/admin/login**: 관리자 로그인 (body: username, password → access_token)

## 인증

- **API Key**: Header `X-API-Key` (서비스 간 호출)
- **JWT**: query `token` 또는 Header `Authorization: Bearer <jwt>` (채팅 페이지·앱에서 발급한 토큰)
- JWT payload: system_id, user_id, exp (동일한 CHAT_GATEWAY_JWT_SECRET으로 앱에서 서명해 발급)
