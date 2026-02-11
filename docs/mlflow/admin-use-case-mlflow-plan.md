# 관리자(Admin) Use Case 및 MLflow 품질 관리 계획

**전제**: K8s + MinIO + Qdrant + RAG Backend + Dify + MLflow가 구성된 상태

## 🎯 관리자 목표

> "문서를 MinIO에 올리면, 챗봇이 헛소리 안 하고, 의도한 문서 기반으로, 일관되게 잘 답변하는지를 확인·개선·운영하고 싶다."

---

## 전체 시스템에서 각 컴포넌트의 역할 (관리자 시점)

| 시스템 | 관리자 관점의 역할 |
|--------|-------------------|
| **MinIO** | 정답의 원천(Source of Truth) — 관리자가 올린 문서가 여기 있음 |
| **RAG Ingest Job** | 문서를 읽어 → 쪼개고 → 임베딩 → 검색 가능하게 준비 |
| **Qdrant** | "이 질문에 관련된 문서 조각은 뭐지?"를 빠르게 찾는 엔진 |
| **RAG Backend** (FastAPI) | 검색 + 프롬프트 조립 + LLM 호출 (실제 두뇌) |
| **Dify** | 사용자용 챗 UI + 워크플로우 (관리자는 안쪽을 제어) |
| **MLflow** | "지금 챗봇 상태가 좋은가?"를 숫자·이력·비교로 관리 |

### 핵심 포인트

- **MinIO** = 지식 저장소
- **MLflow** = 품질 관리 대시보드
- **Dify** = 겉모습
- **RAG Backend** = 실제 로직

---

## tz-chatbot과의 매핑

| Use Case 컴포넌트 | tz-chatbot 구현 | 경로/설정 |
|-------------------|-----------------|-----------|
| MinIO | MinIO Helm (devops namespace) | `minio/`, bucket `rag-docs`, prefix `raw/drillquiz/` |
| RAG Ingest | `ingest.py` + CronJob/Job | `rag/scripts/ingest.py`, `rag/drillquiz/rag-ingestion-job-drillquiz.yaml` |
| Qdrant | Qdrant Deployment | `rag/qdrant-values.yaml`, collection `rag_docs_drillquiz` |
| RAG Backend | RAG Backend Deployment | `rag/drillquiz/rag-backend-drillquiz.yaml` |
| Dify | Dify Helm + 워크플로우 | `dify/`, DrillQuiz/CoinTutor 설정 |
| chat-gateway | Dify 앞단 API Gateway | `chat-gateway/` |
| **MLflow** | **추가 필요** | tz-mlops-mlflow 프로젝트의 MLflow 서버 연동 |

---

## Use Case: "문서 업로드 → 챗봇 검증 → 개선"

### STEP 1️⃣ 관리자가 문서를 MinIO에 업로드

**관리자 행동**

- PDF / Markdown / TXT 파일을 MinIO 버킷에 업로드  
- 예: `minio://rag-docs/raw/drillquiz/policy/refund_policy_2025.pdf`

**시스템 내부**

- 아직 챗봇은 아무것도 모름
- "원본 데이터만 저장된 상태"

**관리자 체크**

- 문서가 어디 버킷/경로에 들어갔는지 명확히 문서화
- 나중에 문제 추적 시 기준점이 됨

---

### STEP 2️⃣ RAG Ingest 파이프라인 실행 (자동 or 수동)

**관리자 행동**

- "이 문서들로 챗봇 학습해" 버튼 클릭 or
- 스케줄된 CronJob 자동 실행  
  - 예: `rag-ingestion-cronjob-drillquiz`

**시스템 내부 작업**

1. MinIO에서 문서 다운로드
2. 문서 파싱 (PDF → 텍스트)
3. 청킹 (chunk_size, chunk_overlap)
4. 임베딩 생성
5. Qdrant에 벡터 저장
6. 메타데이터 저장 (doc_id, source, path, created_at)

**MLflow에 기록할 항목 (추가 예정)**

| 항목 | 내용 |
|------|------|
| params | chunk_size, chunk_overlap, embedding_model, embedding_provider, minio_prefix, qdrant_collection |
| metrics | num_documents, num_chunks, ingest_duration_sec |
| artifacts | 파싱된 텍스트 샘플, 청킹 결과 통계 |
| tags | topic=drillquiz, mode=incremental\|full |

**관리자 체크**

- "이 문서는 어떤 설정으로 인덱싱됐는가"를 나중에 반드시 알 수 있어야 함
- → MLflow가 이 정보를 보관

---

### STEP 3️⃣ 관리자가 "기대 질문 세트"로 테스트

**관리자 행동**

- 미리 준비한 질문 리스트 실행  
  - Q1. 환불은 며칠 안에 가능한가?  
  - Q2. 배송비는 누가 부담하나?  
  - Q3. 약관 버전은 무엇인가?

**시스템 내부**

1. 질문 → Qdrant 검색
2. 관련 문서 chunk N개 선택
3. 프롬프트 조립
4. LLM 호출 → 답변 생성

**MLflow에 기록할 항목 (추가 예정)**

| 항목 | 내용 |
|------|------|
| params | question, top_k, temperature |
| metrics | latency_ms, retrieval_score, (가능하면) 자동 평가 점수 |
| artifacts | 검색된 chunk ID 목록, 최종 답변, 사용된 문서 버전 |

**관리자 체크**

- 답변이 문서에 근거했는가?
- 엉뚱한 말(환각)이 없는가?
- 질문별로 일관적인가?

---

### STEP 4️⃣ "챗봇이 왜 이렇게 답했는지" 추적

**관리자가 보고 싶은 것**

- "왜 Q2에서 이상한 답이 나왔지?"

**MLflow에서 확인**

