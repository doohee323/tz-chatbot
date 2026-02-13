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

## 2. 필요한 데이터 항목 (rag-quality-data-collection 기준)

### 2-1. 필수 (최소)

| 항목 | 설명 | 수집 위치 |
|------|------|-----------|
| **question** | 사용자 질문 | chat-gateway |
| **answer** | 모델 최종 답변 | chat-gateway |
| **timestamp** | 요청 시각 | chat-gateway |
| **conversation_id** | 대화 세션 ID | chat-gateway |
| **message_id** | 메시지 ID | chat-gateway |

### 2-2. 추천 추가 (RAG·품질 분석 시)

| 항목 | 설명 | 수집 위치 |
|------|------|-----------|
| **retrieved** | RAG 검색 결과 (chunk_id, score, content, source_path) | Dify metadata → 매핑 |
| **top_k** | 검색 chunk 개수 | Dify metadata (워크플로 출력 시) |
| **collection** | Qdrant collection | Dify metadata (워크플로 출력 시) |
| **latency_ms** | 소요 시간(ms) | Dify metadata.usage.latency → 변환 |
| **model_name** | 사용 LLM | Dify metadata (워크플로 출력 시) |
| **system_id** | 출처 시스템 (cointutor, drillquiz) | chat-gateway |
| **dify_metadata** | Dify 응답 metadata 전체 (usage, retriever_resources 등) | Dify API 응답 그대로 저장 |

### 2-3. Dify API 실제 응답과 매핑

chat-gateway는 Dify **Chatflow /chat-messages** 응답의 `metadata`를 그대로 쓰지 않고, 아래처럼 매핑한다.

| 우리 필드 | Dify 응답 | 비고 |
|-----------|-----------|------|
| **retrieved** | `metadata.retriever_resources` | 배열 항목을 `chunk_id`(segment_id), `score`, `content`, `source_path`(document_name) 형태로 변환 |
| **latency_ms** | `metadata.usage.latency` | Dify는 초 단위이면 ×1000 해서 ms로 저장 |
| **top_k**, **collection**, **model_name** | (없음) | Dify 기본 응답에는 없음. 워크플로에서 **메타데이터 출력**으로 넣어 주면 수집됨 |

- RAG를 쓰는 앱이면 `retriever_resources`가 채워지고, 위 매핑으로 `retrieved`가 MinIO JSON에 들어간다.
- `top_k`/`collection`/`model_name`을 쓰려면 Dify 워크플로 노드에서 “메타데이터에 추가”하도록 설정해야 한다.

### 2-4. 전체 Dify metadata 저장 (dify_metadata)

**누락 없이** 분석·재현을 위해, Dify `/chat-messages` 응답의 `metadata` 객체 전체를 MinIO JSON의 **`dify_metadata`** 필드에 그대로 저장한다.

**참고(커스텀 도구 RAG)**: DrillQuiz처럼 워크플로에서 **API 도구(Tool)** 노드(예: DrillQuiz RAG)로만 RAG를 호출하는 경우, Dify는 `metadata.retriever_resources`를 채우지 않는다. 내장 **Knowledge Retrieval** 노드를 쓰면 이 필드가 채워진다. 커스텀 도구만 쓰면 답변은 RAG 기반이어도 `retriever_resources`는 빈 배열로 온다.

| Dify metadata 필드 | 설명 |
|--------------------|------|
| **usage** | prompt_tokens, completion_tokens, total_tokens, latency(초), time_to_first_token, time_to_generate, 가격 등 |
| **retriever_resources** | RAG 검색 결과 원본 (dataset_id, document_id, segment_id, score, content 등) |
| **annotation_reply** | 어노테이션 답변 (있을 경우) |
| 기타 | 워크플로에서 메타데이터로 추가한 모든 필드 |

- 상위 필드(retrieved, latency_ms 등)는 위 매핑으로 **정규화**해 두고, `dify_metadata`에는 **원본 전체**를 넣어 두므로, 이후 스키마가 바뀌어도 원본을 활용할 수 있다.

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

**정규화 필드** (분석·쿼리용) + **dify_metadata** (원본 전체).

```json
{
  "log_id": "uuid",
  "log_type": "chat_quality",
  "timestamp": "2025-02-12T10:30:00Z",
  "system_id": "cointutor",
  "project": "cointutor",
  "topic": "default",
  "conversation_id": "conv-xxx",
  "message_id": "msg-xxx",
  "question": "환불은 며칠 안에 가능한가?",
  "answer": "환불은 구매일로부터 7일 이내에 가능합니다.",
  "retrieved": [
    {
      "chunk_id": "abc123_chunk_0",
      "score": 0.92,
      "content": "환불 정책: 구매일로부터 7일 이내...",
      "source_path": "policy/refund_2025.pdf"
    }
  ],
  "top_k": 5,
  "collection": "rag_docs_cointutor",
  "latency_ms": 1200,
  "model_name": "gpt-4o-mini",
  "dify_metadata": {
    "annotation_reply": null,
    "retriever_resources": [],
    "usage": {
      "prompt_tokens": 1399,
      "completion_tokens": 326,
      "total_tokens": 1725,
      "latency": 1.2,
      "time_to_first_token": 0.8,
      "time_to_generate": 0.4,
      "total_price": "0.0012347",
      "currency": "USD"
    }
  }
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

### 6-4. MinIO 저장 확인

- chat-gateway 로그: `Chat quality stored to MinIO: rag-quality-data/{project}/{topic}/raw/...`
- MinIO 콘솔 또는 mc: `mc ls myminio/rag-quality-data/drillquiz/default/raw/$(date +%Y-%m-%d)/`
- port-forward 시: `kubectl port-forward svc/minio 9000:9000 -n devops` 후 `http://localhost:9000` 접속

---

## 7. 구현 체크리스트

### tz-chatbot (데이터 수집·저장)

- [x] chat-gateway `record_chat_to_minio` 구현
- [x] MinIO 버킷 동적 생성 (없으면 make_bucket)
- [x] chat-gateway에서 대화마다 MinIO 업로드 (record_chat 후 호출)
- [ ] Dify 워크플로우에서 RAG 메타데이터(retrieved 등)를 응답 metadata에 포함하도록 설정 (선택)

### tz-mlops-mlflow (ML 소비)

- [ ] MinIO `rag-quality-data` 경로에서 데이터 읽기 유틸/스크립트
- [ ] MLflow 평가 파이프라인에서 소스 데이터로 사용
