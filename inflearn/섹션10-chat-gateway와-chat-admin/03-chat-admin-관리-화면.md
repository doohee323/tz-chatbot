# 03. chat-admin 관리 화면

## 역할

- **시스템(앱) CRUD**: 새 챗봇 앱(system_id) 등록, Dify URL·API Key·챗봇 토큰 설정, 수정·삭제
- **채팅 조회**: system_id·user_id 기준으로 대화 목록·메시지 조회 (Dify 또는 DB 캐시)
- **RAG 문서 업로드**: 토픽(system_id)별로 MinIO `raw/{system_id}/` 에 파일 업로드
- **재색인 트리거**: 업로드 후 해당 토픽의 RAG Ingestion Job을 수동 실행
- **테스트 토큰 발급**: 관리자가 해당 시스템용 JWT를 발급해 채팅 페이지 바로 열기

## 기술 스택

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Vue (채팅 페이지·관리 UI)
- **DB**: 로컬은 SQLite, K8s는 PostgreSQL(chat_admin)
- **인증**: 관리자 회원가입/로그인, JWT로 채팅 페이지 접근

## 접근

- K8s 배포 시 Ingress로 `https://<admin-host>/` 등 제공
- 로컬: `./admin.sh` 후 `http://localhost:8000/` (포트는 설정에 따름)
