# 11-1. 실습: 도메인 및 HTTPS 확인

## 목표

- Ingress에 설정한 도메인으로 접속하고, HTTPS(SSL)가 정상 동작하는지 확인합니다.

## 단계

### 1. DNS 설정

- 사용할 도메인(예: chat.example.com)의 **A 레코드**(또는 CNAME)를 Ingress Controller가 받는 **외부 IP**(또는 로드밸런서 호스트명)로 설정
- 전파 시간이 걸릴 수 있으므로 `dig` 또는 브라우저로 확인

### 2. Ingress·Certificate 확인

```bash
kubectl get ingress -A
kubectl get certificate -A
kubectl get secret -A | grep tls
```

- Certificate가 Ready이고, 해당 Secret에 tls 인증서가 채워져 있는지 확인

### 3. 브라우저 접속

- `https://<설정한-도메인>` 으로 접속
- 인증서가 유효하고, 해당 서비스(chat-gateway, chat-admin, Dify 등)가 로드되는지 확인

### 4. 문제 시

- cert-manager 로그: `kubectl logs -n cert-manager deploy/cert-manager`
- Ingress Controller 로그, Certificate 이벤트(`kubectl describe certificate ...`)로 검증 실패 원인 확인
- 방화벽·로드밸런서에서 80/443이 열려 있는지 확인
