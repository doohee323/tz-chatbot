# How to Add the Chat Module (Vue app)

This document describes how to add the chat widget (as used in CoinTutor and tz-drillquiz) to another Vue project.

## Prerequisites

- **TZ-Chat** server must be deployed, and you must have one of the `CHAT_GATEWAY_API_KEY` API keys.
- The Vue 2/3 project must have an **auth service** or be able to implement a minimal interface (authService adapter).

---

## 1. Copy files

| Source (sample) | Target (project) |
|-----------------|------------------|
| `sample/ChatWidget.vue` | `src/components/ChatWidget.vue` |

```bash
cp chat-gateway/sample/ChatWidget.vue your-vue-app/src/components/ChatWidget.vue
```

---

## 2. Auth service (authService) integration

ChatWidget expects the following interface:

- **`authService.getUserSync()`**  
  - Returns: `{ username?: string, email?: string }` or `null`  
  - Logged-in user: return an object with `username` and/or `email` (widget uses `username || email` as `user_id`)  
  - Not logged in: `null` → widget sends `user_id` as `anonymous`

- **`authService.subscribe(handler)`**  
  - Register a callback to be invoked when auth state changes  
  - Returns: unsubscribe function (call when component is destroyed)

### 2-1. When you already have authService

- Either make `getUserSync()` return `{ username, email }`, or
- Adjust the field used in ChatWidget’s `getChatUserId()` to match your project in one place.

### 2-2. When you don’t have authService

- Copy `sample/authService.adapter.example.js` to `src/services/authService.js`, then
- Wire your login/logout to call `setAuthUser(user)` or `setAuthUser(null)`.

---

## 3. Update App.vue

- **import**: Add the `ChatWidget` component
- **components**: Register `ChatWidget`
- **template**: Add `<ChatWidget v-if="isLoggedIn" />` at the bottom of the layout (e.g. after Footer). Showing only when logged in matches CoinTutor and tz-drillquiz.
- **data**: Ensure `isLoggedIn` exists and is updated on login/logout.

See `App.vue.snippet` for exact code snippets.

```vue
<template>
  <div id="app">
    <!-- ... existing layout ... -->
    <AppFooter />
    <ChatWidget v-if="isLoggedIn" />
  </div>
</template>

<script>
import ChatWidget from '@/components/ChatWidget.vue'
// ...
export default {
  data() {
    return {
      isLoggedIn: false,
      // ...
    }
  },
  components: {
    AppFooter,
    ChatWidget
  },
  // ...
}
</script>
```

---

## 4. Environment variables

The following env vars are required at build time. Use `.env` locally and replace placeholders in `env-frontend` etc. for CI.

| Variable | Description | Example |
|----------|-------------|---------|
| `VUE_APP_CHAT_GATEWAY_URL` | TZ-Chat base URL (no trailing `/`) | `https://chat.drillquiz.com` |
| `VUE_APP_CHAT_GATEWAY_API_KEY` | Gateway API key (one of CHAT_GATEWAY_API_KEY) | (injected by Jenkins/CI) |
| `VUE_APP_CHAT_GATEWAY_SYSTEM_ID` | System identifier (must match gateway ALLOWED_SYSTEM_IDS) | `drillquiz`, `cointutor` |

Example file: `env-frontend.example`

### 4-1. Local development

- Vue CLI only auto-loads `.env` / `.env.local`. To use `env-frontend`, have **vue.config.js** read `env-frontend` at build time and attach it to `process.env`.
- Then set URL/API key in `env-frontend` and restart `npm run serve` for the widget to work.

---

## 5. Chat token API and UI labels

- **GET /v1/chat-token?system_id=...&user_id=...&lang=...**  
  - Query: `system_id`, `user_id`, `lang` (e.g. `en`, `ko`, `ja`, `zh`, `es`, `fr`).  
  - Header: `X-API-Key: <API_KEY>`.  
  - Response: `{ token: string, ui?: { title, close, open, tokenError, loading } }`.  
  - If the gateway returns `ui`, the widget uses those strings for the header/buttons/messages; otherwise it uses your app’s i18n (`$t('chat.*')`) or built-in defaults.

