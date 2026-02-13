# Chat API에서 MinIO 로깅 보강 방법

MinIO에 쌓이는 `chat_quality` 로그에서 **ground_truth**, **일관성·샘플 수**를 어떻게 채울 수 있는지 정리합니다.

---

## 1. 부족했던 부분과 해결 방식

| 부족한 부분 | 원인 | Chat API에서의 취합 방법 |
|-------------|------|---------------------------|
| **ground_truth** | 수동 정의 필요 | 기대 질문 세트 YAML(`expected_questions.yaml`)에 정의 후, 질문 문자열 매칭 시 자동 부여 |
| **샘플 수** | 트래픽/사용량에 의존 | 기대 질문으로 배치 호출(`batch_eval_rag.py`) + 실서비스 로그 병행 수집 |

---

## 2. 구체적 설정 (chat-gateway)

### 2-1. ground_truth / keywords (기대 질문 세트)

**환경변수**

- `EXPECTED_QUESTIONS_PATH`: YAML 파일 절대 경로 (예: `/app/config/expected_questions.yaml`)

**YAML 형식 예 (expected_questions.yaml)**

```yaml
questions:
  - id: "q_cointutor_1"
    question: "코인튜터는?"
    ground_truth: "블록체인 및 암호화폐 전문 교육 기관"
    keywords: ["블록체인", "암호화폐", "교육", "2018"]
```

- 사용자 질문과 **문자열 완전 일치**하는 항목이 있으면, 해당 로그에 `question_id`, `ground_truth`, `keywords`가 자동으로 들어갑니다.
- 예시 파일: `chat-gateway/config/expected_questions.cointutor.example.yaml`

---

## 3. MinIO 로그에 저장되는 필드

**기존 필드**와 **분석용 필드** 모두 저장한다.

| 구분 | 필드 | 설명 |
|------|------|------|
| 식별·경로 | log_id, log_type, timestamp, question, answer, conversation_id, message_id, system_id, project, topic | 로그·경로·대화 식별 |
| 기존 (Dify) | **retrieved** | 지식 검색/위키피디아 검색 결과 (retriever_resources가 있으면 채워짐) |
| | **top_k**, **collection**, **latency_ms**, **model_name** | 검색 파라미터·소스·성능·모델 |
| | **dify_metadata** | usage 등 Dify metadata 전체 |
| 분석용 | **question_id**, **ground_truth**, **keywords** | 기대 질문 매칭 시 (품질·일관성 평가) |

---

## 3-1. `metadata.retriever_resources`가 비어 있을 때 (순수 curl에서도 `[]`인 이유)

**gateway 동작**: Dify 응답의 `result.metadata`를 그대로 읽어, `retriever_resources`가 있으면 `retrieved`로 매핑해 MinIO에 저장한다. **비어 있으면 Dify가 빈 배열을 준 경우**이다.

### 순수 curl에서 안 나오는 직접 원인 (Dify 소스 기준)

Dify `message_cycle_manager.handle_retriever_resources()`는 **아래 조건을 만족할 때만** `task_state.metadata.retriever_resources`에 값을 넣습니다.

- `app_config.additional_features` 가 있고  
- **`additional_features.show_retrieve_source` 가 True** 일 때만

