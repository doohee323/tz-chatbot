# Chat 품질 데이터 MinIO 저장 계획

MLflow 기반 RAG 품질 개선을 위해, 대화 데이터를 MinIO에 저장하는 **스키마·버킷 구조** 및 구현을 정의합니다.

---

## 0. 프로젝트 역할 분리

| 프로젝트 | 역할 |
|----------|------|
| **tz-chatbot** | 데이터 수집·저장 — chat-gateway가 대화를 MinIO에 직접 기록 |
| **tz-mlops-mlflow** | ML 소비 — MinIO에 쌓인 데이터를 읽어 MLflow 학습·평가·품질 파이프라인에 사용 |

---

## 1. 구현 방식

- **chat-gateway**: `record_chat_to_db` 후 **MinIO 직접 업로드** (`record_chat_to_minio`)
- 별도 API 없이, gateway 내부에서 `app/services/chat_quality_minio.py` 호출
- 환경변수 `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` 설정 시 활성화 (미설정 시 스킵)

---

## 2. 저장하는 데이터 (기존 필드 + 분석용 필드)

기존 필드(지식 검색/위키피디아 등 실행 맥락)와 분석용 필드(품질 평가) **둘 다** 저장한다.

### 2-1. 저장 필드

| 구분 | 항목 | 설명 |
|------|------|------|
| **식별·경로** | log_id, log_type, timestamp, question, answer, conversation_id, message_id, system_id, project, topic | 로그 식별·경로·대화 식별 |
| **기존 (Dify)** | **retrieved** | 지식 검색/위키피디아 검색 결과 (retriever_resources 매핑). 지식 검색 경로면 채워져야 함 |
| | **top_k**, **collection** | 검색 개수, 사용한 knowledge base/소스 |
| | **latency_ms**, **model_name** | 소요 시간, 사용 LLM (성능·비용 분석) |
| | **dify_metadata** | Dify 응답 metadata 전체 (usage 등) |
| **분석용** | **question_id**, **ground_truth**, **keywords** | 기대 질문 세트 매칭 시 (LLM-as-judge·일관성 검사) |

**retriever_resources 참고**: 워크플로에서 "지식 검색" 또는 "위키피디아" 경로로 질문이 가면 검색이 수행된다. Dify **내장 Knowledge Retrieval** 노드를 쓰면 `metadata.retriever_resources`가 채워지고, gateway가 이를 `retrieved`로 매핑해 저장한다. (API 도구(Tool)로만 검색하면 Dify가 retriever_resources를 비울 수 있음. "코인튜터는?"처럼 지식 검색으로 가야 하는데 비어 있으면, Dify 앱에서 해당 노드가 내장 지식 검색인지·메타데이터 노출 설정인지 확인할 것.)

### 2-2. ground_truth / keywords (기대 질문 세트)

수동으로 정의한 **기대 질문 세트(YAML)**와 매칭되면, 해당 레코드에 `question_id`, `ground_truth`, `keywords`를 붙여 저장한다. → LLM-as-judge, 키워드 기반 자동 점수화, 일관성 검사에 활용.

| 환경변수 | 설명 |
|----------|------|
| **EXPECTED_QUESTIONS_PATH** | YAML 파일 경로 (예: `/app/config/expected_questions.yaml`) |

- YAML 형식: `questions:` 아래에 `id`, `question`, `ground_truth`, `keywords` 리스트. 사용자 질문 문자열과 **완전 일치**하는 항목이 있으면 해당 id/ground_truth/keywords를 로그에 추가.
- 예시: `chat-gateway/config/expected_questions.cointutor.example.yaml` 참고.

---

## 3. MinIO 버킷 구조 (트리: 프로젝트 → 토픽)

```
rag-quality-data/                          # 버킷 (없으면 동적 생성)
├── {project}/                            # cointutor, drillquiz
│   └── {topic}/                          # default, policy, faq 등
│       └── raw/
│           └── {date}/                   # YYYY-MM-DD
│               └── {log_id}.json
├── processed/                            # (향후)
└── evaluation/                           # (향후)
```

- **버킷**: `rag-quality-data` (없으면 업로드 시 자동 생성)
- **경로**: `{project}/{topic}/raw/{date}/{log_id}.json`
- **project** = system_id (cointutor, drillquiz)
- **topic** = metadata.topic 또는 collection에서 추출, 없으면 "default"

---

## 4. 데이터 형식 (JSON)

기존 필드(실행 맥락) + 분석용 필드 모두 저장.

