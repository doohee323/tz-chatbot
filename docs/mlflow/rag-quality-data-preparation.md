# RAG 품질 개선용 데이터 준비 가이드

RAG 품질 개선을 위해 준비해야 할 데이터 항목과 형식을 정리합니다.

---

## 1. 수집·준비해야 할 데이터

### 1-1. 필수 데이터 (최소)

| 항목 | 설명 | 예시 |
|------|------|------|
| **question** | 사용자 질문 | "환불은 며칠 안에 가능한가?" |
| **retrieved_chunk_ids** | 검색된 chunk ID 목록 | `["doc1_chunk_3", "doc2_chunk_1"]` |
| **retrieved_scores** | 각 chunk의 유사도 점수 | `[0.92, 0.78]` |
| **answer** | 모델이 생성한 최종 답변 | "환불은 구매일로부터 7일 이내..." |
| **timestamp** | 요청 시각 | `2025-02-10T14:30:00Z` |

### 1-2. 추천 추가 데이터

| 항목 | 설명 | 용도 |
|------|------|------|
| **retrieved_chunk_contents** | 검색된 chunk 텍스트 | 답변 근거 분석, 오검색 분석 |
| **source_path** | chunk 출처 문서 경로 | 어떤 문서에서 왔는지 추적 |
| **latency_ms** | 질문 → 답변까지 걸린 시간 | 성능·지연 이슈 분석 |
| **model_name** | 사용한 LLM | 모델별 품질 비교 |
| **top_k** | 검색 chunk 개수 | 파라미터 튜닝 |
| **session_id** | 대화 세션 ID | 대화 흐름 분석 (선택) |

### 1-3. 평가용 데이터 (품질 개선의 목표치)

| 항목 | 설명 | 수집 방식 |
|------|------|-----------|
| **ground_truth** | 정답/기대 답변 | 수동 라벨링 or 기준 문서 |
| **is_correct** | 정답 여부 (0/1) | 수동 검수 or LLM-as-judge |
| **quality_score** | 1~5점 품질 점수 | 수동 평가 or 자동 평가 |
| **feedback** | 사용자 피드백 (좋음/나쁨) | UI 피드백 버튼 |
| **hallucination** | 환각 여부 (0/1) | 수동 or 자동 검출 |

---

## 2. 데이터 형식 예시

### 2-1. 챗 로그 (원시 데이터)

```json
{
  "log_id": "uuid",
  "timestamp": "2025-02-10T14:30:00Z",
  "question": "환불은 며칠 안에 가능한가?",
  "retrieved": [
    {"chunk_id": "abc123", "score": 0.92, "content": "환불 정책: 구매일로부터 7일 이내...", "source": "policy/refund_2025.pdf"},
    {"chunk_id": "def456", "score": 0.78, "content": "배송비는 고객 부담...", "source": "policy/shipping.md"}
  ],
  "answer": "환불은 구매일로부터 7일 이내에 가능합니다.",
  "latency_ms": 1200,
  "model": "gpt-4o-mini",
  "top_k": 5
}
```

### 2-2. 평가 세트 (학습/평가용)

```yaml
# expected_questions.yaml
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

## 3. 데이터 수집 흐름

1. **RAG Backend**: `question`, `retrieved_*`, `answer`, `latency_ms` 등을 로그로 남기기 (파일/DB).
2. **평가 스크립트**: 기대 질문 세트로 배치 호출 → 같은 형식으로 로그 저장.
3. **수동 평가 (선택)**: 샘플링한 질문에 대해 `is_correct`, `quality_score`, `hallucination` 라벨링.
4. **사용자 피드백 (선택)**: 챗 UI에 👍/👎 등 버튼 추가 → `feedback` 저장.

---

## 4. 우선 준비할 것 (체크리스트)

| 순서 | 작업 | 내용 |
|------|------|------|
| 1 | RAG Backend 로깅 | `question`, `retrieved_chunk_ids`, `retrieved_scores`, `answer`, `latency_ms`를 로그에 추가 |
| 2 | 기대 질문 세트 | 10~30개 질문 + `ground_truth` 또는 `keywords`를 YAML/JSON으로 정의 |
| 3 | 배치 평가 스크립트 | 기대 질문으로 API 호출 후 위 형식의 JSON 로그 생성 |
| 4 | 수동 평가 (선택) | 50~100개 샘플에 대해 `is_correct` 등 라벨링 |

---

## 5. 관련 문서

- [admin-use-case-mlflow-plan.md](./admin-use-case-mlflow-plan.md) — 관리자 Use Case 및 MLflow 품질 관리 계획
- [rag-quality-data-collection.md](../rag-quality-data-collection.md) — tz-chatbot에서의 취합 가능 여부·구현 상태
