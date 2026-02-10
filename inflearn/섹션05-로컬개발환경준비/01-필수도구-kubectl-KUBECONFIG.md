# 01. 필수 도구: kubectl, KUBECONFIG

## kubectl

- **Kubernetes 클러스터**와 통신하는 CLI
- 설치: 공식 문서 또는 패키지 매니저(kubectl 설치 가이드 참고)
- 확인: `kubectl version --client`

## KUBECONFIG

- **어떤 클러스터에 접속할지**, 인증 정보가 들어 있는 설정 파일
- 기본 경로: `~/.kube/config`
- 다른 설정 파일을 쓰려면: `export KUBECONFIG=/path/to/your/kubeconfig`
- bootstrap.sh·install.sh 등은 이 환경변수를 따릅니다 (없으면 기본값 사용).

## 최소 확인

```bash
kubectl get nodes
kubectl get ns
```

- `get nodes`가 정상 나오면 클러스터 접근 가능
- 실습 전 반드시 한 번 확인할 것
