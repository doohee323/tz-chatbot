# 02. Ingress NGINX와 MinIO

## Ingress NGINX

- **역할**: 클러스터 **진입점**. 도메인·경로별로 서비스로 라우팅, **TLS 종료**(HTTPS)
- **설치**: `ingress-nginx/install.sh` (Helm). cert-manager로 Let's Encrypt 등 SSL 인증서 자동 발급·갱신 가능
- **네임스페이스**: 주로 default. Ingress 리소스는 각 서비스와 같은 NS 또는 default에 두고, Ingress Controller가 모두 처리

## MinIO

- **역할**: **S3 호환 객체 저장소**. tz-chatbot에서는 **RAG 문서** 저장용
- **버킷**: `rag-docs`. 그 안에 `raw/cointutor/`, `raw/drillquiz/` 등 **토픽별 경로**로 파일 업로드
- **설치**: `minio/install.sh` (Helm), **devops** 네임스페이스
- **사용처**
  - RAG Ingestion Job/CronJob: MinIO에서 파일 읽기 → 청킹·임베딩 → Qdrant
  - chat-admin: 관리자가 RAG 문서 업로드 시 MinIO 해당 경로에 저장

버킷 생성은 MinIO 콘솔 또는 `dify/minio-bucket-job.yaml` 등으로 할 수 있습니다 (저장소별 문서 참고).
