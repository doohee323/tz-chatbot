# 08-1. 실습: 문서 업로드 및 수동 Ingestion

## 목표

- MinIO에 RAG용 문서를 업로드하고, 해당 토픽의 Ingestion Job을 수동으로 실행해 Qdrant에 반영합니다.

## 단계

### 1. 문서 준비

- 테스트용 .md 또는 .txt 파일 준비 (내용은 토픽에 맞게)
- CoinTutor면 `raw/cointutor/`, DrillQuiz면 `raw/drillquiz/` 아래에 들어가야 함

### 2. MinIO에 업로드

- **방법 A**: MinIO 콘솔에서 `rag-docs` 버킷 → `raw/cointutor/`(또는 drillquiz) 폴더 생성 후 파일 업로드
- **방법 B**: chat-admin 관리 화면에서 해당 system_id(토픽)로 “파일 업로드” (업로드 시 raw/{system_id}/ 로 저장되도록 구현된 경우)
- **방법 C**: mc(multipart) 등 S3 호환 CLI로 put

### 3. 수동 Ingestion Job 실행

```bash
# 예: CoinTutor
kubectl create job -n rag ingest-cointutor-$(date +%s) --from=cronjob/rag-ingestion-cronjob-cointutor
kubectl logs -n rag job/ingest-cointutor-<timestamp> -f
```

- Job이 Completed가 되고 로그에 에러가 없으면 성공

### 4. 검증

- RAG Backend(해당 토픽)에 검색 요청을 보내 업로드한 문서 내용이 검색되는지 확인
- 또는 Dify에서 해당 앱으로 채팅해 RAG 응답이 나오는지 확인 (섹션 09와 연계)

이후 CronJob 스케줄에 따라 자동으로 재색인되거나, 관리 화면에서 필요 시 재색인을 트리거할 수 있습니다.