- 어떤 chunk가 검색됐는지
- 검색 점수
- 프롬프트 내용
- 사용된 문서 버전

**문제 유형 예**

- chunk가 너무 작음 → 문맥 손실
- 오래된 문서가 검색됨
- top_k가 너무 큼

**관리자 관점**

- "모델이 멍청한 게 아니라 설정이 잘못됐다"를 증명할 수 있어야 함

---

### STEP 5️⃣ 설정 변경 후 재학습 (개선 루프)

**관리자 행동**

- chunk_size 변경
- embedding 모델 변경
- 특정 문서 제외
- reranker 활성화

**시스템**

1. 다시 ingest
2. 다시 평가
3. 이전 버전과 비교

**MLflow**

- Run A vs Run B 비교
- 점수/지표 그래프
- "이 설정이 더 낫다"를 수치로 확인

**관리자 관점**

- "감으로 좋아진 것 같아요" ❌
- "이 설정이 정량적으로 더 낫다" ⭕️

---

### STEP 6️⃣ 검증 완료 → Dify/서비스 반영

**관리자 행동**

- "이 RAG backend 버전 사용"으로 스위치
- 사용자에게 공개

**운영 중**

- 사용자 질문 로그
- 실패 질문 수집
- 주기적 재평가

---

## 핵심 가치 (관리자 시점 요약)

| 질문 | 답 |
|------|-----|
| 문서를 바꾸면 뭐가 바뀌었는지 알 수 있나? | ⭕ MLflow로 추적 |
| 챗봇이 틀리면 원인을 찾을 수 있나? | ⭕ 검색/프롬프트까지 추적 |
| 설정 변경 효과를 비교할 수 있나? | ⭕ Run 비교 |
| 운영자가 통제권을 가지나? | ⭕ 완전히 |

> **한 줄 요약**: "문서를 올리는 것 자체보다, 챗봇이 잘 대답하도록 '관리·검증·개선'할 수 있게 설계된 구조다."

---

## 구현 계획 (MLflow 연동)

### Phase 1: MLflow 환경 연결

| # | 작업 | 설명 |
|---|------|------|
| 1-1 | MLflow 서버 확인 | tz-mlops-mlflow의 MLflow Tracking (https://mlflow.drillquiz.com) 접근 가능 여부 확인 |
| 1-2 | RAG 전용 Experiment 생성 | `rag_quality` 또는 `rag_drillquiz` experiment 생성 |
| 1-3 | 인증 설정 | MLFLOW_TRACKING_URI, MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD를 Ingest Job / Backend에 전달 |

### Phase 2: Ingest Job에 MLflow 로깅 추가

| # | 작업 | 설명 |
|---|------|------|
| 2-1 | ingest.py 수정 | `mlflow.start_run()`, params (CHUNK_SIZE, EMBEDDING_MODEL 등), metrics (num_chunks, duration) 로깅 |
| 2-2 | Ingest Job env 추가 | MLFLOW_* 환경변수 추가, mlflow 패키지 의존성 추가 |
| 2-3 | Run 이름 규칙 | `ingest_{topic}_{timestamp}` 또는 `ingest_{minio_prefix}_{mode}` |

### Phase 3: 평가(Evaluation) 파이프라인 추가

| # | 작업 | 설명 |
|---|------|------|
| 3-1 | 기대 질문 세트 정의 | YAML/JSON으로 질문-정답 또는 질문-기대 키워드 정의 |
| 3-2 | evaluate_rag.py 스크립트 | 질문 실행 → RAG Backend 호출 → 답변 수집 → MLflow에 Run별로 로깅 |
| 3-3 | 자동 평가 (선택) | LLM-as-judge 또는 키워드 매칭으로 점수화 → mlflow.log_metric() |
| 3-4 | Airflow DAG (선택) | Ingest → Evaluate 순차 DAG 구성 |

### Phase 4: RAG Backend에서 질문별 추적 (선택)

| # | 작업 | 설명 |
|---|------|------|
| 4-1 | Backend 요청/응답 로깅 | question, retrieved_chunk_ids, latency, answer를 MLflow에 child run으로 기록 |
| 4-2 | 디버그 모드 | MLFLOW_LOG_QUERIES=true일 때만 로깅 (성능 영향 최소화) |

### Phase 5: 운영 대시보드 및 개선 루프

| # | 작업 | 설명 |
|---|------|------|
| 5-1 | MLflow UI 활용 | Run 비교, 파라미터·메트릭 정렬, best run 선택 |
| 5-2 | 문서화 | "이 버전의 ingest 설정"과 "평가 점수"를 팀에 공유 |
| 5-3 | 정기 재평가 | 주기적으로 evaluate_rag.py 실행, 점수 하락 시 알림 |

---

## 파일 구조 (추가/수정 예상)

```
refer/tz-chatbot/
├── rag/
│   ├── scripts/
│   │   ├── ingest.py          # MLflow 로깅 추가
│   │   └── evaluate_rag.py    # 신규: 기대 질문 세트 실행 및 MLflow 로깅
│   ├── config/
│   │   └── expected_questions.yaml  # 신규: 기대 질문 세트
│   └── drillquiz/
│       └── rag-ingestion-job-drillquiz.yaml  # MLFLOW_* env 추가
└── docs/
    └── mlflow/
        └── admin-use-case-mlflow-plan.md  # 본 문서
```

---

## 다음 단계

1. **Phase 1** 완료 후 `ingest.py`에 MLflow 로깅 코드 추가
2. `expected_questions.yaml` 샘플 작성 (DrillQuiz 정책 관련 3~5문항)
3. `evaluate_rag.py` 스크립트 작성 및 로컬 테스트
4. 필요 시 Airflow DAG로 Ingest → Evaluate 파이프라인 구성
