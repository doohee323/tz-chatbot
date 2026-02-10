# 01. Ingress 및 도메인 개요

## Ingress 역할

- **HTTP/HTTPS** 트래픽을 클러스터 안의 **Service**로 라우팅
- **호스트(도메인)·경로**별로 어떤 Service로 보낼지 규칙 정의
- tz-chatbot: Dify, RAG UI, chat-gateway, chat-admin 등 각각 **호스트** 또는 **경로**로 구분해 Ingress에 등록

## 도메인

- 실제 서비스 시 **도메인**을 Ingress 규칙에 넣음 (예: chat.example.com, admin.example.com, dify.example.com)
- DNS에서 해당 도메인을 **Ingress Controller**가 받는 IP(또는 로드밸런서)로 연결
- 저장소의 Ingress YAML은 `k8s_domain` 등 변수로 치환하는 경우가 있음 (install.sh, values 확인)

## TLS (HTTPS)

- **cert-manager**로 Let's Encrypt 등에서 인증서 자동 발급·갱신
- Ingress 리소스에 **tls** 섹션과 **annotations**로 cert-manager 사용 지정
- Ingress NGINX 설치 시 cert-manager 설치 순서·CRD는 저장소 문서 참고