- **iframe**  
  - URL: `{VUE_APP_CHAT_GATEWAY_URL}/chat?token=...&embed=1&lang=...`  
  - Passing `lang` keeps the chat UI language in sync with the app.

---

## 6. i18n (optional)

- If the app uses `vue-i18n`, the widget uses `this.$i18n.locale` for the `lang` parameter (allowed: `en`, `es`, `ko`, `zh`, `ja`, `fr`; others fall back to `en`).
- Add translation keys for fallback when the gateway does not return `ui`:
  - `chat.title`, `chat.close`, `chat.open`, `chat.tokenError`, `chat.loading`, `chat.notConfigured`, `chat.unknownError`, `chat.networkError`  
  - `chat.networkError` is shown when the token request fails with a network/CORS error.

---

## 7. CI build (e.g. Jenkins, refer/drillquiz/ci style)

- **env-frontend in repo**  
  - Keep `env-frontend` in the repo (like tz-drillquiz) with placeholders:  
    `VUE_APP_CHAT_GATEWAY_API_KEY=CHAT_GATEWAY_API_KEY_PLACEHOLDER`, and optionally `DOMAIN_PLACEHOLDER` for app host.
- **Build script (e.g. ci/k8s.sh build_frontend)**  
  - Replace placeholders in order: first `CHAT_GATEWAY_API_KEY_PLACEHOLDER` (from Jenkins credential or env), then `DOMAIN_PLACEHOLDER` (from branch/domain).  
  - No need to extract env from ConfigMap; single source is `env-frontend` + sed.
- **Jenkins**  
  - Credential ID: `CHAT_GATEWAY_API_KEY` (Secret text). If missing, build continues but the chat widget will show “not configured”.

---

## 8. Flow summary

1. User (logged in) sees the chat button (bottom right). Widget is typically shown only when `isLoggedIn` is true.
2. On open, call `GET /v1/chat-token?system_id=...&user_id=...&lang=...` with `X-API-Key` to get a JWT and optional `ui` labels.
3. Open iframe with `chat URL?token=...&embed=1&lang=...`.
4. If the request fails with a network/CORS error, show `chat.networkError` (or equivalent). On success, use `data.ui` for labels when provided.

---

## 9. CSP (Content-Security-Policy)

When the app sets a **Content-Security-Policy** header (e.g. Ingress nginx), the chat widget needs:

- **connect-src**  
  Include the chat gateway origin (e.g. `https://chat.drillquiz.com`) so `fetch('.../v1/chat-token?...')` is allowed.
- **frame-src**  
  Include the same origin so the chat UI iframe can load.

Example (Ingress `configuration-snippet`):

```text
connect-src 'self' ... https://chat.drillquiz.com;
frame-src 'self' https://chat.drillquiz.com;
```

If not set, the browser will show “Refused to connect ... violates the document's Content Security Policy” and the token request or iframe will be blocked.

---

## sample folder contents

| File | Purpose |
|------|---------|
| `ChatWidget.vue` | Widget component (Vue 2: beforeDestroy, transition enter/leave). Uses chatUi from API, chatLang, iframe lang, networkError. Copy and adapt. |
| `App.vue.snippet` | Snippets for import, registration, and `<ChatWidget v-if="isLoggedIn" />` in App.vue |
| `env-frontend.example` | Frontend build env example (gateway URL, API key placeholder, system_id) |
| `authService.adapter.example.js` | Minimal authService (getUserSync with username/email, subscribe) when you don’t have one |
| `INTEGRATION.md` | This integration guide |

### Jenkins credentials

- To enable the chat widget in CI, add a **Secret text** credential in Jenkins.
- **ID:** `CHAT_GATEWAY_API_KEY`
- **Value:** An API key issued by the TZ-Chat gateway (one of CHAT_GATEWAY_API_KEY).
