# 06. OpenTelemetry와 분산 추적 (OTLP)

## OpenTelemetry란

**OpenTelemetry(OTLP)**는 마이크로서비스 환경에서 **분산 추적(Distributed Tracing)**, **메트릭**, **로그**를 수집·전송·분석하는 표준 프레임워크입니다.

- **chat-admin**, **chat-gateway**, **chat-inference** 등 여러 Pod에서 발생하는 요청을 **하나의 트레이스로 연결**해서 성능 병목이나 오류를 빠르게 파악할 수 있습니다.
- Jaeger, Zipkin, DataDog 등 다양한 백엔드와 호환됩니다.

## tz-chatbot에서의 OTLP 설정

### 환경변수

다음 환경변수로 OTLP Exporter를 활성화합니다:

```bash
# OTLP Exporter 활성화 (OTEL_EXPORTER_OTLP_ENDPOINT로 수신기 주소 지정)
OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317"  # 또는 "http://localhost:4317"
OTEL_EXPORTER_OTLP_PROTOCOL="grpc"  # gRPC 프로토콜 (기본값)

# 서비스명 설정 (Jaeger UI에서 보이는 서비스 이름)
OTEL_SERVICE_NAME="chat-gateway"  # 또는 "chat-admin", "chat-inference"

# (선택) 샘플링 비율: 1.0 = 100%, 0.1 = 10% (프로덕션에서는 낮춤)
OTEL_TRACES_SAMPLER="parentbased_traceidratio"
OTEL_TRACES_SAMPLER_ARG="0.1"  # 10% 샘플링

# (선택) 제외할 URL 패턴 (헬스체크·준비성 프로브 등)
OTEL_PYTHON_EXCLUDED_URLS="/health,/ready,/live"
```

### K8s ConfigMap 예시

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chat-gateway-otel-config
  namespace: devops
data:
  OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector.monitoring:4317"
  OTEL_SERVICE_NAME: "chat-gateway"
  OTEL_TRACES_SAMPLER: "parentbased_traceidratio"
  OTEL_TRACES_SAMPLER_ARG: "0.1"
  OTEL_PYTHON_EXCLUDED_URLS: "/health,/ready,/live"
```

### Deployment에서 적용

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-gateway
  namespace: devops
spec:
  template:
    spec:
      containers:
      - name: chat-gateway
        image: your-registry/chat-gateway:latest
        envFrom:
        - configMapRef:
            name: chat-gateway-otel-config  # ← ConfigMap 참조
        env:
        - name: OTEL_EXPORTER_OTLP_HEADERS
          valueFrom:
            secretKeyRef:
              name: otel-headers-secret
              key: authorization  # 인증 헤더 필요 시
```

## OTLP 수신기 설치

Kubernetes 클러스터에 **OpenTelemetry Collector** 배포:

```bash
# Helm으로 OTLP Collector + Jaeger 백엔드 설치
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

helm install otel-collector open-telemetry/opentelemetry-collector \
  -n monitoring \
  --values otel-collector-values.yaml
```

### otel-collector-values.yaml (간단한 예)

```yaml
mode: daemonset

config:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

  exporters:
    jaeger:
      endpoint: jaeger-collector.monitoring:14250
      tls:
        insecure: true
    logging:
      loglevel: debug

  service:
    pipelines:
      traces:
        receivers: [otlp]
        exporters: [jaeger, logging]
      metrics:
        receivers: [otlp]
        exporters: [logging]
```

## 분산 추적 조회

### 1. Jaeger UI 접속

```bash
# Jaeger UI 포워딩 (K8s 환경)
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686

# 브라우저에서 열기
http://localhost:16686
```

### 2. 요청 트레이스 확인

- **Service 선택**: chat-gateway, chat-admin 등 서비스명 선택
- **Operation 선택**: `/v1/chat`, `/v1/conversations` 등 요청 경로
- **View traces** 클릭 → 트레이스 목록 표시
- **한 트레이스 선택**: 체인 따라 각 마이크로서비스로의 호출 시간·오류 시각화

### 3. 성능 병목 파악

```
클라이언트 요청 (t=0ms)
  └─ chat-gateway: 150ms
      ├─ Dify 호출: 120ms
      │   └─ LLM 응답 대기: 100ms
      └─ DB 저장: 30ms
```

이렇게 각 단계 소요 시간이 보이므로, "Dify LLM 호출이 느리다", "DB 쿼리가 오래 걸린다" 등을 빠르게 파악할 수 있습니다.

## 로그 중앙화와 함께

OTLP는 **분산 추적(요청 체인)**에 중점을 두고, **Loki/EFK 로그 수집**은 **각 Pod의 상세 로그**에 중점을 둡니다.

- **Jaeger(OTLP)**: "어느 서비스가 느린가?" "요청이 어디서 오류났나?"
- **Loki/EFK**: "그 서비스에서 정확히 뭐가 일어났나?" (상세 로그)

두 방식을 함께 쓰면 **운영 효율이 크게 향상**됩니다.

## 관련 문서

- [docs/additional-requirements.md](../../docs/additional-requirements.md) — 추가 운영 요구사항 (모니터링·스케일링)
- OpenTelemetry 공식 문서: https://opentelemetry.io/
- Jaeger 공식 문서: https://www.jaegertracing.io/
