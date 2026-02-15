# Dify Extractor: Connection refused [Errno 111]

## 현상

- **에러**: `An error occurred in the langgenius/dify_extractor/dify_extractor, please contact the author ... error type: ConnectError, error details: [Errno 111] Connection refused`
- **발생 위치**: 데이터셋 문서 처리 시 (예: [datasets/.../documents/...](https://dify.drillquiz.com/datasets/7ad452a5-a685-4d45-8671-22e2567be3d2/documents/dca7e361-146c-42c7-ad15-021ebc19401d))
- **실패 노드**: 파이프라인 내 **Dify Extractor** 노드 (예: Node 1750836391776)

## K8s에서 확인한 내용

- **dify-worker** 로그: `dify_extractor` 호출 직후 `ConnectError: [Errno 111] Connection refused` 발생.
- **dify-plugin-daemon** 에는 `DIFY_INNER_API_URL: http://dify-api:5001` 이 설정되어 있으며, Pod 내부에서 `curl http://dify-api:5001/` 연결은 **성공**함.
- **dify-api**, **dify-plugin-daemon** 등 서비스·Pod 모두 정상 존재.

## 원인 (확정)

[공식 이슈 #1816](https://github.com/langgenius/dify-official-plugins/issues/1816) 및 플러그인 코드 확인 결과:

- Worker/API가 플러그인을 호출할 때 **파일 다운로드 URL**을 함께 넘깁니다.
- 이 URL은 **FILES_URL** 환경 변수(또는 이에 대응하는 설정)로 만들어집니다.
- Helm 기본값으로 `api.url.files` 등이 **외부 주소**(`https://dify.drillquiz.com`)로 설정되어 있으면, 플러그인에 전달되는 파일 URL도 외부 주소가 됨.
- 플러그인은 **plugin-daemon Pod 안**에서 `httpx.get(file_url)` 로 파일을 받습니다. 이때 외부 URL로 접속하면 Ingress/네트워크 특성상 **Connection refused** 또는 접근 실패가 발생할 수 있습니다.

즉, **플러그인에 넘어가는 파일 URL이 내부에서 접근 가능한 주소가 아니어서** 발생한 문제입니다.

## 대응 방법

### 0. 적용한 조치 (Helm / K8s)

- **api**, **worker** 의 `extraEnv`에 **FILES_URL** 을 내부 주소로 설정함.
- `dify/values.yaml`:
  - `api.extraEnv`: `FILES_URL: "http://dify-api:5001"`
  - `worker.extraEnv`: `FILES_URL: "http://dify-api:5001"`
- 적용 후 `helm upgrade` 또는 재배포 후, 데이터셋 문서 처리( Dify Extractor )를 다시 실행해 보면 됨.

### 1. 공식 설정 기준 (docker-compose.yaml)

[공식 Dify docker-compose](https://github.com/langgenius/dify/blob/main/docker/docker-compose.yaml) 기준:

- **api / worker** 의 shared env에는 `CONSOLE_INNER_API_URL`, `SERVICE_INNER_API_URL` **없음**.  
  `CONSOLE_API_URL`, `SERVICE_API_URL` 등 외부 URL만 사용.
- **plugin_daemon** 에만 **내부 API URL** 설정:
  - `DIFY_INNER_API_URL: ${PLUGIN_DIFY_INNER_API_URL:-http://api:5001}`
  - `DIFY_INNER_API_KEY: ${PLUGIN_DIFY_INNER_API_KEY:-...}`

즉, 플러그인이 Dify API를 호출할 때 쓰는 주소는 **Plugin Daemon** 의 `DIFY_INNER_API_URL` 로만 제어됨.  
Helm 차트에서 pluginDaemon이 이 값을 `http://dify-api:5001` 로 넘기면, 클러스터 내부에서 접근 가능한 주소가 됨.

### 2. Plugin Daemon에서 내부 URL 사용 확인

- **dify-plugin-daemon** ConfigMap에 이미 `DIFY_INNER_API_URL: http://dify-api:5001` 이 있으므로, **플러그인이 이 값만 사용한다면** 연결은 되어야 합니다.
- 문제가 계속되면, **API/Worker가 플러그인 invoke 시 넘기는 URL**이 외부 URL로 고정돼 있는지 확인 (Dify 이슈/문서: “plugin invoke API URL”, “document extractor connection”).

### 3. 네트워크 접근성 점검

- plugin-daemon Pod에서 **dify-api** 로의 연결 확인:

```bash
kubectl exec -n dify deployment/dify-plugin-daemon -- curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://dify-api:5001/
```

- `404` 등 4xx가 나오면 **연결 자체는 성공**한 것이고, 플러그인이 잘못된 URL을 쓰는 경우일 수 있음.
- `Connection refused` 가 나오면 dify-api 서비스/포트(5001) 및 네트워크 폴리시를 확인.

### 4. 임시 회피 (파이프라인 변경)

- 해당 데이터셋의 **처리 파이프라인**에서 **Dify Extractor** 대신 다른 추출기(예: File 직접 입력 → Variable Aggregator 등)를 쓰면, 이 플러그인 연결은 사용하지 않게 됩니다.
- 이미 **LLM Generated Q&A 1 (txt→Extractor)** 에서 `.txt` 를 Dify Extractor 쪽으로 보내도록 수정한 상태라면, Connection refused 가 나는 경로만 우회하는 용도로 고려할 수 있습니다.

## 참고

- [Dify Plugin Daemon](https://github.com/langgenius/dify-plugin-daemon)
- [Dify Document Extractor](https://docs.dify.ai/en/guides/workflow/node/doc-extractor)
- Dify Helm chart: `api.env`, `worker.env`, `pluginDaemon.env` 에서 API URL 관련 변수 확인.
