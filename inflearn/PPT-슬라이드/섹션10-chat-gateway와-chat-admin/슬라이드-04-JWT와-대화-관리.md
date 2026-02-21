# 슬라이드 04: JWT와 대화 관리

## 슬라이드 내용 (한 장)

**JWT (사용자 인증)**
• `/chat?token=<JWT>` — JWT payload: system_id, user_id, exp
• 클라이언트 앱 백엔드가 CHAT_GATEWAY_JWT_SECRET으로 서명해 발급
• 사용자를 채팅 페이지로 리다이렉트/링크/iframe

**대화 저장 및 조회**
• **저장**: chat-gateway가 Dify 메시지를 DB에 저장 (설정 따라)
• **조회**: `/v1/conversations`, `/v1/conversations/{id}/messages` (API Key 또는 JWT)
• **동기화**: `POST /v1/sync` — Dify → DB 주기 동기화
• **관리자 조회**: chat-admin에서 system_id·user_id로 대화·메시지 조회·삭제

---

## 발표 노트

JWT는 채팅 페이지 접근을 위한 토큰입니다. 사용자가 채팅을 하려면 `/chat?token=<JWT>` 형태로 URL을 만들어야 합니다. JWT 안에는 어떤 시스템(system_id), 어떤 사용자(user_id)인지, 그리고 토큰 만료 시간(exp)이 들어 있습니다.

JWT는 클라이언트 앱의 백엔드에서 발급합니다. DrillQuiz 백엔드가 "사용자가 채팅을 열겠다"라는 요청을 받으면, CHAT_GATEWAY_JWT_SECRET이라는 비밀 키로 JWT를 서명해서 만듭니다. 그리고 그 JWT를 포함한 URL을 사용자의 브라우저로 보내 리다이렉트하거나, 또는 iframe으로 이 URL을 열어서 채팅 페이지를 보여줍니다.

대화 관리 부분입니다. chat-gateway는 Dify로 보낸 메시지와 받은 응답을 설정에 따라 DB에 저장합니다. 조회는 `/v1/conversations`로 대화 목록을 조회할 수 있고, `/v1/conversations/{id}/messages`로 특정 대화 안의 메시지들을 조회합니다. 이때 조회 권한은 API Key 또는 JWT로 확인합니다.

Dify 쪽과 DB를 맞추기 위해 주기적으로 동기화를 합니다. `POST /v1/sync`를 cron 같은 걸로 주기적으로 호출하면, Dify에 있는 대화와 메시지를 gateway DB로 가져옵니다. 이렇게 하면 관리자가 나중에 chat-admin에서 대화를 조회할 수 있고, 캐시로 관리할 수 있습니다.

관리자는 chat-admin에서 system_id와 user_id를 선택해서 해당 사용자의 대화 목록과 각 대화의 메시지들을 조회할 수 있습니다. 필요하면 대화를 삭제할 수도 있습니다.
