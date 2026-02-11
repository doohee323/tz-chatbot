# RAG 품질 개선용 데이터 취합 가이드

ML/RAG 품질 개선을 위해 필요한 데이터 항목과, tz-chatbot에서 **취합 가능 여부** 및 **구현 상태**를 정리합니다.

---

## 1. 필요 데이터와 취합 가능 여부

### 1-1. 필수 데이터 (최소)

| 항목 | 설명 | 취합 가능 여부 | 수집 위치 |
|------|------|----------------|-----------|
| **question** | 사용자 질문 | ✅ 가능 | RAG Backend 요청, chat-gateway DB(MessageCache) |
| **retrieved_chunk_ids** | 검색된 chunk ID 목록 | ✅ 가능 | RAG Backend에서 응답에 포함·로그 (doc_id + chunk_index) |
| **retrieved_scores** | 각 chunk 유사도 점수 | ✅ 가능 | RAG Backend 응답·로그에 이미 포함 |
| **answer** | 모델이 생성한 최종 답변 | ✅ 가능 | chat-gateway DB(MessageCache, assistant 메시지) |
| **timestamp** | 요청 시각 | ✅ 가능 | RAG Backend·gateway 양쪽에서 기록 |

### 1-2. 추천 추가 데이터

| 항목 | 취합 가능 여부 | 비고 |
|------|----------------|------|
| **retrieved_chunk_contents** | ✅ 가능 | RAG Backend 응답·품질 로그에 포함 |
| **source_path** | ✅ 가능 | ingest 시 metadata.path, Backend 응답에 포함 |
| **latency_ms** | ✅ 가능 | RAG Backend에서 /query 처리 시간 측정·로그 |
| **model_name** | ⚠️ Dify 설정 | Dify 워크플로우에서 사용 중인 LLM; Backend에는 없음. gateway에서 Dify 메타데이터로 수집 가능 시 추가 |
| **top_k** | ✅ 가능 | RAG Backend 요청 파라미터·로그 |
| **session_id** | ✅ 가능 | conversation_id (gateway DB)로 대체 가능 |

### 1-3. 평가용 데이터 (목표치)

| 항목 | 수집 방식 | 비고 |
|------|-----------|------|
| **ground_truth** | 수동 라벨링 or 기준 문서 | 기대 질문 세트(YAML/JSON)로 관리 |
| **is_correct** | 수동 검수 or LLM-as-judge | 별도 평가 스크립트·파이프라인 |
| **quality_score** | 수동 평가 or 자동 평가 | 동일 |
| **feedback** | UI 피드백 버튼 | chat-admin/프론트 확장 시 추가 |
| **hallucination** | 수동 or 자동 검출 | 평가 스크립트에서 처리 |

---

## 2. 현재 구조에서의 수집 흐름

```
[클라이언트] → [chat-gateway] → [Dify] → [RAG Backend /query] → Qdrant
                    ↓                          ↓
              MessageCache 저장          품질 로그 (JSON 라인)
              (question, answer,          question, retrieved_*,
               conversation_id, timestamp)  latency_ms, top_k, timestamp
```

- **RAG Backend**: `/query` 호출 시 `question`, `retrieved_chunk_ids`, `retrieved_scores`, `retrieved_chunk_contents`, `source_path`, `top_k`, `latency_ms`, `timestamp` 를 **구조화 로그**(JSON 라인)로 출력. 환경변수로 로깅 on/off.
- **chat-gateway**: 기존대로 `record_chat_to_db`로 사용자 질문(question)과 assistant 답변(answer), `conversation_id`, `created_at` 저장.
- **취합**: RAG 로그와 gateway DB를 **timestamp + question(또는 conversation_id)** 기준으로 나중에 매칭·병합. 또는 배치 평가 스크립트는 기대 질문만 RAG에 보내서 로그 생성.

---

## 3. 구현된 항목

| 순서 | 작업 | 상태 |
|------|------|------|
| 1 | RAG Backend: chunk_id 응답 포함, 품질 로그(question, retrieved_*, latency_ms, top_k) 출력 | ✅ 본 문서와 동일 커밋에서 반영 |
| 2 | 기대 질문 세트 예시 (YAML) | ✅ `rag/scripts/expected_questions.example.yaml` |
| 3 | 배치 평가 스크립트 (기대 질문으로 /query 호출 후 로그 생성) | ✅ `rag/scripts/batch_eval_rag.py` |
| 4 | 수동 평가·피드백 UI | 미구현 (선택) |

**품질 로그 활성화 (K8s)**  
RAG Backend Deployment에 환경변수 추가 후 재배포:

```yaml
env:
  - name: RAG_QUALITY_LOG
    value: "1"
```

로그는 Pod 표준출력(stdout)에 한 줄씩 출력되므로, Loki·Fluentd 등으로 수집하거나 `kubectl logs`로 확인할 수 있습니다.

---

## 4. 데이터 형식 예시

### 4-1. RAG Backend 품질 로그 (한 줄 JSON)

환경변수 `RAG_QUALITY_LOG=1` 로 활성화 시, 표준출력에 한 요청당 한 줄씩 출력됩니다.

```json
{"log_type":"rag_query","timestamp":"2025-02-10T14:30:00Z","question":"환불은 며칠 안에 가능한가?","retrieved":[{"chunk_id":"abc123_chunk_0","score":0.92,"content":"환불 정책: 구매일로부터 7일 이내...","source_path":"policy/refund_2025.pdf"},{"chunk_id":"def456_chunk_1","score":0.78,"content":"배송비는 고객 부담...","source_path":"policy/shipping.md"}],"top_k":5,"collection":"rag_docs_cointutor","latency_ms":120}
```

### 4-2. 챗 로그 (gateway DB + RAG 로그 병합)

- **MessageCache**: `conversation_id`, `message_id`, `role`(user/assistant), `content`, `created_at`
- user 메시지 = question, assistant 메시지 = answer. RAG 로그와 매칭 시 `created_at` ± 수 초 + `content`(question) 유사도로 연결.

### 4-3. 평가 세트 (기대 질문)

`rag/scripts/expected_questions.example.yaml` 참고.

```yaml
questions:
  - id: "q1"
    question: "환불은 며칠 안에 가능한가?"
    ground_truth: "7일 이내"
    keywords: ["7일", "환불"]
  - id: "q2"
    question: "배송비는 누가 부담하나?"
    ground_truth: "고객 부담"
    keywords: ["고객", "배송비"]
```

---

## 5. 우선 준비하면 좋은 것 (요약)

1. **RAG Backend 로깅**: `question`, `retrieved_chunk_ids`, `retrieved_scores`, `retrieved_chunk_contents`, `source_path`, `top_k`, `latency_ms`, `timestamp` → 구현됨. 배포 시 `RAG_QUALITY_LOG=1` 설정.
2. **기대 질문 세트**: 10~30개 질문 + ground_truth/keywords를 YAML로 정의 → 예시 추가됨.
3. **배치 평가 스크립트**: 기대 질문으로 RAG `/query` 호출 후 동일 형식 JSON 로그 생성 → `batch_eval_rag.py` 추가됨.
4. **수동 평가(선택)**: 50~100개 샘플에 대해 is_correct 등 라벨링 → 별도 도구/스프레드시트 권장.

이 정도 데이터가 모이면 RAG 품질 개선 실험(검색 파라미터, top_k, 프롬프트 비교 등)을 진행할 수 있습니다.
