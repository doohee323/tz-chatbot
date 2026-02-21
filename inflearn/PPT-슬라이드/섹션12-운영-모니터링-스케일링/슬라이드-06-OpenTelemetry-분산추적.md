# 슬라이드 06: OpenTelemetry 분산 추적 (OTLP)

## 슬라이드 내용 (한 장)

**OpenTelemetry란**
• 마이크로서비스 환경에서 **분산 추적(Distributed Tracing)** 수집·전송·분석
• 여러 Pod의 요청을 **하나의 트레이스로 연결** — 성능 병목·오류 빠르게 파악
• 표준 프레임워크: Jaeger, Zipkin, DataDog 등 다양한 백엔드 지원

**OTLP Exporter 설정 (K8s)**
• 환경변수:
  - `OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317"`
  - `OTEL_SERVICE_NAME="chat-gateway"` (또는 chat-admin, chat-inference)
  - `OTEL_TRACES_SAMPLER="parentbased_traceidratio"`, `OTEL_TRACES_SAMPLER_ARG="0.1"` (10% 샘플링)
  - `OTEL_PYTHON_EXCLUDED_URLS="/health,/ready,/live"` (제외 패턴)

**조회 (Jaeger UI)**
• `kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring`
• 브라우저: http://localhost:16686
• Service 선택 → Operation 선택 → 트레이스 체인·소요 시간 시각화

**로그 중앙화와 함께**
• Jaeger: "어느 서비스가 느린가?" (분산 추적)
• Loki/EFK: "정확히 뭐가 일어났나?" (상세 로그)

---

## 발표 노트

OpenTelemetry(OTLP)는 마이크로서비스 환경에서 요청이 여러 서비스를 거쳐 가면서 어디에서 시간이 오래 걸리는지, 어디서 오류가 나는지를 파악하기 위한 표준 프레임워크입니다. 분산 추적이라고 부르는데, 클라이언트에서 시작한 요청이 chat-gateway를 거쳐 Dify로 가고, Dify가 RAG Backend를 호출하는 모든 과정을 하나의 트레이스로 연결해서 볼 수 있습니다. Jaeger, Zipkin, DataDog 같은 여러 백엔드와 호환됩니다.

OTLP Exporter를 활성화하려면 환경변수를 설정합니다. OTEL_EXPORTER_OTLP_ENDPOINT는 OTLP를 수신하는 collector의 주소입니다. OTEL_SERVICE_NAME은 Jaeger UI에서 보이는 서비스 이름이 되고, chat-gateway면 chat-gateway, chat-admin이면 chat-admin으로 설정합니다. 샘플링을 설정하면 모든 요청을 추적하지 않고 일정 비율만 추적해서 성능 오버헤드를 줄입니다. 10% 샘플링이면 100개 요청 중 10개만 추적합니다. OTEL_PYTHON_EXCLUDED_URLS로 헬스체크나 준비성 프로브 같은 건 추적에서 제외할 수 있습니다.

조회는 Jaeger UI에서 합니다. kubectl port-forward로 16686 포트를 로컬로 포워드한 뒤, 브라우저에서 localhost:16686을 열면 Jaeger 대시보드가 보입니다. 서비스를 선택(chat-gateway 등)하고, 어떤 operation을 볼지 선택(/v1/chat, /v1/conversations 등)한 뒤 View traces를 누르면 해당 요청들의 트레이스 목록이 나옵니다. 한 트레이스를 클릭하면 요청이 어디를 거쳐 갔는지, 각 단계에서 몇 ms가 걸렸는지 시각화되어 보입니다.

로그 중앙화(Loki, EFK)와는 역할이 다릅니다. Jaeger 같은 분산 추적은 "어느 서비스가 느린가, 어디서 타임아웃되는가"처럼 전체 요청 흐름과 성능을 봅니다. Loki나 EFK 같은 로그 수집은 "그 서비스에서 정확히 뭐가 일어났는가, 어떤 오류 메시지가 나왔는가" 같은 상세 내용을 봅니다. 둘을 함께 쓰면 운영이 훨씬 효율적입니다.
