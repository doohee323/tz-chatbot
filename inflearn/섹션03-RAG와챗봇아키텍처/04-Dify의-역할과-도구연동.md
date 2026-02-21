# 04. Dify의 역할과 도구 연동

## Dify만으로 RAG를 하지 않고, 왜 별도 RAG 앱을 두는가

### Dify 내장 RAG의 한계 (실무에서 LangChain 전환이 많은 이유)

- **Dify만으로도 RAG는 가능합니다.** 지식 베이스(문서 업로드 → 청킹·임베딩 → 검색)가 내장되어 있어, **초기 구축·프로토타입**에는 유리합니다. 다만 규모가 커지거나 요구사항이 늘어나면 한계가 드러나고, **실제로 많은 기업이 Dify로 초기 구축 후 자체 LangChain 기반 RAG로 전환**하는 패턴이 있습니다.
- **Dify 내장 RAG의 대표적 한계**:
  - **검색 품질·유연성**: 복잡한 질의·문장형 질의에서 관련 청크를 제대로 못 찾거나, 여러 청크에 흩어진 정보를 종합하기 어렵다. 청크 크기·검색 전략·하이브리드 검색 등 **세밀한 튜닝이 제한적**이다.
  - **파이프라인·데이터 소스 제어**: 청킹·임베딩 모델·벡터 DB를 Dify 설정에 의존한다. **MinIO/S3를 단일 소스로 두고 CronJob으로 배치 재색인**하거나, 외부 벡터 DB(Qdrant 등)를 그대로 쓰는 구성이 Dify UI/API만으로는 맞지 않다.
  - **복수 앱·토픽 분리**: 앱마다 지식 베이스를 따로 두면 관리가 흩어지고, **공통 문서 저장소 + 토픽별 컬렉션·Backend 분리** 같은 운영 모델과 잘 맞지 않는다.
  - **상용 수준 요구**: 상용 서비스 수준의 검색 정확도·확장성·커스터마이징을 원하면 **외부 검색 API 또는 자체 RAG 파이프라인(LangChain 등) 구축이 불가피**하다는 평가가 많다.

따라서 **“Dify로 RAG를 이해한 뒤, Dify 없이도 동일한 RAG 파이프라인을 구성할 수 있게 한다”**는 것이 이 강의의 관점에 맞습니다.

### 이 강의에서의 두 가지 관점: Dify로 이해하기 vs LangChain으로 직접 구성하기

| 구분 | Dify 중심으로 RAG 이해하기 | Dify 없이 LangChain으로 RAG 구성하기 (tz-chatbot 방식) |
|------|---------------------------|--------------------------------------------------------|
| **목적** | RAG가 “검색 → LLM 컨텍스트 → 생성”으로 이어지는 **흐름을 직관적으로 이해** | **실제 파이프라인**(Loader → Splitter → Embedding → Vector DB → 검색 API)을 코드·인프라로 이해하고 **자체 운영 가능**하게 함 |
| **역할** | Dify가 **오케스트레이션**(대화·도구 호출)·내장 지식 베이스 또는 **도구 URL**로 RAG 호출 | **MinIO → Ingestion(LangChain) → Qdrant → RAG Backend**를 직접 구성. Dify는 “호출자”(도구 URL)로만 쓰거나, 나중에 **Dify를 빼고** gateway가 RAG Backend·LLM을 직접 호출하도록 바꿀 수 있음 |
| **학습 효과** | UI·워크플로우로 RAG 개념을 빠르게 체감 | 청킹·임베딩·벡터 검색·배치 Ingestion을 **직접 제어**할 수 있어, Dify 한계를 넘어서거나 Dify 없이 서비스를 이전할 때 대비 가능 |

- tz-chatbot에서는 **Dify + 외부 RAG Backend** 구성을 쓰므로, “Dify 내장 지식 베이스”에 갇히지 않고 **RAG 파이프라인은 LangChain·Qdrant로 완전히 우리가 제어**합니다. 나중에 Dify 대신 다른 오케스트레이터나 자체 채팅 서버를 붙여도 **동일한 RAG Backend를 그대로 재사용**할 수 있습니다.
- 정리: **Dify로 RAG 흐름을 이해하고**, **LangChain 기반 별도 RAG 앱(Backend + Ingestion)으로 “Dify 없이도 돌릴 수 있는” 구성을 함께 익히는 것**이, RAG를 제대로 이해하고 실무에 적용하는 데 도움이 됩니다.

## Dify란

- **LLM 오케스트레이션** 플랫폼: 대화 흐름, 프롬프트, **도구(Tool)** 호출을 조합해 챗봇·에이전트를 만듦
- 웹 UI로 앱(워크플로우) 생성·배포, API Key 발급
- tz-chatbot에서는 **K8s에 Helm으로** 설치, `dify` 네임스페이스

## Dify의 역할

- **챗봇 앱**: 사용자 메시지 수신 → LLM이 답변 생성 (필요 시 도구 호출)
- **RAG 도구 연동**: “지식 검색” 같은 **도구**의 URL을 **RAG Backend** 주소로 설정
  - 예: `http://rag-backend.rag.svc.cluster.local:8000/query` (CoinTutor), DrillQuiz용 Backend URL 별도
- 사용자 ID는 chat-gateway에서 `{system_id}_{user_id}` 형태로 Dify에 전달해, 앱별·사용자별로 구분

## 도구(Tool) URL

- Dify 워크플로우에서 “도구” 노드에 **HTTP URL**을 넣으면, Dify가 그 URL로 요청을 보냄
- RAG Backend는 `/query` 등에서 질의를 받아 Qdrant 검색 후 결과를 반환
- 따라서 **RAG Backend Service 주소**(K8s 내부: `http://rag-backend.rag.svc...`)를 Dify 도구 URL로 설정해야 함 (섹션 09에서 실습).
