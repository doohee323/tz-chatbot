# 01. bootstrap과 설치 순서

## bootstrap.sh란

- tz-chatbot **전체 K8s 환경**을 한 번에 올리기 위한 진입점 스크립트
- **전제**: K8s 클러스터 존재, `kubectl`·`KUBECONFIG` 설정됨
- 이미 설치된 컴포넌트는 건너뛰고, 없는 것만 순서대로 설치합니다.

## 설치 순서 (bootstrap.sh 기준)

| 순서 | 단계 | 네임스페이스 | 내용 |
|------|------|--------------|------|
| Phase 0 | 사전 점검 | - | `kubectl get nodes` 로 클러스터 접근 확인 |
| 1 | Ingress NGINX | default | cert-manager, TLS. 모든 HTTP/HTTPS 진입점 |
| 2 | MinIO | devops | 객체 저장소, `rag-docs` 버킷 (RAG 문서) |
| 3 | RAG 스택 | rag | Qdrant, RAG Backend(CoinTutor/DrillQuiz), Ingestion Job/CronJob |
| 4 | Dify | dify | Helm 차트, 챗봇·RAG 도구 연동 |

**chat-admin, chat-gateway**는 bootstrap에 포함되지 않습니다. CI(k8s.sh) 또는 Jenkins로 별도 배포합니다.

## 실행 방법

```bash
export KUBECONFIG=~/.kube/your-config   # 필요 시
./bootstrap.sh
```

- `TZ_REPO_ROOT`는 스크립트가 자동으로 설정
- 각 단계에서 이미 설치된 경우 "Already installed, skipping" 메시지가 나옵니다.
