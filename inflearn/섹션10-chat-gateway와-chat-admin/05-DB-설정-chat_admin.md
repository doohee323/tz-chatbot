# 05. DB 설정: chat_admin

## DB 생성

- chat-gateway와 chat-admin이 사용하는 **PostgreSQL DB 이름**: `chat_admin`
- **bootstrap.sh에는 DB 생성이 포함되지 않습니다.** 수동으로 생성해야 합니다.

## 생성 예시 (README 기준)

```bash
DB_PASS=$(kubectl -n devops get secret chat-admin-secret-main -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d)
kubectl exec -n devops devops-postgres-postgresql-0 -- env PGPASSWORD="$DB_PASS" psql -U postgres -c "CREATE DATABASE chat_admin;"
```

- **PostgreSQL**이 이미 devops NS 등에 설치되어 있어야 함
- Secret 이름은 브랜치에 따라 `chat-admin-secret-main`, `chat-admin-secret-qa`, `chat-admin-secret-dev` 등 (README Branches and namespaces 표 참고)
- 같은 비밀번호를 앱이 사용하므로, Secret의 POSTGRES_PASSWORD와 DB 생성 시 사용한 계정이 맞아야 합니다.

## 앱 설정

- **chat-admin / chat-gateway** 배포 시: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB=chat_admin 등 환경변수 또는 Secret으로 전달
