# Dify K8s 로그 확인 및 qa_chunk 에러 대응

## 1. 로그 확인 (네임스페이스 `dify`)

```bash
# Pod 목록
kubectl get pods -n dify

# API 서버 로그 (실행 오류, 워크플로/지식베이스 처리)
kubectl logs -n dify deployment/dify-api --tail=200

# 실시간 로그
kubectl logs -n dify deployment/dify-api -f

# Worker 로그 (비동기 작업, 인덱싱 등)
kubectl logs -n dify deployment/dify-worker --tail=200

# 특정 Pod 이름으로 로그 (복수 레플리카일 때)
kubectl logs -n dify -l app.kubernetes.io/name=dify-api --tail=100 --prefix=true
```

## 2. `qa_chunk` IndexError: index 2 is out of bounds for axis 0 with size 2

**증상**: 지식베이스 "테스트 실행" 시  
`An error occurred in the langgenius/qa_chunk/qa_chunk ... IndexError: index 2 is out of bounds for axis 0 with size 2`

**원인 요약**

- 입력에 **파일이 없음**: `sys.files: []` 인 상태에서 테스트를 돌리면, Q&A 청크 노드가 파일에서 열(column)을 읽으려다 **열 개수(2)보다 큰 인덱스(2)** 에 접근해 에러가 납니다.
- CSV가 **question, answer** 두 열이면 열 인덱스는 0, 1뿐인데, `Column_Number_for_Answers: 2` 를 **0-based** 로 쓰면 인덱스 2를 참조하게 되어 같은 에러가 날 수 있습니다.

**조치**

1. **테스트 실행이 아니라 문서 업로드로 진행**
   - 지식베이스 → 데이터 소스 추가 → **Q&A 형식** 선택 후 `USER_GUIDE_QA.csv`(또는 `USER_GUIDE_QA_en.csv`)를 **업로드**.
   - "테스트 실행"은 업로드된 파일이 있을 때만 동작하도록 되어 있으므로, **먼저 파일을 올리고** 인덱싱/처리를 실행하세요.
2. **열 번호 설정 (0-based)**
   - Dify UI 도움말: **"The number of first column is 0"** — 즉 Dify는 **0부터 시작**하는 열 번호를 씁니다.
   - `USER_GUIDE_QA.csv` / `USER_GUIDE_QA_en.csv` 는 1번째 열 = question, 2번째 열 = answer 이므로:
     - **Column Number for Questions** = **0** (첫 번째 열)
     - **Column Number for Answers** = **1** (두 번째 열)
   - 화면에서 **1, 2** 로 되어 있으면 **0, 1** 로 바꾼 뒤 **프로세스** 실행하세요. 1과 2로 두면 "index 2 is out of bounds for axis 0 with size 2" 에러가 납니다.
3. **Dify 버전**
   - 사용 중인 버전(예: 1.11.4)의 Release Notes에서 `qa_chunk` / Q&A 인덱싱 관련 이슈가 있는지 확인합니다.

## 3. 트레이싱에서 상세 확인

UI 안내대로 **트레이싱(Tracing)** 탭으로 이동해 해당 실행의 상세 로그를 보면, 실패한 노드와 스택 정보를 확인할 수 있습니다.  
K8s 쪽 로그와 함께 보려면:

```bash
kubectl logs -n dify deployment/dify-api --tail=300 | grep -A 5 -i "qa_chunk\|IndexError\|error"
```

## 4. "Index chunk variable is required" / 청크 0개

**증상**: Q&A CSV를 올리고 열 번호 0, 1 로 했는데도  
- 상단에 **"Index chunk variable is required."** 에러  
- 청크 0개, 문단 0, 평균 0 characters

**원인**: 지식베이스를 **지식 파이프라인(Knowledge Pipeline)** 으로 만든 경우, CSV 업로드 시 "인덱스에 쓸 청크 변수"가 지정되지 않아 발생하는 알려진 이슈입니다.

**조치 (둘 중 하나)**

1. **일반 지식베이스로 새로 만들기 (권장)**  
   - **지식(Knowledge)** → **만들기** 또는 **새 지식**  
   - 생성 방식에서 **"문서 업로드"** 방식(파이프라인이 아닌 **일반** 지식 생성)을 선택합니다.  
   - 데이터 소스에서 **Q&A** 형식 선택 후 CSV 업로드, Column for Questions = **0**, Answers = **1** 로 설정하고 **저장 및 처리** 실행.  
   - 이 방식이면 "Index chunk variable" 단계가 없어서 위 에러가 나지 않습니다.
2. **파이프라인을 계속 쓸 때**  
   - 파이프라인 편집 화면에서, 파일/CSV를 처리하는 노드 다음에 **"인덱스 청크"** 또는 **"Index chunk"** 를 지정하는 변수/노드가 있는지 확인합니다.  
   - 해당 필드에 **질문 열(column 0)** 을 인덱싱에 사용하도록 매핑해야 합니다. (UI가 버전마다 다를 수 있음.)

## 5. Qdrant 404 — Collection doesn't exist

**증상**:  
`Unexpected Response: 404 (Not Found)`  
`Not found: Collection 'Vector_index_..._Node' doesn't exist!`

**원인**: Dify 지식베이스가 사용하는 **벡터 인덱스 컬렉션**이 Qdrant에 없음.  
- 문서 처리(인덱싱)가 실패했거나, Qdrant를 초기화/재설치했거나, 해당 지식베이스가 아직 한 번도 성공적으로 인덱싱되지 않은 경우 발생.

**조치**

1. **지식베이스에서 문서 다시 처리**  
   - 해당 지식베이스 → **문서** → 해당 문서(CSV) 선택 → **재처리** 또는 **다시 처리** 실행.  
   - 청크가 정상 생성된 뒤 임베딩이 돌아가면 Qdrant에 `Vector_index_..._Node` 컬렉션이 생성됩니다.
2. **Qdrant 컬렉션 확인** (선택)  
   - Qdrant가 K8s `rag` 네임스페이스에 있다면:  
     `kubectl exec -n rag deployment/qdrant -- curl -s http://localhost:6333/collections`  
   - 목록에 해당 컬렉션이 없으면 위 1번으로 재처리 후 다시 확인.
3. **지식베이스를 새로 만든 경우**  
   - "일반 문서 업로드" 방식으로 지식 생성 → Q&A CSV 업로드 → Column 0, 1 설정 → **저장 및 처리**를 한 번 성공시키면, 그때 컬렉션이 생성됩니다. 이전에 "Index chunk variable" 등으로 실패했다면 컬렉션이 안 만들어진 상태일 수 있음.

## 6. 요약

| 확인 항목 | 명령어 |
|-----------|--------|
| Pod 상태 | `kubectl get pods -n dify` |
| API 로그 | `kubectl logs -n dify deployment/dify-api --tail=200` |
| Worker 로그 | `kubectl logs -n dify deployment/dify-worker --tail=200` |
| qa_chunk 에러 시 | Q&A CSV 업로드 후 열 번호 **0, 1** (0-based) 설정 |
| Index chunk variable / 청크 0개 | **일반 지식 생성(문서 업로드)** 방식으로 지식베이스 새로 만들어서 Q&A CSV 업로드 |
| Qdrant 404 Collection doesn't exist | 지식베이스에서 해당 문서 **재처리**하여 벡터 인덱스(Qdrant 컬렉션) 생성 |
