# 슬라이드 01: bootstrap과 설치 순서

## 슬라이드 내용 (한 장)

**bootstrap.sh**  
• tz-chatbot **전체 K8s 환경** 한 번에 올리는 진입점  
• 전제: 클러스터 존재, kubectl·KUBECONFIG 설정  
• 이미 설치된 것은 건너뛰고 없는 것만 순서대로 설치

**설치 순서**

| 순서 | 단계 | NS | 내용 |
|------|------|-----|------|
| 0 | 사전 점검 | - | kubectl get nodes |
| 1 | Ingress NGINX | default | cert-manager, TLS |
| 2 | MinIO | devops | rag-docs 버킷 |
| 3 | RAG 스택 | rag | Qdrant, Backend, Ingestion |
| 4 | Dify | dify | Helm, 챗봇·RAG 도구 |

• chat-admin, chat-gateway는 **bootstrap 제외** → CI(k8s.sh) 또는 Jenkins 별도 배포  
• 실행: `export KUBECONFIG=... ; ./bootstrap.sh`  
• **제거**: `./bootstrap.sh uninstall` → rag/uninstall.sh 호출 (Dify → RAG 순 제거). MinIO·Ingress NGINX는 유지. 재설치: `./bootstrap.sh`

---

## 발표 노트

bootstrap.sh는 tz-chatbot 전체 K8s 환경을 한 번에 올리기 위한 진입점 스크립트입니다. 전제 조건은 Kubernetes 클러스터가 이미 있고, kubectl과 KUBECONFIG가 설정되어 있다는 것입니다. 스크립트는 이미 설치된 컴포넌트는 건너뛰고, 없는 것만 순서대로 설치합니다.

Phase 0에서는 사전 점검으로 kubectl get nodes를 실행해서 클러스터 접근이 되는지 확인합니다. 1단계는 Ingress NGINX를 default 네임스페이스에 설치합니다. cert-manager와 TLS 설정이 들어가고, 모든 HTTP·HTTPS 진입점이 됩니다. 2단계는 MinIO를 devops 네임스페이스에 설치하고, rag-docs 버킷을 RAG 문서 저장소로 씁니다. 3단계는 RAG 스택을 rag 네임스페이스에 올립니다. Qdrant, RAG Backend, Ingestion Job·CronJob이 여기 들어갑니다. 4단계는 Dify를 dify 네임스페이스에 Helm으로 설치하고, 챗봇과 RAG 도구 연동을 설정합니다.

chat-admin과 chat-gateway는 bootstrap에 포함되지 않습니다. 나중에 CI의 k8s.sh나 Jenkins로 별도 배포합니다. 실행 방법은 KUBECONFIG를 필요하면 설정한 뒤 루트에서 ./bootstrap.sh를 실행하면 됩니다. TZ_REPO_ROOT는 스크립트가 자동으로 잡고, 각 단계에서 이미 설치된 경우 "Already installed, skipping" 메시지가 나옵니다. 제거할 때는 ./bootstrap.sh uninstall을 실행하면 rag/uninstall.sh가 호출되어 Dify를 먼저, 그다음 RAG를 제거합니다. MinIO와 Ingress NGINX는 그대로 두고, 다시 설치하려면 ./bootstrap.sh를 실행하면 됩니다.
