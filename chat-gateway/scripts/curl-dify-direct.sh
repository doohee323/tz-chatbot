#!/usr/bin/env bash
# Dify API 직접 호출 (gateway 거치지 않음). retriever_resources 등 metadata 확인용.
# 사용: ./scripts/curl-dify-direct.sh [질문] [system_id] [user_id]
#   system_id: cointutor | drillquiz (기본: drillquiz). 코인튜터 질문은 cointutor 로 호출해야 코인튜터 앱으로 감.
# .env: DIFY_BASE_URL, DIFY_COINTUTOR_BASE_URL(선택), DIFY_DRILLQUIZ_BASE_URL(선택),
#       DIFY_API_KEY, DIFY_COINTUTOR_API_KEY, DIFY_DRILLQUIZ_API_KEY

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Error: .env not found"
  exit 1
fi

QUESTION="${1:-코인튜터는 무엇인가?}"
SYSTEM_ID="${2:-drillquiz}"
USER_ID="${3:-curl-direct-user}"

# system_id 별 URL/API 키 (소문자로 통일)
SID=$(echo "$SYSTEM_ID" | tr '[:upper:]' '[:lower:]')
if [[ "$SID" == "cointutor" ]]; then
  BASE_URL=$(grep -E '^DIFY_COINTUTOR_BASE_URL=' .env | cut -d= -f2- | tr -d '\r" ')
  [[ -z "$BASE_URL" ]] && BASE_URL=$(grep -E '^DIFY_BASE_URL=' .env | cut -d= -f2- | tr -d '\r" ')
  API_KEY=$(grep -E '^DIFY_COINTUTOR_API_KEY=' .env | cut -d= -f2- | tr -d '\r" ')
else
  BASE_URL=$(grep -E '^DIFY_DRILLQUIZ_BASE_URL=' .env | cut -d= -f2- | tr -d '\r" ')
  [[ -z "$BASE_URL" ]] && BASE_URL=$(grep -E '^DIFY_BASE_URL=' .env | cut -d= -f2- | tr -d '\r" ')
  API_KEY=$(grep -E '^DIFY_DRILLQUIZ_API_KEY=' .env | cut -d= -f2- | tr -d '\r" ')
  [[ -z "$API_KEY" ]] && API_KEY=$(grep -E '^DIFY_API_KEY=' .env | cut -d= -f2- | tr -d '\r" ')
fi

if [[ -z "$BASE_URL" || -z "$API_KEY" ]]; then
  echo "Error: BASE_URL and API_KEY required for system_id=$SYSTEM_ID (check .env)"
  exit 1
fi

BASE_URL="${BASE_URL%/}"
echo "POST $BASE_URL/v1/chat-messages (blocking)  [app: $SID]"
echo "Query: $QUESTION"
echo "---"

BODY=$(jq -n --arg q "$QUESTION" --arg u "$USER_ID" \
  '{inputs: {}, query: $q, response_mode: "blocking", conversation_id: "", user: $u}')
curl -s -X POST "$BASE_URL/v1/chat-messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq .
