#!/usr/bin/env bash
# bash /vagrant/tz-local/resource/n8n/install.sh
cd /vagrant/tz-local/resource/n8n

set -e
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

NS=n8n

kubectl create namespace ${NS} --dry-run=client -o yaml | kubectl apply -f -

# n8n Community Helm chart (Ingress 포함 values.yaml_bak 사용)
helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo update

helm uninstall n8n -n ${NS} 2>/dev/null || true

helm upgrade --install n8n community-charts/n8n \
  --namespace ${NS} \
  -f values.yaml_bak

echo "n8n 설치 완료. 접속 URL은 values.yaml_bak의 ingress.hosts 참고"
exit 0
