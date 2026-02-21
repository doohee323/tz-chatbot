# 슬라이드 04: 운영 시스템 확장 (Scaling)

## 슬라이드 내용 (한 장)

**수동 스케일링**
• Deployment replicas 조정: `kubectl patch deployment <name> -n <ns> -p '{"spec":{"replicas":3}}'`
• 또는 `kubectl scale deployment <name> --replicas=3 -n <ns>`
• 매니페스트에서 `replicas: 3`으로 변경 후 `kubectl apply`

**자동 스케일링 (HPA: Horizontal Pod Autoscaler)**
• CPU, 메모리 기반 자동 스케일링
• 전제: metrics-server 설치 필요 (K8s 1.19+)
• HPA 예: `minReplicas: 2, maxReplicas: 10, targetCPUUtilization: 70%`

**대상 컴포넌트**
• **RAG Backend**: CPU 집약적 (벡터 검색) — HPA 권장
• **Dify**: 메모리 집약적 (LLM 추론) — HPA + 리소스 제한
• **chat-gateway / chat-admin**: I/O 집약적 — 필요시 HPA

**모니터링**
• `kubectl top nodes / pods` — 리소스 사용량 확인
• metrics-server 설치: `kubectl apply -f https://...metrics-server.yaml`

---

## 발표 노트

운영하면서 부하가 증가하면 시스템을 확장해야 합니다. 스케일링은 두 가지 방법이 있습니다. 하나는 수동 스케일링으로, kubectl patch 명령어로 Deployment의 replicas 수를 조정하거나, 매니페스트 파일의 replicas를 바꿔서 kubectl apply하는 겁니다. 간단하지만 사람이 직접 해야 합니다.

더 좋은 방법은 자동 스케일링, HPA(Horizontal Pod Autoscaler)입니다. CPU나 메모리 사용량에 따라 Pod 수를 자동으로 늘리거나 줄입니다. 다만 metrics-server가 K8s 클러스터에 설치되어 있어야 합니다. HPA는 최소 replicas와 최대 replicas를 정해두고, 예를 들어 CPU 사용률이 70%를 넘으면 Pod를 늘리고, 30% 이하가 되면 줄이는 식으로 설정합니다.

각 컴포넌트의 특성에 따라 다릅니다. RAG Backend는 벡터 검색을 하느라 CPU를 많이 쓰니까 HPA가 유용합니다. Dify는 LLM 추론 때문에 메모리를 많이 쓰고 예측 불가능한 부하가 생기므로, HPA와 함께 리소스 제한(requests, limits)을 잘 설정해야 합니다. chat-gateway와 chat-admin은 I/O가 주된 작업이라 필요에 따라 HPA를 설정하면 됩니다.

모니터링은 `kubectl top`으로 현재 리소스 사용량을 확인할 수 있습니다. nodes로 하면 각 노드의 사용량, pods로 하면 각 Pod의 사용량을 봅니다. metrics-server가 없으면 top 명령이 작동하지 않으니까, 설치해야 합니다. 쿠버네티스 공식 문서에서 metrics-server.yaml을 받아서 설치하면 됩니다.
