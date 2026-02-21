#!/usr/bin/env bash
# n8n workflow API (list / import / export / rename / activate / delete / webhooks)
#
# Usage:
#   export N8N_URL="https://your-n8n.example.com"
#   export N8N_API_KEY="your-api-key"
#
#   ./n8n/n8n.sh list                      # list workflows
#   ./n8n/n8n.sh import <workflow.json>  # create workflow (import from file)
#   ./n8n/n8n.sh export <workflow-id> [output.json]  # export to file (fails if file exists)
#   ./n8n/n8n.sh rename <workflow-id> <new-name>  # rename
#   ./n8n/n8n.sh activate <workflow-id>   # activate (active=true)
#   ./n8n/n8n.sh deactivate <workflow-id> # deactivate (active=false)
#   ./n8n/n8n.sh webhooks <workflow-id>   # show webhook/chat URLs
#   ./n8n/n8n.sh call <workflow-id> [message]  # invoke webhook (Basic Auth: N8N_WEBHOOK_USER, N8N_WEBHOOK_PASSWORD)
#   N8N_DEBUG=1 ./n8n/n8n.sh call <id> [msg]   # debug: print webhookId, URL, auth status, body
#   N8N_DEBUG=1 ./n8n/n8n.sh import <file>     # debug: print file path, payload source (jq vs raw), size, first bytes
#   ./n8n/n8n.sh executions <workflow-id> [limit]  # list execution logs (default limit 20)
#   ./n8n/n8n.sh execution <execution-id>         # show one execution detail (includeData)
#   ./n8n/n8n.sh delete <workflow-id>     # delete workflow
#
# Examples:
#   ./n8n/n8n.sh rename e3MrkCu9b5B3Yvrh "Chat2Gmail (copy)"

set -e
CMD="${1:-}"
if [[ -z "$CMD" ]]; then
  CMD="help"
fi
case "$CMD" in
  help|-h|--help)
    echo "n8n workflow API (list / import / export / rename / activate / delete / webhooks)"
    echo ""
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  list                      list workflows (NAME, ID, ACTIVE, UPDATED)"
    echo "  import <workflow.json>    create workflow (import from file)"
    echo "  export <workflow-id> [file.json]  export workflow to file (error if file exists)"
    echo "  rename <workflow-id> <name>  rename workflow"
    echo "  activate <workflow-id>     activate workflow (active=true)"
    echo "  deactivate <workflow-id>   deactivate workflow (active=false)"
    echo "  webhooks <workflow-id>     show webhook/chat URLs"
    echo "  call <workflow-id> [msg]   invoke webhook (auth: N8N_WEBHOOK_USER, N8N_WEBHOOK_PASSWORD)"
    echo "  executions <workflow-id> [limit]  list execution logs (default limit 20)"
    echo "  execution [workflow-id] <execution-id>  show detail; with workflow-id, verify belonging"
    echo "  delete <workflow-id>       delete workflow"
    echo "  help                       this help"
    echo ""
    echo "Environment (set before using list/import/export/rename/delete etc.):"
    echo "  export N8N_URL=\"https://your-n8n.example.com\""
    echo "  export N8N_API_KEY=\"your-api-key\""
    echo "  export N8N_WEBHOOK_USER='user'       # for call (Basic Auth)"
    echo "  export N8N_WEBHOOK_PASSWORD='pass'   # for call (use single quotes if password has !)"
    echo "  N8N_DEBUG=1 $0 import <file>         # debug import (file path, payload source, size)"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 import n8n/Chat2Gmail.json"
    echo "  $0 export e3MrkCu9b5B3Yvrh n8n/Chat2Gmail2.json"
    echo "  $0 rename e3MrkCu9b5B3Yvrh \"Chat2Gmail (copy)\""
    echo "  $0 activate e3MrkCu9b5B3Yvrh"
    echo "  $0 webhooks e3MrkCu9b5B3Yvrh"
    echo "  $0 call e3MrkCu9b5B3Yvrh \"Hello\"   # N8N_WEBHOOK_USER+PASSWORD set"
    echo "  $0 executions e3MrkCu9b5B3Yvrh 10   # last 10 runs"
    echo "  $0 execution e3MrkCu9b5B3Yvrh 12345  # detail + verify belongs to workflow"
    echo "  $0 delete e3MrkCu9b5B3Yvrh"
    exit 0
    ;;
esac
if [[ -z "$N8N_URL" || -z "$N8N_API_KEY" ]]; then
  echo "Set N8N_URL and N8N_API_KEY first."
  echo "  export N8N_URL=\"https://your-n8n.example.com\""
  echo "  export N8N_API_KEY=\"your-api-key\""
  exit 1