```json
{
  "log_id": "uuid",
  "log_type": "chat_quality",
  "timestamp": "2025-02-12T10:30:00Z",
  "project": "cointutor",
  "topic": "default",
  "question": "코인튜터는?",
  "answer": "코인튜터는 대한민국의 블록체인 및 암호화폐 전문 교육 기관입니다...",
  "conversation_id": "conv-xxx",
  "message_id": "msg-xxx",
  "system_id": "cointutor",
  "retrieved": [
    { "chunk_id": "abc_chunk_0", "score": 0.92, "content": "...", "source_path": "USER_GUIDE_QA..." }
  ],
  "top_k": 5,
  "collection": "rag_docs_cointutor",
  "latency_ms": 1200,
  "model_name": "Gemini CHAT",
  "dify_metadata": { "usage": { "total_tokens": 1725, "latency": 1.2 }, "retriever_resources": [] },
  "question_id": "q_cointutor_1",
  "ground_truth": "블록체인 및 암호화폐 전문 교육 기관",
  "keywords": ["블록체인", "암호화폐", "교육", "2018"]
}
```

---

## 5. chat-gateway 설정

### 5-1. 환경변수 (.env 또는 K8s Secret/ConfigMap)

| 변수 | 설명 | 예시 |
|------|------|------|
| MINIO_ENDPOINT | MinIO API URL | `http://minio.devops.svc.cluster.local:9000` |
| MINIO_ACCESS_KEY | Access Key (rootUser 또는 IAM) | |
| MINIO_SECRET_KEY | Secret Key (rootPassword 또는 IAM) | |
| MINIO_RAG_QUALITY_BUCKET | 버킷명 (기본: rag-quality-data) | `rag-quality-data` |
| EXPECTED_QUESTIONS_PATH | 기대 질문 YAML (ground_truth/keywords 매칭) | `/app/config/expected_questions.yaml` |

### 5-2. K8s 배포 시

chat-gateway Deployment에 env 추가:

```yaml
env:
  - name: MINIO_ENDPOINT
    value: "http://minio.devops.svc.cluster.local:9000"
  - name: MINIO_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: minio  # 또는 rag-quality-minio-secret
        key: rootUser
  - name: MINIO_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: minio
        key: rootPassword
```

---

## 6. 테스트 (curl)

채팅 결과 기록(DB + MinIO)은 **POST /v1/chat** 한 번으로 트리거된다. 응답이 오면 백그라운드에서 `record_chat_to_db` → `record_chat_to_minio` 가 수행된다.

### 채팅 결과 기록 API (curl 샘플)

```bash
# 환경 변수 (로컬 예시)
export GATEWAY_URL="http://localhost:8088"
export API_KEY="your-chat-gateway-api-key"

# 채팅 전송 → DB 기록 + MinIO 기록(백그라운드) 트리거
curl -s -X POST "${GATEWAY_URL}/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "system_id": "drillquiz",
    "user_id": "test-user-001",
    "message": "환불은 며칠 안에 가능한가?"
  }' | jq .
```

- **응답**: `conversation_id`, `message_id`, `answer`, `metadata`(Dify 원본)
- **기록**: 동일 요청 기준으로 SQLite/DB에 대화 저장, MinIO `rag-quality-data/{project}/{topic}/raw/{date}/{log_id}.json` 에 JSON 저장

### 6-1. Chat API 호출 (API Key 사용)

```bash
# 환경 변수
export GATEWAY_URL="http://localhost:8088"   # 또는 https://chat.drillquiz.com
export API_KEY="your-chat-gateway-api-key"

# 대화 전송 (MinIO 저장 트리거)
curl -X POST "${GATEWAY_URL}/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "system_id": "drillquiz",
    "user_id": "test-user-001",
    "message": "환불은 며칠 안에 가능한가?"
  }'
```

### 6-2. JWT 토큰 사용 (챗 페이지용)

로컬 curl에서 `/v1/chat-token` 호출 시 **Origin 헤더**가 필요하다 (허용 목록에 없으면 403). 브라우저는 자동으로 보냄.

```bash
# 1) 토큰 발급 (curl 사용 시 Origin 헤더 추가)
TOKEN=$(curl -s -X GET "${GATEWAY_URL}/v1/chat-token?system_id=drillquiz&user_id=test-user-001" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Origin: http://localhost:8088" \
  | jq -r '.token')

# 2) Chat API 호출 (Bearer 토큰)
curl -X POST "${GATEWAY_URL}/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "message": "배송비는 누가 부담하나?"
  }'
```

### 6-3. 기존 대화 이어하기 (conversation_id)

`conversation_id`는 **동일 system_id**에서 생성된 값이어야 한다 (다른 system_id면 Dify에서 404).

