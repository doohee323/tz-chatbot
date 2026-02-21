# n8n

n8n 워크플로 자동화 (Community Helm Chart).  
설치: `bash install.sh`

## 구성 개요

- **n8n:** [n8n_weather.json](./n8n_weather.json) 워크플로를 n8n에 추가해 Chat 웹훅으로 **외부에 노출**한다.
- **Dify:** [dify_weather.yml](./dify_weather.yml)로 Dify 앱/워크플로를 재구성해 Dify API로 **외부에 노출**한다. Dify를 호출하면 내부에서 n8n Chat 웹훅을 호출하고, **나온 결과**를 Dify 응답으로 반환한다.

외부에서는 **n8n 웹훅** 또는 **Dify API** 둘 중 편한 쪽으로 호출할 수 있다.

---

## n8n (n8n_weather.json)

- **워크플로 정의:** [n8n_weather.json](./n8n_weather.json)  
  n8n 에디터에서 Import로 불러와 사용한다. Chat Trigger + AI 에이전트(날씨·뉴스 등 도구) 구성.
- **노출:** Chat 웹훅 URL로 외부 호출 가능.

### Chat 웹훅 호출

- **URL:** `https://n8n.drillquiz.com/webhook/e5616171-e3b5-4c39-81d4-67409f9fa60a/chat`
- **인증:** Basic Auth  
  - 사용자: `doohee323`  
  - 비밀번호: `Hongdoohee!323`
- **Body (JSON):**
  - `sessionId` (필수): 세션 식별자. 같은 값이면 대화 맥락 유지.
  - `chatInput` (필수): 사용자 메시지.

```bash
curl -s --max-time 30 -X POST "https://n8n.drillquiz.com/webhook/e5616171-e3b5-4c39-81d4-67409f9fa60a/chat" \
  -H "Content-Type: application/json" \
  -u 'doohee323:Hongdoohee!323' \
  -d '{"sessionId":"my-session","chatInput":"서울 날씨 알려줘"}'
```

- 도구 호출(날씨 등)이 있으면 응답에 수 초 걸릴 수 있으므로 `--max-time 30` 권장.
- 응답: `{"output":"..."}` 형태.

---

## Dify (dify_weather.yml)

- **앱/워크플로 정의:** [dify_weather.yml](./dify_weather.yml)  
  Dify에서 YAML로 앱을 가져오거나 재구성해 사용한다. 시작 → HTTP 요청(n8n Chat 웹훅 호출) → 종료 구조로, n8n 결과를 그대로 외부에 노출한다.
- **노출:** Dify Workflow API (`/v1/workflows/run`)로 외부 호출 가능.

### Dify API 호출

- **URL:** `POST https://dify.drillquiz.com/v1/workflows/run`
- **인증:** `Authorization: Bearer {api_key}` (Dify 앱 API 키)
- **Body:** `inputs.query` 필수. `response_mode`: `blocking` 또는 `streaming`, `user`: 사용자 식별자.

```bash
curl -s -X POST 'https://dify.drillquiz.com/v1/workflows/run' \
  -H 'Authorization: Bearer app-hDWO8esDwF38MM75mJBMD88I' \
  -H 'Content-Type: application/json' \
  -d '{"inputs":{"query":"서울 날씨 알려줘"},"response_mode":"blocking","user":"curl-user-1"}'
```

- 응답의 `data.outputs.body`에 n8n 에이전트 응답(JSON 문자열)이 담긴다.

---

## 참고

- Ingress/프록시 사용 시 `N8N_PROXY_HOPS=1` 설정 필요 (values.yaml `main.extraEnvVars`).
- Chat 메모리 노드는 단일 인스턴스용. Queue Mode/멀티 메인 사용 시 Redis 등 외부 메모리 사용 권장.

### n8n 접속 URL / OAuth 콜백 도메인 바꾸기

n8n이 인식하는 주소(OAuth 콜백 등)는 **요청의 Host**와 같다. Ingress를 Helm values에만 두므로, **values.yaml_bak**의 `ingress.hosts[].host`·`ingress.tls[].hosts`만 원하는 도메인(예: `n8n.drillquiz.com`)으로 수정하면 된다. 별도 `N8N_EDITOR_BASE_URL`·`n8n-ingress.yaml`은 사용하지 않는다.
