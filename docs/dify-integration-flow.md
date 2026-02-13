# Chat-Gateway ↔ Dify 연동 흐름

코드 기준으로 현재 Dify와 통합되는 부분을 정리한 문서다.

---

## 1. 설정이 어디서 오는지

| 용도 | 우선순위 | 출처 |
|------|----------|------|
| **Base URL** | 1) DB | `chat_systems.dify_base_url` (system_id별) |
| | 2) env | `DIFY_<system_id>_BASE_URL` (예: `DIFY_DRILLQUIZ_BASE_URL`) → 없으면 `DIFY_BASE_URL` |
| **API Key** | 1) DB | `chat_systems.dify_api_key` |
| | 2) env | `DIFY_<system_id>_API_KEY` → 없으면 `DIFY_API_KEY` |
| **chat-token 허용 키** | env + DB | `CHAT_GATEWAY_API_KEY`(쉼표 구분) + DB `dify_chatbot_token` |

- **DB** (`chat_systems`): chat-admin에서 시스템 등록 시 저장. 테이블이 없거나 비어 있으면 **env fallback** 사용.
- **env**: `app/config.py`의 `Settings`. per-system으로 `DIFY_DRILLQUIZ_*`, `DIFY_COINTUTOR_*` 선언돼 있음.

**코드 위치**
- 설정 읽기: `app/services/system_config.py` — `get_dify_base_url()`, `get_dify_api_key()`
- env 필드: `app/config.py` — `dify_base_url`, `dify_api_key`, `dify_drillquiz_*`, `dify_cointutor_*`

---

## 2. Dify를 호출하는 곳

모든 호출은 `app/dify_client.py`를 거친다.

| API | 함수 | URL (base from config) | 용도 |
|-----|------|------------------------|------|
| 채팅 전송 | `send_chat_message()` | `POST {base}/v1/chat-messages` | `POST /v1/chat` 처리 시 |
| 대화 목록 | `get_conversations()` | `GET {base}/v1/conversations` | 캐시/동기화, 대화 목록 API |
| 메시지 목록 | `get_conversation_messages()` | `GET {base}/v1/messages` | 캐시/동기화, 메시지 조회 |
| 대화 삭제 | `delete_conversation()` | `DELETE {base}/v1/conversations/{id}` | 대화 삭제 API |

**Base URL**  
- `get_dify_base_url(system_id)` → `{base}` (끝 `/` 제거)  
- 실제 요청: `{base}/v1/...` (예: `https://dify.drillquiz.com/v1/chat-messages`)

**인증**  
- `Authorization: Bearer {get_dify_api_key(system_id)}`  
- Dify 앱의 **API Key** (스튜디오 → API Access) 사용. Chatbot Token(임베드)과 다름.

---

## 3. POST /v1/chat → Dify 한 번에 보내는 것

**진입점**: `app/routers/chat.py` → `post_chat()`

1. **identity 결정**  
   - JWT 있음 → `system_id`, `user_id`는 토큰에서.  
   - API Key만 있음 → body 또는 query의 `system_id`, `user_id` 필수.
2. **Dify 설정 확인**  
   - `get_dify_api_key(ident.system_id)`, `get_dify_base_url(ident.system_id)`  
   - 둘 중 하나라도 비면 503.
3. **Dify 호출**  
   - `send_chat_message(`  
     - `user=ident.dify_user` → `"{system_id}_{user_id}"` (예: `drillquiz_test-user-001`)  
     - `query=body.message`  
     - `conversation_id=body.conversation_id` (이어하기 시)  
     - `inputs=body.inputs`  
     - `response_mode="blocking"`  
     - `system_id=ident.system_id`  
   - )
4. **Dify 응답 사용**  
   - `conversation_id`, `message_id`, `answer`, `metadata`  
   - DB 기록, MinIO 기록(백그라운드), 클라이언트에 그대로 반환.

**dify_client 실제 요청**
- URL: `get_dify_base_url(system_id) + "/v1/chat-messages"`
- Headers: `Authorization: Bearer {get_dify_api_key(system_id)}`, `Content-Type: application/json`
- Body: `{ "inputs": {}, "query": "...", "response_mode": "blocking", "user": "drillquiz_user-123" }` (+ 선택 `conversation_id`)

---

## 4. 현재 .env 기준으로 쓰이는 값

| system_id | Base URL | API Key |
|-----------|----------|---------|
| drillquiz | `DIFY_BASE_URL` = https://dify.drillquiz.com | `DIFY_DRILLQUIZ_API_KEY` |
| cointutor | `DIFY_BASE_URL` = https://dify.drillquiz.com | `DIFY_COINTUTOR_API_KEY` |

- `DIFY_DRILLQUIZ_BASE_URL` / `DIFY_COINTUTOR_BASE_URL` 없으면 공용 `DIFY_BASE_URL` 사용.
- 두 system_id 모두 **같은 Dify 호스트**, **앱만 다른 키**로 구분하는 구조.

---

## 5. Dify 쪽에서 사용하는 토큰 정리

| 이름 | 어디서 쓰는지 | chat-gateway 사용 여부 |
|------|----------------|-------------------------|
| **API Key** (app-xxx) | Dify **API** 호출 시 `Authorization: Bearer` | ✅ 사용. `get_dify_api_key(system_id)` → 모든 Dify API 호출에 사용 |
| **Chatbot Token** (임베드) | Dify **웹/임베드** 채팅에서 클라이언트가 Dify 직접 호출할 때 | ❌ gateway가 Dify 호출할 때는 사용 안 함. `/v1/chat-token` 허용 키로만 DB의 `dify_chatbot_token` 사용 |

즉, **지금 연동되는 부분은 전부 Dify API Key**이고, Chatbot Token은 gateway가 Dify로 요청 보낼 때는 쓰이지 않는다.

---

## 6. 참고 코드 경로

- Dify 호출: `app/dify_client.py`
- 채팅 라우트·identity·설정 사용: `app/routers/chat.py`
- Base URL / API Key 결정: `app/services/system_config.py` + `app/config.py`
- identity·dify_user: `app/auth.py` (`ChatIdentity.dify_user`)
