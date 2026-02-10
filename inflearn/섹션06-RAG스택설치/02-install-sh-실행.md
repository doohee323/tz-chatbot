# 02. install.sh 실행

## 실행 방법

```bash
cd tz-chatbot/rag
bash install.sh
```

- **KUBECONFIG**가 설정된 상태에서 실행 (다른 클러스터 사용 시 `KUBECONFIG=... bash install.sh`)
- install.sh는 보통 다음 순서로 적용합니다:
  - namespace `rag` 생성
  - Qdrant Helm 설치 (qdrant-values.yaml)
  - 컬렉션 생성 Job (qdrant-collection-init.yaml)
  - RAG Backend (CoinTutor/DrillQuiz) Deployment·Service
  - RAG Frontend, Ingress
  - Ingestion Job/CronJob (토픽별 YAML)
  - (저장소에 따라) ingest.py·requirements를 ConfigMap으로 업로드

## 주의

- **MinIO**가 이미 `devops` NS에 설치되어 있어야 합니다 (bootstrap 2단계).
- **Ingress NGINX**가 있으면 RAG Ingress가 동작합니다. install.sh 내부에서 `k8s_domain` 등 치환이 있을 수 있으므로 저장소의 install.sh·rag-ingress.yaml 내용을 확인하세요.
- 설치 후 **반드시** 토픽별 Secret을 생성해야 Backend가 정상 동작합니다 (다음 파일).
