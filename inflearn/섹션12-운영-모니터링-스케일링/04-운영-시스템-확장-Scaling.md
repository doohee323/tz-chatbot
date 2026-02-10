# 04. 운영 시 시스템 확장 (Scaling)

## HPA (Horizontal Pod Autoscaler)

- **CPU·메모리 사용률**에 따라 Pod 수를 자동으로 늘리거나 줄임
- **metrics-server**가 클러스터에 설치되어 있어야 HPA가 동작합니다. (`kubectl top pods` 로 확인)
- tz-chatbot에서 HPA 예시:
  - **rag/rag-hpa.yaml**: rag-backend, rag-backend-drillquiz, rag-frontend (min/max replicas, target CPU %)
  - **dify/dify-hpa.yaml**: Dify API·Worker
  - **chat-gateway/ci/k8s.yaml**, **chat-admin/ci/k8s.yaml**: chat-gateway-hpa, chat-admin-hpa

## replicas

- Deployment의 **replicas**를 늘리면 Pod가 여러 개 뜨고, Service가 로드밸런싱
- HPA를 쓰면 minReplicas~maxReplicas 범위에서 자동 조정. 사용하지 않으면 수동으로 replicas만 올릴 수 있음

## 적용 시 주의

- **minReplicas=1, maxReplicas=1** 처럼 고정해 두었으면 스케일 아웃되지 않음. 트래픽이 늘면 maxReplicas를 올리고, metrics-server·리소스 요청/제한을 점검하세요.
- **StatefulSet**(DB, Qdrant 등)은 보통 HPA보다는 replicas를 고정하거나 전용 스케일링 전략을 사용합니다.
