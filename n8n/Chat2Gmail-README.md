# Chat2Gmail 워크플로 사용 방법

채팅 메시지를 받아서 Gmail로 "Daily quote" 이메일을 보내는 n8n 워크플로입니다.

## 워크플로 구조

1. **When chat message received** (채팅 트리거) → 사용자가 보낸 메시지 수신
2. **Results** (Set 노드) → 채팅 입력을 `quote` 변수로 설정
3. **Connect your Gmail** (Gmail 노드) → 수신자에게 이메일 발송

## 하려면 (필수 설정)

### 1. n8n에 워크플로 가져오기

- n8n UI: 메뉴 → **Import from File** → `Chat2Gmail.json` 선택  
- 또는 API: `POST /api/v1/workflows` 로 JSON body 전송

### 2. Gmail 연동 (필수)

- **Connect your Gmail** 노드 더블클릭
- **Credential for Gmail** 에서 **Create new** 선택
- Gmail OAuth2로 로그인해 계정 연결
- 수신 주소가 다르면 **Send to** 를 본인 이메일로 변경 (현재 `doohee323@gmail.com`)

### 3. 채팅 인증 (필수)

- **When chat message received** 노드는 **Basic Auth** 사용
- **Credential for HTTP Basic Auth** 에서 새 credential 생성 후 사용자명/비밀번호 설정
- 채팅 URL 접속 시 이 사용자명·비밀번호로 로그인하게 됨

### 4. 워크플로 활성화

- 우측 상단 **Active** 스위치를 켜기
- 채팅 URL이 생성되면 해당 URL로 접속해 메시지를 보내면, 그 내용이 `quote` 로 들어가 이메일로 전송됨

## 참고

- 이메일 본문은 `{{ $json.author }}` 와 `{{ $json.quote }}` 를 사용하는데, 현재 Set 노드는 **quote** 만 채움. **author** 도 쓰려면 Results(Set) 노드에 `author` 필드를 추가하거나, 채팅 입력을 JSON(예: `{"author":"이름","quote":"문구"}`)으로 보내도록 구성하면 됩니다.
- 시간대 등은 워크플로 **Settings** 에서 변경 가능 (기본: America/Los_Angeles).
