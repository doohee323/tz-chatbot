# Calendar → Email 워크플로우

Google Calendar 일정이 생성/변경될 때 지정한 수신자에게 이메일을 보내는 Dify 워크플로우입니다.

## 방법 1: Dify Studio에서 직접 구성 (권장)

YAML 임포트는 플러그인 버전/스키마 차이로 실패할 수 있으므로, 아래 순서로 **Studio에서 노드를 직접 추가**하는 것을 권장합니다.

### 1. 워크플로우 앱 생성

1. **Studio** → **Create App** → **Workflow** 선택
2. 앱 이름 예: `Calendar-Email-Workflow`

### 2. 트리거: Google Calendar

1. **Trigger** 영역에서 **Plugin Trigger** 선택
2. **Google Calendar Trigger** 플러그인 선택 (미설치 시 Marketplace에서 설치)
3. Google OAuth 연결 후, 어떤 캘린더/이벤트 타입에서 워크플로를 실행할지 설정 (예: 특정 캘린더의 이벤트 생성/업데이트)
4. 트리거가 내보내는 변수 확인 (예: `event.summary`, `event.start`, `event.description`)

### 3. Code 노드: 이벤트 → 이메일 제목/본문

1. **+** → **Code** 노드 추가
2. 트리거 노드와 연결 (트리거 출력을 Code 입력으로)
3. 입력: 트리거 이벤트 객체 (플러그인 문서에 따른 필드명 사용)
4. 출력: `subject`(string), `body`(string)
5. 예시 로직:

```python
def main(trigger_output: dict) -> dict:
    event = trigger_output.get("event", trigger_output)
    summary = event.get("summary", "일정 알림")
    start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date", "")
    desc = event.get("description", "")
    return {
        "subject": f"[캘린더] {summary}",
        "body": f"일정: {summary}\n시작: {start}\n\n{desc}"
    }
```

### 4. Tool 노드: 이메일 발송

1. **+** → **Tool** → **Email** (langgenius/email) 선택
2. Code 노드와 연결
3. 파라미터 설정:
   - **to**: 수신 이메일 (고정값 또는 워크플로 변수)
   - **subject**: Code 노드 출력 `subject`
   - **body**: Code 노드 출력 `body`

### 5. 저장 및 트리거 구독

- **Save** 후 **Publish**
- Plugin Trigger 설정에서 **구독(Subscription)** 생성 완료 (Google Calendar가 Dify URL로 웹훅 발송하도록)

---

## 방법 2: YAML 임포트 시도

`Calendar-Email-Workflow.yml` 은 위 구조를 YAML로 정리한 템플릿입니다.

1. **Studio** → **Workflow** → **Import from YAML** (또는 앱 메뉴에서 Import)
2. `Calendar-Email-Workflow.yml` 선택
3. 플러그인 버전이 맞지 않으면 Marketplace에서 **Google Calendar Trigger**, **Email** 플러그인 설치 후 다시 시도
4. 임포트 후 각 노드에서 **연결·변수·수신자(to)** 등 필요 시 수정

### DSL 임포트 시 자주 나는 에러 (K8s dify-api 로그 기준)

- **`ValueError: 'plugin-trigger' is not a valid NodeType`**  
  Dify API가 노드 타입으로 `plugin-trigger`(하이픈)를 허용하지 않는 경우입니다.  
  YAML에서는 `type: plugin_trigger`(언더스코어)로 수정해 두었습니다.  
  그래도 같은 에러가 나면 해당 Dify 버전에서는 **플러그인 트리거를 DSL로 임포트하지 못하는 것**이므로, **방법 1**처럼 Studio에서 워크플로를 새로 만들고 트리거만 UI에서 추가하세요.

---

## Calandar-Email.yml (LLM 정리 → 이메일)

`Calandar-Email.yml` 은 **일정 데이터를 LLM이 이해하기 쉽게 문장으로 정리한 뒤 이메일로 보내는** 워크플로우입니다.

- **트리거** (Google Calendar) → **Code** (두 트리거 출력 합침) → **LLM** (제목·본문 생성) → **이메일** 발송
- LLM은 캘린더 이벤트(JSON)를 받아 `subject`, `email_body` 구조로 출력하고, 이메일 도구가 이를 제목·본문에 매핑합니다.
- **이메일 수신자(send_to)** 는 Dify Studio에서 **이메일 Tool 노드** 파라미터에 반드시 설정해야 합니다 (예: `["your@email.com"]` JSON 배열).

### "일정 데이터 합치기" Code 노드 – Input Variable에 트리거가 안 보일 때

Code 노드 INPUT VARIABLES 에서 **(x) Set variable** 을 눌렀을 때 **SYSTEM**(sys.user_id 등)만 보이고 **Google Calendar Event Created** 트리거 출력이 안 보이는 경우가 있습니다.

**원인**  
플러그인 트리거는 워크플로우 **시작 노드**라서, Dify UI에 따라 “변수 선택” 목록에 **노드 출력**이 아닌 **시작(Trigger) 출력**으로만 나오거나, 여러 트리거가 있을 때 목록에 아예 안 뜨는 경우가 있습니다.

**해결 방법 (둘 중 하나)**

1. **트리거 1개만 쓰기 (가장 단순)**  
   - Google Calendar 트리거를 **한 개만** 두고, 그 트리거만 Code 노드에 연결합니다.  
   - Code 노드 INPUT VARIABLES: 변수 **한 개** (예: `trigger_output`) 추가 후, **(x) Set variable** 에서 **트리거 노드**(Google Calendar Event Created) 또는 **Start/Trigger** 항목이 보이면 그걸 선택합니다.  
   - Code에서는 `trigger_output` 하나만 받아서 `events` 를 꺼내면 됩니다.  
   - 두 번째 트리거는 삭제하거나 연결을 끊어도 됩니다.

2. **Variable Aggregator 로 두 트리거 합치기**  
   - **Variable Aggregator** 노드를 추가합니다.  
   - **트리거 1** → Variable Aggregator, **트리거 2** → Variable Aggregator 로 연결합니다.  
   - Aggregator 설정에서 두 트리거의 출력을 각각 변수로 추가합니다 (실행 시 한쪽만 값이 들어옴).  
   - **Variable Aggregator** → **일정 데이터 합치기** Code 노드로 연결합니다.  
   - Code 노드 INPUT VARIABLES 는 **한 개**만 두고, 소스를 **Variable Aggregator** 출력으로 지정합니다.  
   - Code에서는 “어느 트리거에서 왔든” 한 덩어리만 받아서 `events` 를 꺼내면 됩니다.

**Input Variable 이란**  
Code 노드가 **위쪽 노드(트리거, Aggregator 등)에서 어떤 값을 받아올지** 지정하는 것입니다. “Set variable”에서 **그 위쪽 노드의 출력**을 고르면, 워크플로 실행 시 그 노드의 결과가 Code의 `main(trigger1, trigger2)` 인자로 넘어갑니다.

## 필요한 플러그인

| 플러그인 | 용도 |
|----------|------|
| **Google Calendar Trigger** (langgenius/google_calendar_trigger) | 일정 이벤트 수신 → 워크플로 실행 |
| **Email** (langgenius/email) | 이메일 발송 |

두 플러그인 모두 **Settings → Plugins**에서 설치·인증 후 사용할 수 있습니다.