fi
BASE_URL="${N8N_URL%/}/api/v1/workflows"
EXEC_URL="${N8N_URL%/}/api/v1/executions"

case "$CMD" in
  list)
    RES=$(curl -sS -X GET "$BASE_URL" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    # Response: .data[] or root array. Tab + column -t for alignment.
    LIST=$(echo "$RES" | jq -r '(.data // . | if type == "array" then . else [] end)[] | "\(.name)\t\(.id)\t\(.active)\t\(.updatedAt // "-")"' 2>/dev/null)
    (printf 'NAME\tID\tACTIVE\tUPDATED\n'; echo "$LIST" | while IFS=$'\t' read -r name id active updated; do [[ -n "$id" ]] && printf "%s\t%s\t%s\t%s\n" "$name" "$id" "$active" "${updated:-}"; done) | column -t -s $'\t'
    if echo "$RES" | jq -e '.nextCursor' >/dev/null 2>&1; then
      echo "(more: use cursor for pagination)"
    fi
    ;;
  import|upload)
    FILE="${2:-}"
    if [[ -z "$FILE" ]]; then
      echo "Usage: $0 import <workflow.json>"
      exit 1
    fi
    if [[ ! -f "$FILE" ]]; then
      FILE="$(dirname "$0")/$FILE"
      [[ -f "$FILE" ]] || { echo "File not found: $2"; exit 1; }
    fi
    if [[ -n "$N8N_DEBUG" ]]; then
      echo "DEBUG import: file=$FILE"
      echo "DEBUG extension: ${FILE##*.}"
    fi
    PAYLOAD=$(jq 'del(.id, .versionId, .meta, .tags, .active, .pinData) | .settings = {}' "$FILE" 2>/dev/null) || PAYLOAD=$(cat "$FILE")
    if [[ -n "$N8N_DEBUG" ]]; then
      if jq -e . <<< "$PAYLOAD" >/dev/null 2>&1; then
        echo "DEBUG payload: from jq (valid JSON), size=${#PAYLOAD}"
      else
        echo "DEBUG payload: raw file (jq failed or not JSON), size=${#PAYLOAD}"
        echo "DEBUG payload first 120 chars: ${PAYLOAD:0:120}..."
      fi
      echo "DEBUG POST $BASE_URL"
    fi
    echo "Importing $FILE to $BASE_URL ..."
    echo "$PAYLOAD" | curl -sS -X POST "$BASE_URL" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d @- | jq '.' 2>/dev/null || cat
    ;;
  export)
    ID="${2:-}"
    OUT="${3:-}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 export <workflow-id> [output.json]"
      echo "Exports workflow to file. Errors if output file already exists."
      exit 1
    fi
    RES=$(curl -sS -X GET "$BASE_URL/${ID}" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    if [[ -z "$OUT" ]]; then
      NAME=$(echo "$RES" | jq -r '.name // empty' | sed 's/[^a-zA-Z0-9._-]/_/g')
      [[ -z "$NAME" ]] && NAME="$ID"
      OUT="${NAME}.json"
    fi
    if [[ -f "$OUT" ]]; then
      echo "Error: file already exists: $OUT"
      exit 1
    fi
    echo "$RES" | jq '.' > "$OUT"
    echo "Exported to $OUT"
    ;;
  rename)
    ID="${2:-}"
    NEWNAME="${3:-}"
    if [[ -z "$ID" || -z "$NEWNAME" ]]; then
      echo "Usage: $0 rename <workflow-id> <new-name>"
      exit 1
    fi
    RES=$(curl -sS -X GET "$BASE_URL/${ID}" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    # PUT accepts only name, nodes, connections, settings
    PAYLOAD=$(echo "$RES" | jq --arg n "$NEWNAME" '{name: $n, nodes: .nodes, connections: .connections, settings: {}}')
    echo "Renaming workflow $ID to \"$NEWNAME\" ..."
    echo "$PAYLOAD" | curl -sS -X PUT "$BASE_URL/${ID}" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d @- | jq '.' 2>/dev/null || cat
    ;;
  activate)
    ID="${2:-}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 activate <workflow-id>"
      exit 1
    fi
    echo "Activating workflow $ID ..."
    curl -sS -X POST "$BASE_URL/${ID}/activate" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{}' | jq '.' 2>/dev/null || cat
    ;;
  deactivate)
    ID="${2:-}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 deactivate <workflow-id>"
      exit 1
    fi
    echo "Deactivating workflow $ID ..."
    curl -sS -X POST "$BASE_URL/${ID}/deactivate" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{}' | jq '.' 2>/dev/null || cat
    ;;
  call)
    ID="${2:-}"
    MSG="${3:-test}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 call <workflow-id> [message]"
      echo "Env: N8N_WEBHOOK_USER, N8N_WEBHOOK_PASSWORD (Basic Auth). Workflow must be active."
      echo "Debug: N8N_DEBUG=1 $0 call <id> [msg]  to print URL, webhookId, auth status, body."
      exit 1
    fi
    RES=$(curl -sS -X GET "$BASE_URL/${ID}" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    # Use only trigger nodes (chat or webhook), not other nodes that have webhookId (e.g. Gmail)
    FIRST=$(echo "$RES" | jq -r '.nodes[]? | select(.webhookId != null) | select(.type | test("chatTrigger|chattrigger|n8n-nodes-base\\.webhook"; "i")) | [.type, .webhookId] | @tsv' 2>/dev/null | head -1)
    if [[ -z "$FIRST" ]]; then
      echo "No webhook/chat trigger node found in workflow."
      exit 1
    fi
    read -r NTYPE WID <<< "$FIRST"
    SESSION_ID="${N8N_WEBHOOK_SESSION_ID:-my-session}"
    if echo "$NTYPE" | grep -qiE "chatTrigger|chattrigger"; then
      CALL_URL="${N8N_URL%/}/webhook/${WID}/chat"
      BODY=$(jq -n --arg sid "$SESSION_ID" --arg msg "$MSG" '{sessionId: $sid, chatInput: $msg}')
    else
      CALL_URL="${N8N_URL%/}/webhook/${WID}"
      BODY=$(jq -n --arg msg "$MSG" '{message: $msg}')
    fi
    if [[ -n "$N8N_DEBUG" ]]; then
      WFNAME=$(echo "$RES" | jq -r '.name // empty')
      echo "DEBUG workflow: $WFNAME (id=$ID)"
      echo "DEBUG webhookId: $WID"
      echo "DEBUG URL: $CALL_URL"
      echo "DEBUG auth: user=${N8N_WEBHOOK_USER:-<unset>} password_set=$([[ -n "$N8N_WEBHOOK_PASSWORD" ]] && echo yes length=${#N8N_WEBHOOK_PASSWORD} || echo no)"
      echo "DEBUG body: $BODY"
    fi
    echo "Calling: $CALL_URL"
    if [[ -n "$N8N_WEBHOOK_USER" && -n "$N8N_WEBHOOK_PASSWORD" ]]; then
      OUT=$(curl -sS --max-time 30 -w "\n[HTTP %{http_code}]" -X POST "$CALL_URL" \
        -H "Content-Type: application/json" \
        -u "${N8N_WEBHOOK_USER}:${N8N_WEBHOOK_PASSWORD}" \
        -d "$BODY")
    else
      echo "Set N8N_WEBHOOK_USER and N8N_WEBHOOK_PASSWORD for Basic Auth."
      OUT=$(curl -sS --max-time 30 -w "\n[HTTP %{http_code}]" -X POST "$CALL_URL" \
        -H "Content-Type: application/json" -d "$BODY")
    fi
    CODE=$(echo "$OUT" | tail -1)
    BODY_OUT=$(echo "$OUT" | sed '$d')
    echo "$BODY_OUT" | jq '.' 2>/dev/null || echo "$BODY_OUT"
    echo "$CODE"
    if [[ "$CODE" == "[HTTP 403]" ]] && [[ -n "$N8N_WEBHOOK_PASSWORD" ]]; then
      echo "Hint: 403 = wrong auth. If password contains ! use single quotes: export N8N_WEBHOOK_PASSWORD='yourpass'"
    fi
    ;;
  executions)
    ID="${2:-}"
    LIMIT="${3:-20}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 executions <workflow-id> [limit]"
      echo "Lists execution logs for the workflow (default limit 20)."
      exit 1
    fi
    RES=$(curl -sS -X GET "${EXEC_URL}?workflowId=${ID}&limit=${LIMIT}" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    LIST=$(echo "$RES" | jq -r '(.data // . | if type == "array" then . else [] end)[]? | "\(.id)\t\(.status)\t\(.startedAt // "-")\t\(.stoppedAt // "-")"' 2>/dev/null)
    if [[ -z "$LIST" ]]; then
      echo "No executions found for workflow $ID."
      exit 0
    fi
    (printf 'ID\tSTATUS\tSTARTED\tSTOPPED\n'; echo "$LIST") | column -t -s $'\t'
    if echo "$RES" | jq -e '.nextCursor' >/dev/null 2>&1; then
      echo "(more: use limit or cursor for pagination)"
    fi
    echo ""
    echo "To see full detail: $0 execution <id>"
    ;;
  execution)
    # execution <execution-id>   OR   execution <workflow-id> <execution-id> (verify belonging)
    WID_ARG="${2:-}"
    EID="${3:-}"
    if [[ -z "$EID" ]]; then
      EID="$WID_ARG"
      WID_ARG=""
    fi
    if [[ -z "$EID" ]]; then
      echo "Usage: $0 execution <execution-id>"
      echo "   or: $0 execution <workflow-id> <execution-id>   # verify execution belongs to workflow"
      echo "Get execution-id from: $0 executions <workflow-id>"
      exit 1
    fi
    RES=$(curl -sS -X GET "${EXEC_URL}/${EID}?includeData=true" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    EXEC_WID=$(echo "$RES" | jq -r '.workflowId // empty')
    echo "Execution: $EID"
    echo "workflowId: $EXEC_WID   (this execution belongs to this workflow)"
    if [[ -n "$WID_ARG" ]]; then
      if [[ "$EXEC_WID" != "$WID_ARG" ]]; then
        echo "WARNING: workflowId mismatch. You passed workflow $WID_ARG but this execution belongs to $EXEC_WID"
      else
        echo "OK: execution belongs to workflow $WID_ARG"
      fi
    fi
    echo "$RES" | jq -r 'if .status then "status: \(.status)\nstartedAt: \(.startedAt // "-")\nstoppedAt: \(.stoppedAt // "-")" else empty end'
    if echo "$RES" | jq -e '.data?.resultData?.error' >/dev/null 2>&1; then
      echo ""
      echo "Error:"
      echo "$RES" | jq -r '.data.resultData.error'
    fi
    echo ""
    echo "Full JSON:"
    echo "$RES" | jq '.'
    ;;
  webhooks)
    ID="${2:-}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 webhooks <workflow-id>"
      exit 1
    fi
    RES=$(curl -sS -X GET "$BASE_URL/${ID}" -H "X-N8N-API-KEY: $N8N_API_KEY")
    if echo "$RES" | jq -e '.message' >/dev/null 2>&1; then
      echo "$RES" | jq -r '.message'
      exit 1
    fi
    NAME=$(echo "$RES" | jq -r '.name // empty')
    echo "Workflow: $NAME (${ID})"
    echo "Active:   $(echo "$RES" | jq -r '.active')"
    echo ""
    HAS_ANY=0
    echo "$RES" | jq -r '.nodes[]? | select(.webhookId != null) | [.name, .type, .webhookId, (if .credentials then (.credentials | to_entries | map("\(.key): \(.value.name)") | join("; ")) else "" end)] | @tsv' 2>/dev/null | while IFS=$'\t' read -r nname ntype wid creds; do
      [[ -z "$wid" ]] && continue
      HAS_ANY=1
      if echo "$ntype" | grep -qiE "chatTrigger|chattrigger"; then
        echo "Node: $nname"
        echo "  type: $ntype"
        echo "  webhookId: $wid"
        echo "  auth: ${creds:-none}"
        echo "  URL (chat): ${N8N_URL%/}/webhook/${wid}/chat"
      else
        echo "Node: $nname"
        echo "  type: $ntype"
        echo "  webhookId: $wid"
        echo "  auth: ${creds:-none}"
        echo "  URL: ${N8N_URL%/}/webhook/${wid}"
      fi
      echo ""
    done
    # If no webhookId found, list trigger nodes that may have webhooks (API sometimes omits webhookId)
    TRIGGERS=$(echo "$RES" | jq -r '.nodes[]? | select(.type | test("chatTrigger|chattrigger|n8n-nodes-base\\.webhook"; "i")) | "\(.name)\t\(.type)\t\(.webhookId // "")"' 2>/dev/null)
    if [[ -n "$TRIGGERS" ]]; then
      echo "$TRIGGERS" | while IFS=$'\t' read -r nname ntype wid; do
        if [[ -z "$wid" ]]; then
          echo "Node: $nname"
          echo "  type: $ntype"
          echo "  webhookId: (not in API response)"
          echo "  -> This workflow was likely imported/synced; the API does not return webhookId. Open the workflow in n8n UI and check the trigger node for the Production URL (e.g. .../webhook/<id>/chat)."
          echo ""
        fi
      done
    fi
    ;;
  delete)
    ID="${2:-}"
    if [[ -z "$ID" ]]; then
      echo "Usage: $0 delete <workflow-id>"
      exit 1
    fi
    echo "Deleting workflow $ID ..."
    curl -sS -X DELETE "$BASE_URL/${ID}" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" | jq '.' 2>/dev/null || echo "Done."
    ;;
  *)
    echo "Unknown command: $CMD"
    echo "Usage: $0 list | import <workflow.json> | export <id> [file.json] | rename <id> <name> | activate <id> | deactivate <id> | webhooks <id> | call <id> [msg] | executions <id> [limit] | execution <exec-id> | delete <workflow-id>"
    exit 1
    ;;
esac