```bash
# 이전 6-1/6-2 응답의 conversation_id 사용, system_id/user_id 동일하게
curl -X POST "${GATEWAY_URL}/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "system_id": "drillquiz",
    "user_id": "test-user-001",
    "conversation_id": "이전_응답의_conversation_id",
    "message": "추가 질문입니다."
  }'
```

### 6-4. MinIO 저장 확인 (ML용 데이터가 실제로 쌓이는지)

**저장되는 조건**

- chat-gateway(예: chat.drillquiz.com)에 **다음 3개 환경변수**가 모두 설정되어 있어야 함:
  - `MINIO_ENDPOINT`
  - `MINIO_ACCESS_KEY`
  - `MINIO_SECRET_KEY`
- 하나라도 비어 있으면 `record_chat_to_minio`는 **호출되지만 업로드를 스킵**하고 로그에 `Chat quality MinIO: skipped (... not configured)` 가 남음.

**K8s에서 MinIO 미저장 원인 확인 (실제 사례)**

- **ConfigMap** (`chat-gateway-configmap-main` 등): `MINIO_ENDPOINT`, `MINIO_RAG_QUALITY_BUCKET` 는 있음.
- **Secret** (`chat-gateway-secret-main` 등): `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` **키가 아예 없을 수 있음** → 이 경우 Pod에 두 값이 주입되지 않아 MinIO 업로드 스킵됨.
- 확인: `kubectl get secret chat-gateway-secret-main -n devops -o jsonpath='{.data}' | jq -r 'keys[]'` 에 `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` 가 없으면 저장 안 됨.
- **조치**: Secret에 MinIO 인증 정보 추가 후 rollout restart. 예:
  ```bash
  kubectl patch secret chat-gateway-secret-main -n devops -p "{\"data\":{\"MINIO_ACCESS_KEY\":\"$(echo -n 'YOUR_MINIO_ACCESS_KEY' | base64)\",\"MINIO_SECRET_KEY\":\"$(echo -n 'YOUR_MINIO_SECRET_KEY' | base64)\"}}"
  kubectl rollout restart deployment/chat-gateway -n devops
  ```
  (CI에서 배포 시 `ci/k8s.sh` 가 Secret을 생성할 때 `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` 환경변수를 넘겨 placeholder를 치환하도록 되어 있음. 배포 파이프라인에서 이 두 값을 설정해 주어야 함.)

**저장 여부 확인 방법**

| 방법 | 확인 내용 |
|------|------------|
| **Gateway 로그** | `Chat quality stored to MinIO: rag-quality-data/cointutor/default/raw/2026-02-13/...` 처럼 남으면 저장됨. `skipped` 또는 `Failed to store` 면 미저장/실패. |
| **MinIO 버킷** | 버킷 `rag-quality-data` 아래 `cointutor/` 또는 `drillquiz/` → `default/`(또는 topic) → `raw/` → `YYYY-MM-DD/` → `{log_id}.json` 파일 존재 여부. |
| **mc CLI** | `mc ls myminio/rag-quality-data/cointutor/default/raw/$(date +%Y-%m-%d)/` |
| **K8s port-forward** | `kubectl port-forward svc/minio 9000:9000 -n devops` 후 브라우저 `http://localhost:9000` → 버킷·경로 확인. |

CoinTutor에서 채팅 전송 시 요청이 `https://chat.drillquiz.com/v1/chat` 로 가므로, **같은 chat-gateway**가 MinIO에 기록한다. 해당 Pod/인스턴스에 위 환경변수가 주입되어 있어야 ML용 데이터가 MinIO에 쌓인다.

---

## 7. 구현 체크리스트

### tz-chatbot (데이터 수집·저장)

- [x] chat-gateway `record_chat_to_minio` 구현
- [x] MinIO 버킷 동적 생성 (없으면 make_bucket)
- [x] chat-gateway에서 대화마다 MinIO 업로드 (record_chat 후 호출)
- [x] MinIO payload에 `question_id`, `ground_truth`, `keywords` 저장 (기대 질문 매칭 시)
- [x] EXPECTED_QUESTIONS_PATH 로 기대 질문 YAML 로드 후 질문 매칭 시 ground_truth/keywords 부여
- [ ] Dify 워크플로우에서 RAG 메타데이터(retrieved 등)를 응답 metadata에 포함하도록 설정 (선택)

### tz-mlops-mlflow (ML 소비)

- [ ] MinIO `rag-quality-data` 경로에서 데이터 읽기 유틸/스크립트
- [ ] MLflow 평가 파이프라인에서 소스 데이터로 사용
