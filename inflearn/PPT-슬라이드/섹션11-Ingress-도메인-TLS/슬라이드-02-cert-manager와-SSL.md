# 슬라이드 02: cert-manager와 SSL

## 슬라이드 내용 (한 장)

**cert-manager**  
• Kubernetes에서 **TLS 인증서**를 자동 발급·갱신하는 컨트롤러  
• **ClusterIssuer / Issuer**: Let's Encrypt 등 발급자(ACME) 설정  
• **Certificate**: “이 도메인용 인증서” 요청 → cert-manager가 ACME로 발급 후 Secret에 저장  
• Ingress에서 해당 Secret을 참조해 HTTPS 종료

**Ingress와 연동**  
• Ingress **spec.tls**: secretName에 인증서 Secret 이름  
• **annotations**: `cert-manager.io/cluster-issuer: letsencrypt-prod` → cert-manager가 Ingress를 보고 Certificate 자동 생성  
• 도메인 검증: HTTP-01 또는 DNS-01. 검증 통과 후 Secret 채움 → Ingress가 TLS 트래픽 처리

**tz-chatbot**  
• **ingress-nginx/** 디렉터리: Ingress NGINX 설치 스크립트, cert-manager CRD·Issuer 예시(letsencrypt-prod.yaml 등)  
• 도메인·이메일은 실제 환경에 맞게 수정 후 적용. 실습 11-1에서 도메인·HTTPS 확인

---

## 발표 노트

cert-manager는 Kubernetes 안에서 TLS 인증서를 자동으로 발급하고 갱신해 주는 컨트롤러입니다. ClusterIssuer나 Issuer 리소스로 Let's Encrypt 같은 ACME 발급자를 설정하고, Certificate 리소스로 “이 도메인용 인증서를 달라”고 요청하면 cert-manager가 ACME 프로토콜로 발급해서 Secret에 저장합니다. Ingress는 그 Secret을 참조해서 HTTPS를 종료합니다.

Ingress와 연동할 때는 spec.tls에 secretName을 넣고, annotations에 cert-manager.io/cluster-issuer를 letsencrypt-prod 같은 Issuer 이름으로 지정합니다. 그러면 cert-manager가 이 Ingress를 보고 자동으로 Certificate 리소스를 만들고, 도메인 소유 검증을 HTTP-01이나 DNS-01로 진행합니다. 검증이 통과하면 Secret이 채워지고, Ingress가 그걸 써서 TLS 트래픽을 처리합니다.

tz-chatbot 저장소에서는 ingress-nginx 디렉터리에 Ingress NGINX 설치 스크립트와 cert-manager CRD, Issuer 예시인 letsencrypt-prod.yaml 등이 있습니다. 사용하실 때는 도메인과 이메일을 실제 환경에 맞게 바꾼 뒤 적용하시면 됩니다. 실습 11-1에서는 설정한 도메인과 HTTPS 동작을 확인하는 절차가 있습니다.
