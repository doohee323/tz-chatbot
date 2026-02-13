# Using the chat gateway from CoinTutor

How to open the gateway chat page (`/chat?token=<JWT>`) from CoinTutor.  
**Prerequisite**: The chat gateway and CoinTutor must share the **same JWT_SECRET**.

---

## 1. Flow summary

1. User is logged into CoinTutor and clicks "Open chat" (or similar).
2. CoinTutor **backend** issues a **JWT** for the current user (payload: `system_id`, `user_id`, `exp`).
3. CoinTutor **frontend** navigates to `https://<gateway-host>/chat?token=<JWT>` (link, redirect, or iframe).
4. Gateway validates the JWT and shows the Dify chat page.

---

## 2. CoinTutor backend: issuing JWT

Store the gateway `.env` **JWT_SECRET** in CoinTutor config (env or config file) and create the JWT as below.

**Payload example** (HS256):

- `system_id`: `"cointutor"` (fixed)
- `user_id`: CoinTutor logged-in user ID (string)
- `exp`: Expiry time (Unix timestamp, e.g. now + 1 hour)

**Example (Python)**:

```python
import jwt
import time

JWT_SECRET = "..."  # Same as gateway .env
GATEWAY_CHAT_URL = "https://chat-admin.example.com"  # Actual gateway URL

def get_chat_url(user_id: str, expires_in_seconds: int = 3600) -> str:
    payload = {
        "system_id": "cointutor",
        "user_id": str(user_id),
        "exp": int(time.time()) + expires_in_seconds,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if hasattr(token, "decode"):
        token = token.decode("utf-8")
    return f"{GATEWAY_CHAT_URL}/chat?token={token}"
```

**Example (Node.js)**:

```javascript
const jwt = require('jsonwebtoken');

const JWT_SECRET = '...';  // Same as gateway .env
const GATEWAY_CHAT_URL = 'https://chat-admin.example.com';

function getChatUrl(userId, expiresInSeconds = 3600) {
  const token = jwt.sign(
    {
      system_id: 'cointutor',
      user_id: String(userId),
      exp: Math.floor(Date.now() / 1000) + expiresInSeconds,
    },
    JWT_SECRET,
    { algorithm: 'HS256' }
  );
  return `${GATEWAY_CHAT_URL}/chat?token=${token}`;
}
```

Expose one **API endpoint** in CoinTutor, e.g.:

- `GET /api/chat-url` or `GET /api/me/chat-url`  
  - Read `user_id` from the login session → build URL with the function above → return `{ "url": "https://.../chat?token=..." }`.

---

## 3. CoinTutor frontend: opening chat

### Option A: Link (new tab)

- Set the chat URL on a button/menu link with `target="_blank"`.
- Frontend gets the URL by calling backend `GET /api/chat-url`.

```html
<a id="open-chat" href="#" target="_blank">Open chat</a>
<script>
  fetch('/api/chat-url')
    .then(r => r.json())
    .then(data => { document.getElementById('open-chat').href = data.url; });
</script>
```

### Option B: Redirect

- On "Open chat" click, navigate the current window to the chat URL.

```javascript
fetch('/api/chat-url')
  .then(r => r.json())
  .then(data => { window.location.href = data.url; });
```

### Option C: iframe

- When you want chat embedded inside a CoinTutor page.

```html
<iframe id="chat-frame" style="width:100%; height:600px; border:0;"></iframe>
<script>
  fetch('/api/chat-url')
    .then(r => r.json())
    .then(data => { document.getElementById('chat-frame').src = data.url; });
</script>
```

---

## 4. Setup checklist

| Item | Check |
|------|-------|
| Gateway `.env` `JWT_SECRET` | **Exactly the same** as CoinTutor backend config |
| Gateway `.env` `ALLOWED_SYSTEM_IDS` | Includes `cointutor` (empty = allow all) |
| Chat URL | Use real gateway URL (local: `http://localhost:8000`, prod: `https://...`) |
| JWT expiry | Keep short (e.g. 1 hour); refresh when needed |

---

## 5. Summary

- CoinTutor does **not** need to know Dify API keys or embed tokens; only the gateway.
- User identity is **JWT `system_id` + `user_id`**; the gateway uses Dify `user` as `cointutor_<user_id>`.
- Other services (e.g. DrillQuiz) can use the same pattern with a different `system_id`.

---

## 6. 브라우저에서 채팅 요청 확인

채팅 시 실제로 나가는 요청은 **채팅 UI가 열린 도메인**에서 나갑니다.  
CoinTutor가 링크/리다이렉트/iframe으로 **gateway 채팅 페이지**를 열었다면, 요청은 **gateway 호스트**(예: `https://chat.xxx.com`)로 나가며, `cointutor.net` 도메인으로의 채팅 API 호출은 없습니다.

### 6.1 채팅 시 나가는 요청 (gateway 연동 시)

| 항목 | 내용 |
|------|------|
| **URL** | `{gateway 기준 URL}/v1/chat` (예: `https://chat.xxx.com/v1/chat`) |
| **Method** | `POST` |
| **Headers** | `Authorization: Bearer <JWT>`, `Content-Type: application/json` |
| **Body** | `{ "message": "사용자 입력", "inputs": { "language": "ko" } }` (대화 이어갈 때는 `conversation_id` 포함) |

- `system_id`(예: `cointutor`)는 **JWT payload**에 들어 있으며, 요청 body/query가 아님.
- Gateway가 JWT를 검증·복호화해 `system_id`, `user_id`를 쓰고, DB 기록·MinIO 기록 시 `system_id=cointutor`로 저장.

### 6.2 DevTools에서 확인하는 방법

1. **CoinTutor에서 채팅 열기**: CoinTutor가 gateway URL로 열었다면 (새 탭/iframe 모두) 해당 탭에서 진행.
2. **개발자 도구** 열기 (F12 또는 우클릭 → 검사).
3. **Network** 탭 선택 → **Preserve log** 체크.
4. 채팅 입력 후 전송.
5. 목록에서 **`chat`** 또는 gateway 호스트 이름으로 필터.
6. **`v1/chat`** (POST) 요청 선택 후 확인:
   - **Request URL**: `https://<gateway-host>/v1/chat`
   - **Request Headers**: `Authorization: Bearer eyJ...`
   - **Payload**: `message`, `inputs.language`, (선택) `conversation_id`

JWT payload에서 `system_id` 확인: [jwt.io](https://jwt.io)에 토큰 붙여넣고 Payload의 `system_id`가 `cointutor`인지 확인.

### 6.3 cointutor.net에서 요청이 안 보일 때

- 채팅 UI가 **Dify 임베드만** 쓰고 gateway를 거치지 않으면, 요청은 Dify 도메인으로만 나가고 gateway/MinIO에는 기록되지 않습니다.
- 이 경우 CoinTutor 쪽에서 채팅 진입점을 **gateway 채팅 URL**(JWT 포함)로 바꿔야 gateway·MinIO에 `system_id=cointutor`로 기록됩니다.
