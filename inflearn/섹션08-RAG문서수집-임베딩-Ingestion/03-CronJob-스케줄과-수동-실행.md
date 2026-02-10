# 03. CronJob 스케줄과 수동 실행

## CronJob 스케줄

- **CoinTutor**: 예시 — 매일 02:00 (저장소 YAML의 schedule 필드 확인)
- **DrillQuiz**: 예시 — 매일 02:30
- 스케줄에 따라 MinIO 해당 prefix를 주기적으로 스캔하고, 변경분만 반영(INCREMENTAL)하거나 전체 재색인할 수 있음

## 수동 1회 실행

- CronJob을 “한 번만” 실행하려면 Job을 만들어 주면 됩니다.

```bash
# CoinTutor
kubectl create job -n rag ingest-cointutor-1 --from=cronjob/rag-ingestion-cronjob-cointutor

# DrillQuiz
kubectl create job -n rag ingest-drillquiz-1 --from=cronjob/rag-ingestion-cronjob-drillquiz
```

- Job 이름은 고유해야 하므로, 다시 실행할 때는 이름을 바꿔서 생성 (예: ingest-cointutor-2)

## 전체 재색인 (full sync)

- **INCREMENTAL=false**로 하면 컬렉션을 비우고 처음부터 다시 넣는 방식
- 저장소에 **rag-ingestion-cronjob-*-full** 같은 별도 CronJob YAML이 있을 수 있음. 해당 CronJob에서 Job을 생성하면 full sync가 됩니다.
- chat-admin 관리 화면의 “재색인” 트리거도 내부적으로 이런 Job을 생성할 수 있습니다 (저장소 구현 참고).
