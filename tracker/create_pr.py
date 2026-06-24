import os
import requests

def create_pull_request(owner, repo, token, head, base, title, body):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if r.status_code == 201:
        print(f"PR Created Successfully: {r.json().get('html_url')}")
    else:
        print(f"Failed to create PR: {r.status_code}")
        print(r.text)

if __name__ == "__main__":
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")
    
    if owner and repo and token:
        create_pull_request(
            owner, repo, token,
            head="cleanup-and-fixes",
            base="main",
            title="Refactor: Clean up unused code and fix NameErrors",
            body="이 PR은 다음 변경 사항을 포함합니다:\n1. NameError 수정 (courtlistener.py)\n2. 미사용 상수, 클래스 필드 및 함수 제거 (courtlistener.py, extract.py, complaint_parse.py)\n3. 환경 변수 체크 강화 및 중복 임포트 정리 (run.py)"
        )
    else:
        print("Required environment variables missing.")
