# 02. cert-manager와 SSL

## cert-manager

- Kubernetes에서 **TLS 인증서**를 자동 발급·갱신해 주는 컨트롤러
- **ClusterIssuer** / **Issuer** 리소스로 “Let's Encrypt” 등 발급자 설정
- **Certificate** 리소스로 “이 도메인용 인증서” 요청 → cert-manager가 ACME로 발급 후 Secret에 저장
- Ingress에서 해당 Secret을 참조해 HTTPS 종료

## Ingress와 연동

- Ingress의 **spec.tls** 에 secretName을 넣고, **annotations**에 cert-manager issuer 지정
- 예: `cert-manager.io/cluster-issuer: letsencrypt-prod`
- cert-manager가 Ingress를 보고 자동으로 Certificate를 만들고, 도메인 검증(HTTP-01 또는 DNS-01) 후 Secret을 채움

## tz-chatbot

- **ingress-nginx/** 디렉터리: Ingress NGINX 설치 스크립트, cert-manager CRD·Issuer 예시 (letsencrypt-prod.yaml 등)
- 도메인·이메일 등은 실제 환경에 맞게 수정 후 적용
