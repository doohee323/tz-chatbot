# 슬라이드 01: Ingress·도메인·라우팅

## 슬라이드 내용 (한 장)

**Ingress 역할**  
• 클러스터 외부 → 내부 Service로 HTTP/HTTPS 라우팅. 하나의 로드밸런서·IP로 여러 호스트·경로 분기  
• **Host**: admin.example.com → chat-admin, chat.example.com → chat-gateway, dify.example.com → Dify

**도메인·호스트 설정**  
• DNS A/CNAME을 Ingress Controller(예: LoadBalancer External IP 또는 NodePort)로 연결  
• Ingress 리소스: spec.rules[].host + spec.rules[].http.paths[].path → backend.service  
• 실습: /etc/hosts 또는 로컬 DNS로 admin.example.com, chat.example.com 등 임시 지정 후 브라우저 접속 확인

**TLS(HTTPS)**  
• spec.tls[].hosts + spec.tls[].secretName. secretName에 TLS 인증서가 들어 있는 Secret 이름 지정  
• 인증서 발급·갱신은 cert-manager 사용 시 다음 슬라이드 “cert-manager와 SSL” 참고

---

## 발표 노트

Ingress는 클러스터 바깥에서 들어오는 HTTP·HTTPS 트래픽을 내부 Service로 보내는 라우터 역할을 합니다. 하나의 로드밸런서나 IP로 여러 도메인과 경로를 나눌 수 있어요. 예를 들어 admin.example.com은 chat-admin으로, chat.example.com은 chat-gateway로, dify.example.com은 Dify로 보내도록 설정합니다.

도메인과 호스트 설정은 이렇게 합니다. 먼저 DNS에서 A 레코드나 CNAME을 Ingress Controller가 받는 주소, 즉 LoadBalancer의 External IP나 NodePort로 쓰는 노드 IP로 연결합니다. Ingress 리소스에서는 spec.rules에 host를 쓰고, 그 아래 http.paths에 path와 backend service를 지정합니다. 실습할 때는 도메인을 아직 안 썼다면 /etc/hosts나 로컬 DNS에 admin.example.com, chat.example.com을 Ingress IP로 넣어 두고 브라우저로 접속해 보시면 됩니다.

TLS, 즉 HTTPS를 쓰려면 spec.tls에 hosts와 secretName을 넣습니다. secretName에는 TLS 인증서가 들어 있는 Secret 이름을 적습니다. 이 인증서를 누가 발급하고 갱신하는지는 cert-manager를 쓰면 자동화할 수 있고, 그 내용은 다음 슬라이드 “cert-manager와 SSL”에서 다룹니다.
