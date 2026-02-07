/**
 * API config for TZ-Chat frontend (tz-cointutor style)
 * VUE_APP_API_BASE: API base URL for links to /docs, /cache (empty = same origin)
 * VUE_APP_CHAT_GATEWAY_URL: Chat API base for /v1/conversations, /v1/chat etc. (empty = same origin, for dev proxy)
 */
const ENVIRONMENT = process.env.VUE_APP_ENVIRONMENT || 'development'
const API_BASE = process.env.VUE_APP_API_BASE || ''
const _chatUrl = (process.env.VUE_APP_CHAT_GATEWAY_URL || '').replace(/\/$/, '')
const _fromEnv = _chatUrl && !_chatUrl.includes('PLACEHOLDER')
const CHAT_GATEWAY_URL = _fromEnv ? _chatUrl : (() => {
  // Fallback: derive from current host (chat-admin.drillquiz.com → https://chat.drillquiz.com)
  if (typeof window !== 'undefined' && window.location?.hostname?.includes('chat-admin')) {
    const host = window.location.hostname.replace(/^chat-admin/, 'chat')
    return `${window.location.protocol}//${host}`
  }
  return ''
})()

const apiBase = (typeof window !== 'undefined' && !API_BASE)
  ? window.location.origin
  : API_BASE

/** Base URL for chat API (/v1/conversations, /v1/chat). Empty = same origin (dev proxy). */
const chatApiBase = CHAT_GATEWAY_URL

export {
  ENVIRONMENT,
  apiBase,
  chatApiBase
}
