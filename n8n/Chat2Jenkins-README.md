# Chat2Jenkins 워크플로 사용 방법

채팅으로 Jenkins 프로젝트 빌드를 트리거하고 결과를 이메일로 받는 n8n 워크플로입니다.

## 워크플로 구조

```
When chat message received (채팅 수신)
    ↓
Extract Job Name (프로젝트명 추출)
    ↓
Trigger Jenkins Build (Jenkins 빌드 시작)
    ↓
Wait 3 seconds (대기)
    ↓
Get Build Status (빌드 상태 조회)
    ↓
Prepare Email Data (이메일 데이터 준비)
    ↓
Send Email (이메일 발송)
```

## 사용 방법

### 1. n8n에 워크플로 가져오기

- n8n UI: **Workflows** → **Import from File** → `Chat2Jenkins.json` 선택
- 또는 API: `POST /api/v1/workflows` 로 JSON body 전송

### 2. Jenkins API 인증 설정 (필수)

**"Trigger Jenkins Build"** 및 **"Get Build Status"** 노드에서:

1. 노드를 더블클릭
2. **Credential for HTTP Basic Auth** 선택
3. **Create new credential** 클릭
4. 다음 정보 입력:
   - **Username**: Jenkins 사용자명 (예: `admin`)
   - **Password**: Jenkins API Token (`11ca2e4847b9389657719bc55e4a6e9390`)
   - 각 노드에서 동일한 credential 적용

### 3. Gmail 연동 (필수)

**"Send Email"** 노드:

1. 노드를 더블클릭
2. **Credential for Gmail** 에서 **Create new** 선택
3. Gmail OAuth2로 로그인해 계정 연결
4. **Send to** 가 `doohee323@gmail.com` 인지 확인 (다르면 변경)

### 4. 채팅 인증 설정 (필수)

**"When chat message received"** 노드:

1. 노드를 더블클릭
2. **Credential for HTTP Basic Auth** 에서 새 credential 생성
3. 사용자명/비밀번호 설정 (채팅 접속 시 로그인)

### 5. 워크플로 활성화

우측 상단 **Active** 스위치를 켜기

## 사용 예제

워크플로 활성화 후 채팅 URL로 접속해서:

```
cointutor-build 빌드해줘
```

또는

```
inference-api 빌드해줘
```

입력하면:

1. 프로젝트명(`cointutor-build`) 추출
2. Jenkins에서 해당 job 빌드 시작
3. 3초 대기 후 빌드 상태 조회
4. 결과를 이메일로 발송

## 주의사항

### Jenkins URL 및 Token

워크플로에 하드코딩되어 있습니다:
- **Jenkins URL**: `https://jenkins.drillquiz.com`
- **Jenkins Token**: `11ca2e4847b9389657719bc55e4a6e9390`

변경하려면 **"Extract Job Name"** 노드에서:
```javascript
{
  "jobName": "{{ $json.chatInput.split(' ')[0] }}",
  "jenkinsUrl": "https://your-jenkins-url",
  "jenkinsToken": "your-token"
}
```

### 프로젝트명 추출 로직

현재는 채팅 입력의 **첫 번째 공백 이전 단어**를 프로젝트명으로 사용합니다:

```
입력: "cointutor-build 빌드해줘"
추출된 jobName: "cointutor-build"
```

더 복잡한 로직이 필요하면 정규식 활용:
```javascript
{{ $json.chatInput.match(/^(\S+)/)?.[1] }}
```

### 빌드 상태 확인

워크플로는 빌드 **시작** 후 3초 대기 후 마지막 빌드 상태를 확인합니다.

- 빌드가 오래 걸리는 경우: **Wait 3 seconds** 노드의 대기 시간 증가
- 실시간 진행상황: Jenkins 웹 UI에서 직접 확인 (`https://jenkins.drillquiz.com`)

## 트러블슈팅

### 이메일이 오지 않음

1. Gmail credential이 제대로 연결되었는지 확인
2. **Send Email** 노드의 **sendTo** 이메일 주소 확인
3. n8n 로그에서 오류 메시지 확인

### Jenkins 빌드가 실패

1. Jenkins URL이 정확한지 확인: `https://jenkins.drillquiz.com`
2. API Token이 유효한지 확인
3. 프로젝트명이 정확한지 확인 (대소문자 구분)
4. Jenkins 접근 권한 확인

### 빌드 상태가 "UNKNOWN"

빌드 대기 시간이 짧을 수 있습니다. **Wait 3 seconds** 노드의 대기 시간을 증가시키세요:
- 5초: `waitValue: 5`
- 10초: `waitValue: 10`

## 참고

- 이메일에 포함되는 정보: 프로젝트명, 빌드 상태, 빌드 번호, 빌드 URL, 타임스탬프
- Chat2Gmail2.json과 유사한 구조로 설계됨
- Jenkins API 문서: https://jenkins.drillquiz.com/api/
