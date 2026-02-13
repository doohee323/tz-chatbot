#!/usr/bin/env bash
# 로컬 chat-gateway (bash gateway.sh) 로 POST /v1/chat 호출 테스트
# 사용: ./scripts/curl-chat-local.sh [질문]
# .env 의 CHAT_GATEWAY_API_KEY, DIFY_* 사용

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Error: .env not found. Copy .env.example to .env and set CHAT_GATEWAY_API_KEY, DIFY_BASE_URL, DIFY_API_KEY"
  exit 1
fi

# .env 에서 API 키 로드
CHAT_GATEWAY_API_KEY=$(grep -E '^CHAT_GATEWAY_API_KEY=' .env | cut -d= -f2- | tr -d '\r" ')
GATEWAY_URL="${GATEWAY_URL:-http://localhost:8088}"
QUESTION="${1:-코인튜터는 무엇인가?}"
SYSTEM_ID="${SYSTEM_ID:-drillquiz}"
USER_ID="${USER_ID:-test-user-local}"

if [[ -z "$CHAT_GATEWAY_API_KEY" ]]; then
  echo "Error: CHAT_GATEWAY_API_KEY not set in .env"
  exit 1
fi

echo "POST $GATEWAY_URL/v1/chat (system_id=$SYSTEM_ID, user_id=$USER_ID)"
echo "Question: $QUESTION"
echo "---"

curl -s -X POST "$GATEWAY_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $CHAT_GATEWAY_API_KEY" \
  -d "{
    \"system_id\": \"$SYSTEM_ID\",
    \"user_id\": \"$USER_ID\",
    \"message\": \"$QUESTION\"
  }" | jq .
