# DrillQuiz 사용자 가이드

DrillQuiz에 오신 것을 환영합니다! 이 가이드에서는 DrillQuiz의 주요 기능을 쉽게 활용하는 방법을 안내합니다.

---

## 목차

1. [DrillQuiz란?](#1-drillquiz란)
2. [시작하기](#2-시작하기)
3. [문제 파일 관리](#3-문제-파일-관리)
4. [시험 만들기와 풀기](#4-시험-만들기와-풀기)
5. [스터디로 함께 학습하기](#5-스터디로-함께-학습하기)
6. [학습 결과 확인하기](#6-학습-결과-확인하기)
7. [고급 기능](#7-고급-기능)
8. [프로필 및 설정](#8-프로필-및-설정)
9. [자주 묻는 질문](#9-자주-묻는-질문)

---

## 1. DrillQuiz란?

DrillQuiz는 **문제 풀이를 통한 효율적인 학습**을 지원하는 플랫폼입니다.

### 핵심 기능

- **문제 파일 업로드**: Excel, CSV 파일로 대량의 문제를 한 번에 등록
- **시험 생성**: 업로드한 문제로 맞춤 시험 만들기
- **스터디 그룹**: 가족, 친구, 동료와 함께 학습 진행 상황 공유
- **틀린 문제 복습**: 자동으로 수집된 틀린 문제로 반복 학습
- **음성 모드**: 마이크로 답변 입력, 발음 연습
- **AI 모의 인터뷰**: AI가 질문하고 답변을 평가해 주는 인터뷰 형식 학습

### 누구에게 유용한가요?

- **학생**: 숙제, 시험 대비, 반복 학습
- **부모님**: 자녀 학습 관리, 진도 확인, 결과 공유
- **선생님**: 학생 숙제 관리, 학습 현황 파악
- **직장인**: 자격증, 면접 준비

---

## 2. 시작하기

### 2.1 회원가입

1. 홈페이지에서 **Login** 또는 **Register** 클릭
2. **Register** 페이지로 이동
3. 다음 정보 입력:
   - **Username** (필수): 로그인에 사용할 아이디
   - **Name** (필수): 표시 이름
   - **Email** (필수): 이메일 주소
   - **Password** (필수): 비밀번호
   - **Password confirmation** (필수): 비밀번호 확인
   - Affiliation, Location: 선택 사항
4. **Register** 버튼 클릭
5. 가입 완료 후 자동으로 로그인됩니다.

### 2.2 Google로 로그인

1. **Login** 페이지 접속
2. **Login with Google** 버튼 클릭
3. Google 계정 선택 및 권한 승인
4. 첫 로그인 시 자동으로 계정이 생성됩니다.

### 2.3 처음 사용자를 위한 추천 흐름

1. 회원가입 또는 로그인
2. **Quiz Files** → 샘플 파일 다운로드 또는 본인 문제 파일 업로드
3. **Exam Management** → 새 시험 생성
4. 시험 풀기 → 결과 확인
5. 필요 시 **Study Management**에서 스터디 생성

---

## 3. 문제 파일 관리

### 3.1 문제 파일 업로드

**지원 형식**: Excel (.xlsx, .xls), CSV

1. 상단 메뉴에서 **Quiz Files** 클릭
2. **Upload File** 버튼 클릭
3. 파일 선택 후 다음 정보 입력:
   - **Title**: 파일 제목
   - **Description**: 설명 (선택)
   - **Public/Private**: 공개 여부
   - **Language**: 한국어/영어
4. **Upload** 클릭
5. 업로드 완료 후 파일 목록에서 확인

**팁**: 샘플 형식은 `public/sample_en.xlsx` 또는 `public/sample_kr.xlsx`를 참고하세요.

### 3.2 문제 파일 다운로드

1. **Quiz Files** 페이지에서 원하는 파일 찾기
2. 해당 행의 **Download** 버튼 클릭
3. 브라우저 다운로드 폴더에 Excel 파일이 저장됩니다.

---

## 4. 시험 만들기와 풀기

### 4.1 시험 만들기

1. **Exam** 메뉴 → **Exam Management** 이동
2. **+ Create** 버튼 클릭
3. 시험 정보 입력:
   - **Title (Korean / English)**: 시험 제목
   - **Description**: 설명 (선택)
4. **Select Questions** 클릭
5. 문제 선택 모달에서:
   - 문제 파일 선택
   - 개별 또는 전체 문제 선택
   - **Add Selected** 클릭
6. 추가된 문제 순서는 드래그로 변경 가능
7. 옵션 설정:
   - **Public/Private**: 공개 여부
   - **Force answer input**: 답안 입력 강제
   - **Enable voice mode**: 음성 모드 지원
8. **Create Exam** 클릭

### 4.2 시험 풀기

1. **Exam Management**에서 시험 선택
2. **Details** 버튼 클릭
3. 시험 정보 확인 후 **Start Exam** 클릭
4. 문제 풀이:
   - **객관식**: 선택지 클릭
   - **주관식**: 텍스트 입력
5. **Submit Answer** 클릭 후 정답/오답 확인
6. 해설 확인 후 **Next**로 다음 문제 이동
7. 모든 문제 완료 시 결과 페이지로 자동 이동

### 4.3 재시험 (틀린 문제만)

1. **Results** 페이지 접속
2. 재시험할 시험 결과 선택
3. **Retake Exam** 버튼 클릭
4. **Wrong answers only** 또는 **All questions** 선택
5. **Create Retake** 확인
6. 새로 생성된 재시험을 **Exam Management**에서 시작

### 4.4 시험 구독 및 일일 시험

1. **Exam Management**에서 구독할 시험 선택
2. **Subscribe** 버튼 클릭 (구독됨 표시 확인)
3. 다음 날 **Daily Exam**에서 구독한 시험의 랜덤 문제 풀기
4. **Profile**에서 구독 목록 관리

### 4.5 시험 복사·수정·삭제

- **복사**: 시험 선택 → **Copy** → 제목에 "Copy"가 붙은 새 시험이 생성됩니다.
- **수정**: **Details** → **Edit** → 제목, 문제, 순서 등 수정 후 **Save Changes**
- **삭제**: 시험 선택(체크박스) → **Delete** → 확인 모달에서 **Confirm Delete**

---

## 5. 스터디로 함께 학습하기

### 5.1 스터디 생성

1. **Study** 메뉴 → **Study Management** 이동
2. **+ Create** 버튼 클릭
3. 스터디 정보 입력:
   - **Title (Korean / English)**: 스터디 이름
   - **Goal (Korean / English)**: 목표
   - **Start Date / End Date**: 기간
   - **Public/Private**: 공개 여부
4. **Create Study** 클릭

### 5.2 Task 추가하기

1. 생성한 스터디의 **Detail** 페이지 이동
2. **Add Task** 클릭
3. Task 정보 입력:
   - **Task Name**: 과제 이름 (선택)
   - **Exam**: 연결할 시험 선택
   - **Due Date**: 마감일 (선택)
   - **Order**: 순서
4. **Add Task** 클릭
5. 여러 Task 추가 시 드래그로 순서 변경 가능

### 5.3 멤버 관리

1. 스터디 **Detail** 페이지 → **Members** 탭
2. **Add Member** 클릭
3. Username 또는 Email 입력, Role(Member/Admin) 선택
4. **Add** 클릭

### 5.4 공개 스터디 가입 요청

1. **Study Management**에서 **Public Studies** 필터 선택
2. 가입할 스터디 선택
3. **Request to Join** 클릭
4. 가입 요청 메시지 입력 (선택) 후 **Submit Request**
5. 스터디 관리자 승인 후 멤버로 추가됩니다.

### 5.5 진행률 확인

1. **Study Management**에서 스터디 선택
2. **Progress** 컬럼에서 전체 진행률 확인
3. 스터디 클릭 → **View Progress Dashboard**로 상세 대시보드 이동
4. 멤버별·Task별 진행률, 그래프 확인

---

## 6. 학습 결과 확인하기

### 6.1 시험 결과 조회

1. **Results** 메뉴 클릭 (또는 홈의 Recent Quizzes)
2. 결과 목록에서 확인:
   - 시험명, 점수, 정답/오답 수
   - 완료 날짜, 소요 시간
3. 특정 결과 클릭 → 문제별 상세 확인
4. 날짜·시험별 필터링, 통계 요약 활용

### 6.2 개인 통계

1. **Profile** → **Statistics** 탭
2. 총 시험 수, 평균 점수, 총 문제 풀이 수, 정답률 확인
3. 기간 필터(1주일/1개월/3개월/1년) 적용
4. 차트로 학습 패턴·추이 확인

### 6.3 랜덤 연습

1. 홈의 **Random Practice** 카드 클릭
2. 설정:
   - 문제 수 (5/10/20/50)
   - 난이도 (Easy/Medium/Hard/All)
   - 태그 선택 (선택)
   - 틀린 문제 우선 (선택)
3. **Start Practice** 클릭
4. 자동 생성된 시험 풀기

### 6.4 틀린 문제 복습

1. **Profile** → **Wrong Answers** 섹션
2. 틀린 문제 목록 확인 (정답률 낮은 순)
3. **Practice Wrong Answers** 클릭
4. 문제 수 선택 (최근 10/20/전체) 후 **Start Practice**

---

## 7. 고급 기능

### 7.1 즐겨찾기

- 시험 풀이 중 **별 아이콘** 클릭 → 즐겨찾기 추가
- **Favorites** 메뉴에서 즐겨찾기한 문제만 모아서 풀기

### 7.2 문제 무시

- 시험 풀이 중 **Ignore this question** 클릭
- 해당 문제는 랜덤·일일 시험에서 제외
- **Profile**에서 무시한 문제 목록 확인 및 **Unignore**로 해제 가능

### 7.3 음성 모드

1. 음성 모드 지원 시험 선택 후 시험 시작
2. **Voice Mode** 토글 활성화
3. 마이크 권한 허용
4. **Start Recording** → 답변 말하기 → **Stop Recording**
5. 변환된 텍스트 확인·수정 후 **Submit Answer**

**팁**: 조용한 환경, 명확한 발음을 권장합니다.

### 7.4 AI 모의 인터뷰

1. AI 인터뷰 지원 시험 선택
2. 시험 시작 후 **AI Interview Mode** 활성화
3. **Start Interview** 클릭
4. AI 질문에 텍스트 또는 음성으로 답변
5. AI 피드백과 추가 질문으로 대화형 진행
6. 완료 후 최종 평가 및 개선 사항 확인

### 7.5 다국어 학습

1. **Profile** → 언어 설정에서 **한국어** 또는 **English** 선택
2. **Save Changes** 클릭
3. UI와 콘텐츠가 선택한 언어로 표시됩니다.

---

## 8. 프로필 및 설정

### 8.1 프로필 수정

1. 상단 네비게이션에서 사용자명 클릭 → **Profile**
2. Email, 언어 설정 변경
3. **Save Changes** 클릭

### 8.2 비밀번호 변경 (일반 계정)

1. **Profile** → **Change Password** 섹션
2. Current Password, New Password, Confirm New Password 입력
3. **Change Password** 클릭

### 8.3 학습 데이터 초기화

1. **Profile** → **Data Management** 섹션
2. **Clear All My Data** 클릭
3. 확인 모달에서 **Confirm** 클릭

**주의**: 시험 결과가 모두 삭제되며, 되돌릴 수 없습니다. 시험·스터디·계정은 유지됩니다.

### 8.4 회원 탈퇴

1. **Profile** → **Account Management** 섹션
2. **Delete Account** 클릭
3. 사유 입력 (선택) 후 **Confirm Delete** 클릭

**주의**: 계정과 모든 데이터가 삭제되며, 복구할 수 없습니다.

---

## 9. 자주 묻는 질문

### Q1. Excel 파일 형식은 어떻게 만들어야 하나요?

`public/sample_en.xlsx` 또는 `public/sample_kr.xlsx`를 참고하세요. 문제 제목, 내용, 정답, 해설 등을 컬럼으로 구성하면 됩니다.

### Q2. 시험을 공개하면 누구나 풀 수 있나요?

네. 공개(Public) 시험은 로그인하지 않아도 풀 수 있습니다. 비공개(Private)는 본인만 접근할 수 있습니다.

### Q3. 스터디 멤버는 어떻게 시험에 접근하나요?

스터디에 Task로 추가된 시험은 해당 스터디 멤버가 구독 여부와 관계없이 **내 시험**에서 확인하고 풀 수 있습니다.

### Q4. 틀린 문제는 어디서 확인하나요?

**Profile**의 **Wrong Answers** 섹션에서 확인할 수 있습니다. 여기서 틀린 문제만 모아 복습할 수 있습니다.

### Q5. 음성 모드가 작동하지 않아요.

- 브라우저 마이크 권한이 허용되었는지 확인하세요.
- Chrome, Safari 등 최신 브라우저 사용을 권장합니다.
- 시험이 음성 모드 지원으로 생성되었는지 확인하세요.

### Q6. 언어를 바꾸면 기존 학습 데이터가 사라지나요?

아니요. 언어 설정은 화면 표시에만 영향을 주며, 시험 결과·진행률 등은 그대로 유지됩니다.

---

## 관련 문서

- **[사용 시나리오](USER_SCENARIOS.md)**: 엄마와 아이, 선생님과 학생 등 실제 활용 사례
- **[Use Case 명세](../usecase/USECASE.md)**: 시스템 기능별 상세 시나리오 (테스트·개발 참고용)

---

## 도움말 및 문의

- **이슈 신고**: [GitHub Issues](https://github.com/doohee323/drillquiz/issues)
- **저장소**: https://github.com/doohee323/drillquiz

DrillQuiz와 함께 효율적인 학습을 시작해 보세요.