즉, **앱 발행(Features)에서 "Citation / 참조(출처) 표시"를 켜야** API 응답 `metadata.retriever_resources`에 검색 결과가 채워집니다.  
(이슈 [dify#8264](https://github.com/langgenius/dify/issues/8264)에서 maintainer가 물었던 "reference function switch"가 바로 이 설정이다.)

**확인·조치**

1. **Dify 스튜디오** → 해당 **Chatflow 앱** → 우측 상단 **Features** (또는 발행 설정).
2. **Citation** / **참조(출처) 표시** / **Show retrieve source** 옵션을 **켬**.
3. 저장 후 다시 **Publish** 한 뒤, 같은 curl로 `/v1/chat-messages` 호출해 `metadata.retriever_resources` 확인.

위 설정을 켜도 비어 있다면, 아래를 추가로 확인한다.

- **실제로 지식 검색을 타는 경로인지**  
  - 해당 질문이 워크플로 분기에서 **Knowledge Retrieval** 노드를 거쳐야 함.  
  - 검색 노드를 안 타면 `retriever_resources`가 비어 있는 것이 정상.
- **내장 지식베이스 vs 외부 API**  
  - **내장 Knowledge Retrieval 노드**(Dify 지식베이스)를 쓰면 `QueueRetrieverResourcesEvent`가 발행되어 위 로직으로 metadata에 들어감.  
  - **외부 API(커스텀 도구)**로만 검색하면 이벤트가 안 날아갈 수 있어, API 응답에는 계속 `[]`일 수 있음 ([dify#11422](https://github.com/langgenius/dify/issues/11422)).

**retrieved를 꼭 쌓고 싶을 때**

- Dify에서 채워 주지 않으면 gateway만으로는 `retrieved`를 채울 수 없다.
- 선택지: (1) 위 **Citation/참조 표시** 켜기 + 내장 Knowledge Retrieval 사용, (2) Dify **Chat** 앱 + 지식베이스 사용, (3) 별도 RAG 백엔드 호출 결과를 gateway에서 MinIO에 넣는 방식(별도 구현).

### API만으로 RAG 사용 여부를 확실히 알려면 (체크리스트)

`/v1/chat-messages` 응답의 `metadata.retriever_resources`가 채워지도록 하려면 아래를 **순서대로** 적용한다.

| 순서 | 할 일 | 설명 |
|------|--------|------|
| 1 | **Citation(참조 표시) 켜기** | Dify 스튜디오 → 해당 앱 → **Features** → **Citation** / **참조(출처) 표시** / **Show retrieve source** 를 **ON**. 저장 후 **Publish** 다시 실행. |
| 2 | **내장 Knowledge Retrieval 노드 사용** | 워크플로에서 지식 검색을 **Dify 내장 "Knowledge Retrieval" 노드**(지식베이스 직접 연결)로 구성. **외부 API(커스텀 도구)**로만 검색하면 `QueueRetrieverResourcesEvent`가 안 날아가서 API에 `[]`로 나올 수 있음. |
| 3 | **질문이 검색 경로를 타는지 확인** | 해당 질문이 분기에서 **Knowledge Retrieval 노드를 실제로 거치는지** 워크플로에서 확인. 검색 노드를 안 타면 비어 있는 것이 정상. |
| 4 | **퍼블릭 API로 재호출** | `./scripts/curl-dify-direct.sh "코인튜터란?" cointutor` 등으로 **발행된 앱**의 `/v1/chat-messages`(blocking) 호출 후 `metadata.retriever_resources` 확인. |

**1~3까지 했는데도 API에서 여전히 `[]`인 경우**

- **Dify 버전**: advanced-chat에서 metadata가 비었던 버그가 0.8.0에서 보고되었고, 이후 PR로 usage는 수정됐으나 retriever_resources는 버전/경로에 따라 다를 수 있음. **Dify를 최신 안정 버전으로 올린 뒤** 다시 테스트.
- **이슈 검색**: [dify issues: retriever_resources advanced-chat](https://github.com/langgenius/dify/issues?q=retriever_resources+advanced-chat) 에서 동일 사례·패치 여부 확인.
- **대안**: API로는 구분이 안 되므로, (1) **스트리밍** 응답에서 `message_end` 등에 retriever_resources가 오는지 확인하거나, (2) gateway에서 **RAG 백엔드를 별도 호출**해 `retrieved`를 채우는 방식으로 우회.

### 앱 구분·잘못된 답변 사례와 다음 단계

**상황**: "코인튜터란?" 질문에 "문제 파일 업로드, 시험 생성, 스터디 그룹…" 같은 **DrillQuiz** 기능 설명이 나옴.

| 원인 | 의미 |
|------|------|
| **잘못된 앱으로 호출** | Dify 직접 호출 시 DrillQuiz API 키를 쓰면 DrillQuiz 앱이 응답함. 코인튜터 질문은 **코인튜터 앱(코인튜터 API 키)** 로 호출해야 함. |
| **retriever_resources: []** | 해당 회차에서 RAG로 문서를 쓰지 않았음. 지식 검색 경로를 타지 않거나, 퍼블릭 API에서 Dify가 metadata에 채우지 않는 경우. |

**로컬 테스트 시 앱 구분**

- `chat-gateway/scripts/curl-dify-direct.sh` 에서 **두 번째 인자**로 앱 지정.
  - 코인튜터 앱: `./scripts/curl-dify-direct.sh "코인튜터란?" cointutor`
  - DrillQuiz 앱(기본): `./scripts/curl-dify-direct.sh "코인튜터란?"` 또는 `... drillquiz`

**품질 개선 체크리스트**

1. **앱/시스템 구분**: 채팅 클라이언트·gateway에서 `system_id`(cointutor vs drillquiz)를 올바르게 보내고, 해당 앱의 Dify API 키로만 호출하는지 확인.
2. **코인튜터 전용 RAG**: Dify 코인튜터 앱 워크플로에 코인튜터 지식베이스/문서가 연결되어 있고, "코인튜터란?" 같은 질문이 Knowledge Retrieval 노드를 타는지 확인.
3. **프롬프트 제약**: 필요 시 "현재는 코인튜터 앱이므로 코인튜터 서비스만 설명하라"는 식의 제약을 LLM 노드에 추가.
4. **재검증**: 같은 질문으로 코인튜터 앱을 호출했을 때 `retriever_resources`가 채워지는지(또는 Citation 설정 후 채워지는지), 답변이 코인튜터 내용으로 나오는지 확인.

이런 식의 잘못된 답변 사례를 MinIO 등에 로그로 쌓아 두면, **어떤 질문·어떤 앱에서 잘못 답했는지** 데이터로 확인하고 개선 타깃으로 쓸 수 있습니다.

---

## 4. 활용 방법 요약

1. **기대 질문 세트 정의**  
   `expected_questions.yaml`에 질문·ground_truth·keywords 작성 후 `EXPECTED_QUESTIONS_PATH`로 로드.

2. **일관성 검사**  
   같은 `question_id`(같은 질문)에 여러 답변 레코드가 쌓이면, 답변 간 일관성 점수·플래그로 분석 가능.

3. **LLM-as-judge / 키워드 평가**  
   `ground_truth` 또는 `keywords`로 자동 점수화 파이프라인 구성.

4. **샘플 수 늘리기**  
   실서비스 로그 + `rag/scripts/batch_eval_rag.py`로 기대 질문 반복 호출해 로그 추가 수집.

---

## 5. K8s 배포 시 참고

- expected_questions: YAML을 ConfigMap으로 올린 뒤, volumeMount로 `EXPECTED_QUESTIONS_PATH`에 해당하는 경로에 마운트.
