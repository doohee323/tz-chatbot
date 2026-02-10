# 04. JWT와 대화 관리

## JWT 용도

- **채팅 페이지 접근**: `/chat?token=<JWT>` — 토큰에 system_id, user_id, exp가 들어 있으면 해당 사용자·앱으로 채팅
- **발급 주체**: chat-admin(테스트용), 또는 **클라이언트 앱 백엔드**가 같은 **CHAT_GATEWAY_JWT_SECRET**으로 서명해 발급
- 클라이언트 앱은 “채팅 열기” 버튼 클릭 시 백엔드에서 JWT 발급 → 리다이렉트 또는 iframe으로 gateway `/chat?token=...` 열기

## 대화 관리

- **저장**: chat-gateway가 Dify로 보낸/받은 메시지를 DB에 저장 (설정에 따라)
- **조회**: `/v1/conversations`, `/v1/conversations/{id}/messages` — API Key 또는 JWT로 system_id·user_id 기준 조회
- **동기화**: POST /v1/sync 로 Dify 쪽 대화·메시지를 주기적으로 DB로 가져와 캐시/관리자 조회에 사용
- **관리자**: chat-admin에서 system_id·user_id로 대화 목록·메시지 조회, 필요 시 삭제
