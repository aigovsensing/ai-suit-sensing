# 🔗 GitHub Issues API 사용 가이드

> **대상**: GitHub REST API를 활용하여 Issue를 자동으로 생성/관리하고 댓글로 리포트를 누적하는 방법을 학습합니다.  
> **관련 파일**: [`src/github_issue.py`](../src/github_issue.py)

---

## 1. GitHub Issues API란?

GitHub REST API를 통해 저장소의 Issue를 프로그래밍 방식으로 생성·수정·조회·종료할 수 있습니다.

- **Base URL**: `https://api.github.com`
- **인증**: Bearer Token (GitHub Token)
- **공식 문서**: https://docs.github.com/en/rest/issues

---

## 2. 인증 설정

### Personal Access Token (PAT) 발급
1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **"Generate new token"** 클릭
3. 필요 권한 선택:
   - `repo` → `issues` (Issue 읽기/쓰기)
   - `public_repo` (공개 저장소만인 경우)
4. 토큰 복사

### GitHub Actions에서 자동 토큰 사용
```yaml
env:
  GITHUB_TOKEN: ${{ github.token }}   # 워크플로우 실행 시 자동 제공
```

### 요청 헤더
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
```

---

## 3. 주요 API 엔드포인트

| 기능 | Method | 엔드포인트 |
|------|--------|-----------|
| Issue 목록 조회 | GET | `/repos/{owner}/{repo}/issues` |
| Issue 생성 | POST | `/repos/{owner}/{repo}/issues` |
| Issue 수정/종료 | PATCH | `/repos/{owner}/{repo}/issues/{number}` |
| 댓글 목록 조회 | GET | `/repos/{owner}/{repo}/issues/{number}/comments` |
| 댓글 생성 | POST | `/repos/{owner}/{repo}/issues/{number}/comments` |

---

## 4. 주요 기능 구현 (이 프로젝트)

### 4-1. Issue 찾기 또는 생성

```python
import requests

def find_or_create_issue(owner, repo, token, title, label):
    """오늘 날짜의 Issue를 찾거나 새로 생성합니다."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # 열린 Issue 중 동일 제목 검색
    r = requests.get(url, headers=headers, params={
        "state": "open",
        "labels": label,
        "per_page": 50,
    })
    for issue in r.json():
        if issue["title"] == title:
            return issue["number"]   # 기존 Issue 번호 반환

    # 없으면 새 Issue 생성
    r = requests.post(url, headers=headers, json={
        "title": title,
        "body": "## 📋 자동 수집 리포트\n\n이 이슈에는 자동 수집된 리포트가 댓글로 누적됩니다.",
        "labels": [label],
    })
    return r.json()["number"]
```

### 4-2. 댓글 추가 (리포트 등록)

```python
def create_comment(owner, repo, token, issue_number, body):
    """Issue에 마크다운 댓글을 추가합니다."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    r = requests.post(url, headers=headers, json={"body": body})
    r.raise_for_status()
    return r.json()
```

### 4-3. Issue 종료 (Close)

```python
def close_issue(owner, repo, token, issue_number):
    """Issue를 종료(Close) 상태로 변경합니다."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    r = requests.patch(url, headers=headers, json={"state": "closed"})
    r.raise_for_status()
```

### 4-4. 댓글 전체 조회

```python
def list_comments(owner, repo, token, issue_number):
    """Issue의 모든 댓글을 반환합니다."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    r = requests.get(url, headers=headers)
    return r.json() or []
```

---

## 5. Issue 라벨 활용

이 프로젝트는 `ai-lawsuit-monitor` 라벨로 관련 Issue를 필터링합니다.

### 라벨 생성 (최초 1회)
```python
requests.post(
    f"https://api.github.com/repos/{owner}/{repo}/labels",
    headers=headers,
    json={
        "name": "ai-lawsuit-monitor",
        "color": "0075ca",
        "description": "AI 소송 모니터링 자동 생성 Issue",
    }
)
```

### 라벨로 Issue 필터링
```python
r = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers=headers,
    params={
        "state": "all",      # open, closed, all
        "labels": "ai-lawsuit-monitor",
        "per_page": 50,
        "sort": "created",
        "direction": "desc",
    }
)
issues = r.json()
```

---

## 6. 이 프로젝트의 Issue 라이프사이클

```
[새 날짜 시작]
       ↓
find_or_create_issue()  → 오늘 Issue 생성 (또는 기존 Issue 재사용)
       ↓
apply_deduplication()   → 중복 내용 제거
       ↓
create_comment()        → 조간뉴스 댓글 (Gemini 분석)
       ↓
create_comment()        → 메인 리포트 댓글
       ↓
[다음 날 첫 실행]
       ↓
close_other_daily_issues()
  ├─ generate_consolidated_report()  → 통합 리포트 댓글
  ├─ generate_daily_report()         → 석간뉴스 댓글 + 이메일 발송
  └─ comment_and_close_issue()       → 마무리 댓글 + Issue Close
```

---

## 7. 웹 브라우저로 GitHub Issues 활용

### 이슈 필터링 URL

```
# 특정 라벨의 열린 이슈 목록
https://github.com/{owner}/{repo}/issues?q=is:open+label:ai-lawsuit-monitor

# 모든 이슈 (열림 + 닫힘)
https://github.com/{owner}/{repo}/issues?q=label:ai-lawsuit-monitor

# 최신순 정렬
https://github.com/{owner}/{repo}/issues?q=label:ai-lawsuit-monitor&sort=created&direction=desc
```

### Markdown 렌더링 확인
- GitHub Issue 본문과 댓글은 **자동으로 Markdown 렌더링**
- `## 제목`, `**굵게**`, `| 표 |`, ` ```코드``` ` 등 모두 지원
- `> [!NOTE]`, `> [!WARNING]` 등 GitHub Alert 문법 지원

---

## 8. Rate Limit 관리

GitHub API는 **시간당 요청 수 제한**이 있습니다.

| 인증 방법 | 시간당 요청 수 |
|---------|-------------|
| 미인증 | 60회 |
| Token 인증 | 5,000회 |
| GitHub Actions Token | 1,000회 (저장소당) |

### Rate Limit 확인
```python
r = requests.get("https://api.github.com/rate_limit", headers=headers)
limits = r.json()["rate"]
print(f"남은 요청: {limits['remaining']}/{limits['limit']}")
print(f"리셋 시각: {datetime.fromtimestamp(limits['reset'])}")
```

---

## 9. 참고 자료

| 링크 | 설명 |
|------|------|
| [GitHub REST API 문서](https://docs.github.com/en/rest) | 공식 문서 |
| [Issues API](https://docs.github.com/en/rest/issues) | Issue/댓글 API |
| [GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github) | 지원 Markdown 문법 |
| [GitHub Alerts](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts) | NOTE/WARNING/CAUTION 박스 |
