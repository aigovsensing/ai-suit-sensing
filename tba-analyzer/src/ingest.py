"""tracker 가 생성한 GitHub Issue(및 누적 댓글)를 수집한다.

label(기본 ai-lawsuit-monitor) 로 이슈를 찾고, 본문 + 모든 댓글을 합쳐
분석 대상 텍스트 블록으로 반환한다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

import requests


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


@dataclass
class IssueBundle:
    number: int
    title: str
    url: str
    body: str
    comments: List[str] = field(default_factory=list)

    def full_text(self) -> str:
        """본문 + 댓글을 하나의 분석 텍스트로 합친다."""
        blocks = [f"# ISSUE #{self.number}: {self.title}", self.body or ""]
        for i, c in enumerate(self.comments, 1):
            blocks.append(f"\n--- COMMENT {i} ---\n{c}")
        return "\n".join(blocks)


def fetch_issues(
    owner: str,
    repo: str,
    label: str,
    *,
    token: str = "",
    state: str = "all",
    limit: int = 5,
) -> List[IssueBundle]:
    """label 로 이슈를 찾아 본문+댓글을 채운 IssueBundle 목록을 반환한다."""
    token = token or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN 환경변수가 필요합니다.")

    base = f"https://api.github.com/repos/{owner}/{repo}/issues"
    r = requests.get(
        base,
        headers=_headers(token),
        params={"state": state, "labels": label, "per_page": limit, "sort": "updated"},
        timeout=30,
    )
    r.raise_for_status()

    bundles: List[IssueBundle] = []
    for it in r.json():
        if "pull_request" in it:  # PR 제외
            continue
        b = IssueBundle(
            number=int(it["number"]),
            title=it.get("title", ""),
            url=it.get("html_url", ""),
            body=it.get("body") or "",
        )
        # 댓글 수집
        cr = requests.get(
            it["comments_url"], headers=_headers(token), params={"per_page": 100}, timeout=30
        )
        cr.raise_for_status()
        b.comments = [c.get("body") or "" for c in cr.json()]
        bundles.append(b)
    return bundles
