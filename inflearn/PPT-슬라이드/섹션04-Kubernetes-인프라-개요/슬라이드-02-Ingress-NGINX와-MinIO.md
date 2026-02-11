# 슬라이드 02: Ingress NGINX와 MinIO

## 슬라이드 내용 (한 장)

**Ingress NGINX**  
• 클러스터 **진입점**: 도메인·경로별로 서비스로 라우팅, **TLS 종료**(HTTPS)  
• 설치: ingress-nginx/install.sh (Helm). cert-manager로 Let's Encrypt 등 SSL 자동 발급·갱신  
• NS: 주로 default. Ingress 리소스는 각 서비스 NS 또는 default에 두고 Controller가 처리

**MinIO**  
• **S3 호환 객체 저장소**. tz-chatbot에서는 **RAG 문서** 저장  
• 버킷: `rag-docs`. 안에 `raw/cointutor/`, `raw/drillquiz/` 등 **토픽별 경로**로 업로드  
• 설치: minio/install.sh (Helm), **devops** NS  
• 사용처: RAG Ingestion(MinIO→청킹·임베딩→Qdrant), chat-admin(관리자 RAG 파일 업로드)  
• 버킷 생성: MinIO 콘솔 또는 minio-bucket-job 등 (저장소 문서 참고)

---

## 발표 노트

Ingress NGINX는 클러스터의 진입점입니다. 외부에서 들어오는 요청을 도메인이나 경로별로 적절한 서비스로 라우팅하고, TLS 종료, 즉 HTTPS를 여기서 처리합니다. 설치할 때는 ingress-nginx 폴더의 install.sh를 실행하고, Helm으로 올립니다. cert-manager를 쓰면 Let's Encrypt 같은 곳에서 SSL 인증서를 자동 발급·갱신할 수 있습니다. Ingress Controller는 보통 default 네임스페이스에 두고, 각 서비스용 Ingress 리소스는 해당 서비스와 같은 네임스페이스나 default에 두면 Controller가 다 처리합니다.

MinIO는 S3 호환 객체 저장소입니다. tz-chatbot에서는 RAG 문서 저장용으로 씁니다. 버킷 이름은 rag-docs이고, 그 안에 raw/cointutor, raw/drillquiz처럼 토픽별 경로를 두고 파일을 업로드합니다. 설치할 때는 minio 폴더의 install.sh를 실행하고, Helm으로 devops 네임스페이스에 올립니다. 사용처는 두 가지입니다. RAG Ingestion Job·CronJob이 MinIO에서 파일을 읽어서 청킹·임베딩 후 Qdrant에 넣고, chat-admin에서는 관리자가 RAG 문서를 업로드할 때 MinIO의 해당 토픽 경로에 저장합니다. 버킷 생성은 MinIO 웹 콘솔에서 하거나, 저장소에 minio-bucket-job 같은 YAML이 있으면 그걸로 할 수 있습니다. 저장소별 문서를 참고하시면 됩니다.
