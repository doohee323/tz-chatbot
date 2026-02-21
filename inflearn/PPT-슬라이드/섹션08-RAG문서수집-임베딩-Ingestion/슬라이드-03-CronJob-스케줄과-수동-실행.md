# 슬라이드 03: CronJob 스케줄과 수동 실행

## 슬라이드 내용 (한 장)

**CronJob 주기 실행**
• CoinTutor: 매일 02:00 (저장소 YAML schedule 필드 확인)
• DrillQuiz: 매일 02:30
• MinIO prefix 정기 스캔, 변경분 반영(INCREMENTAL) 또는 전체 재색인

**수동 1회 실행**
```bash
# CoinTutor
kubectl create job -n rag ingest-cointutor-1 \
  --from=cronjob/rag-ingestion-cronjob-cointutor

# DrillQuiz
kubectl create job -n rag ingest-drillquiz-1 \
  --from=cronjob/rag-ingestion-cronjob-drillquiz
```
• Job 이름은 고유해야 함 (다시 실행 시 -2, -3 등으로 변경)

**전체 재색인 (Full Sync)**
• INCREMENTAL=false 로 설정 → 컬렉션 비우고 처음부터
• rag-ingestion-cronjob-*-full 별도 CronJob YAML 사용 가능
• chat-admin 관리 화면 "재색인" 버튼으로도 Job 생성 가능

---

## 발표 노트

RAG Ingestion은 정기적으로 실행되거나 필요할 때 수동으로 실행할 수 있습니다. CronJob으로 정기 일정을 잡으면, CoinTutor는 매일 02:00에, DrillQuiz는 매일 02:30에 자동으로 MinIO에 새로 올린 문서들을 검색해서 임베딩합니다. INCREMENTAL 모드면 변경된 것만 반영하고, 전체 재색인이려면 컬렉션을 비우고 처음부터 넣습니다.

정기 실행이 아니라 지금 바로 한 번 실행하고 싶으면, kubectl create job으로 CronJob에서 Job을 만듭니다. 예를 들어 CoinTutor용 CronJob에서 ingest-cointutor-1이라는 Job을 만들면, 바로 실행되고 끝나면 Pod가 completed 상태가 됩니다. 다시 실행하려면 ingest-cointutor-2 같이 이름을 바꿔서 새로운 Job을 만들어야 합니다.

전체 재색인도 중요합니다. 일반적으로 매일 변경분만 임베딩하는데, 어쩔 때는 기존 벡터들을 다 지우고 처음부터 다시 만들어야 합니다. 예를 들어 임베딩 모델을 바꿨거나, 청킹 방식을 바꿨으면 전체 재색인을 해야 합니다. 저장소에 INCREMENTAL=false로 설정된 별도 CronJob YAML이 있으니 참고하면 되고, 또는 chat-admin 관리 화면의 "재색인" 버튼으로도 전체 재색인 Job을 생성할 수 있습니다.
