# Git 히스토리에서 민감한 파일 제거하기 (Public 저장소)

Public 저장소에 `.cursor/`(API 키·Bearer 토큰 등)가 커밋된 경우, **히스토리를 다시 쓰면** 해당 파일이 모든 커밋에서 제거됩니다.  
**단, 이미 노출된 시크릿은 재발급·폐기해야 합니다.** (히스토리 캐시, fork, 봇 수집 등으로 이미 유출되었을 수 있음)

---

## 1. 반드시 먼저 할 일: 시크릿 재발급·폐기

- **Dify MCP** Bearer 토큰: Dify 앱/설정에서 해당 토큰 재발급 또는 비밀번호 변경
- **mcall-operator** `API_ACCESS_TOKEN`: 해당 서비스에서 키 재발급
- 그 밖에 `.cursor` 또는 다른 커밋에 들어간 API 키·비밀번호 전부 **재발급 또는 비활성화**

히스토리만 지워도, 이미 복제·캐시된 곳에는 예전 커밋이 남을 수 있으므로 시크릿 재발급은 필수입니다.

---

## 2. 히스토리에서 제거할 경로 정하기

예: **`.cursor/`** 디렉터리 전체를 모든 커밋에서 제거

(다른 파일도 제거하려면 아래 명령에 `--path` 를 추가로 나열하면 됨)

---

## 3. 도구 설치: git-filter-repo

`git filter-branch` 는 구식이고 느리므로 **git-filter-repo** 사용을 권장합니다.

```bash
# macOS (Homebrew)
brew install git-filter-repo

# 또는 pip
pip install git-filter-repo
```

---

## 4. 방법 A: 새 클론에서 실행 (권장)

가장 안전한 방법은 **새로 클론한 저장소**에서만 히스토리를 수정하는 것입니다.

```bash
cd /tmp   # 또는 다른 작업 디렉터리
git clone https://github.com/doohee323/tz-chatbot.git tz-chatbot-clean
cd tz-chatbot-clean

# .cursor/ 디렉터리를 전체 히스토리에서 제거
git filter-repo --path .cursor/ --invert-paths --force

# 원격 다시 추가 (filter-repo가 origin을 제거함)
git remote add origin https://github.com/doohee323/tz-chatbot.git
```

이후 **기존 로컬 저장소**에서 force push 할 때는 아래 5단계를 **이 새 클론(`tz-chatbot-clean`)에서** 실행합니다.

---

## 5. 방법 B: 현재 저장소에서 실행

**주의:** 현재 클론에서 실행하면 로컬 히스토리가 바로 바뀝니다. 백업·브랜치 확인 후 진행하세요.

```bash
cd /Users/dhong/workspaces/tz-chatbot

# 미처 푸시 안 한 커밋이 있으면 먼저 커밋 또는 스태시
git status

# .cursor/ 를 전체 히스토리에서 제거
git filter-repo --path .cursor/ --invert-paths --force

# filter-repo는 remote를 지우므로 다시 추가
git remote add origin https://github.com/doohee323/tz-chatbot.git
```

---

## 6. Force Push 로 GitHub 반영

**히스토리가 바뀌므로** 일반 push 가 거부됩니다. force push 가 필요합니다.

```bash
git push --force origin main
```

- **main** 이 기본 브랜치인 경우 위처럼 실행
- 다른 기본 브랜치를 쓰면 `main` 을 해당 브랜치 이름으로 바꾸면 됨

---

## 7. Push 후 확인

- GitHub 저장소에서 **Commits** 탭을 열고, 예전 커밋을 눌러서 **`.cursor` 디렉터리나 해당 파일이 더 이상 안 보이는지** 확인
- `git log --all --full-history -- .cursor/` 를 로컬에서 실행하면, 결과가 비어 있어야 합니다

---

## 8. 협업자·본인 다른 클론이 있는 경우

- 히스토리가 다시 쓰여졌기 때문에 **예전 커밋 해시는 모두 바뀝니다**
- 다른 PC·클론에서는 **예전 history 를 버리고 새로 받는 것**이 안전합니다:
  ```bash
  git fetch origin
  git reset --hard origin/main
  ```
  또는 해당 디렉터리를 삭제한 뒤 **다시 clone** 하는 것을 권장합니다.

---

## 9. GitHub 쪽 추가 조치 (선택)

- **Settings → General → Danger Zone** 에서 “**Remove sensitive data**” 등 안내가 있을 수 있음 (GitHub 버전에 따라 다름)
- 이미 **토큰·비밀번호는 1단계에서 반드시 재발급**했는지 다시 확인

---

## 요약 체크리스트

1. [ ] 노출된 시크릿 전부 재발급·폐기 (Dify, mcall-operator 등)
2. [ ] `git filter-repo` 설치
3. [ ] 새 클론에서 또는 현재 저장소에서 `git filter-repo --path .cursor/ --invert-paths --force` 실행
4. [ ] `git remote add origin ...` (필요 시)
5. [ ] `git push --force origin main` 로 GitHub 반영
6. [ ] GitHub에서 해당 파일이 히스토리에 더 이상 없는지 확인
7. [ ] 다른 클론은 `git reset --hard origin/main` 또는 재 clone
