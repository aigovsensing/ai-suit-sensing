#!/usr/bin/env python3
"""
build_pages.py — AI Litigation Dashboard 정적 사이트 빌더 (GitHub Pages 용)

FastAPI 백엔드가 실시간으로 제공하던 읽기 전용 API 응답을 빌드 시점에
정적 JSON 파일로 미리 계산(pre-compute)하여, 백엔드 없이도 GitHub Pages에서
대시보드를 열람/조작할 수 있게 한다.

동작:
  1. dashboard/data/*.csv 를 읽어 각 파일별로
       docs/api/cases/<file>.json       (= /api/cases?file_name=<file>)
       docs/api/statistics/<file>.json  (= /api/statistics?file_name=<file>)
     를 생성한다. 최신 파일은 docs/api/cases.json / statistics.json 로도 복사.
  2. docs/api/files.json  (= /api/files)  : CSV 파일 목록(최신순)
  3. docs/api/version.json (= /api/version): git 태그/커밋/날짜
  4. frontend/ 을 docs/ 로 복사하되
       - overview.html -> docs/index.html (첫 화면)
       - index.html    -> docs/map.html   (지도 대시보드)
       - lineage.html  -> docs/lineage.html
     로 라우팅을 정적 파일명에 맞춘다.
  5. img/, timeline/, manual/ 등 정적 자산 복사.
  6. 각 HTML <head> 에 pages-shim.js 를 주입해 런타임에서 /api/* 와
     절대경로(/img, /timeline ...) fetch 를 정적 파일로 재매핑한다.
  7. 절대경로 네비게이션(href="/" 등)을 GitHub Pages 하위경로에서도 동작하도록
     상대경로로 치환한다.

사용:
    python dashboard/scripts/build_pages.py          # repo/docs 에 생성
    python dashboard/scripts/build_pages.py --out X   # 임의 경로에 생성
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(SCRIPT_DIR)          # .../dashboard
REPO_ROOT = os.path.dirname(DASHBOARD_DIR)           # repo root
DATA_DIR = os.path.join(DASHBOARD_DIR, "data")
FRONTEND_DIR = os.path.join(DASHBOARD_DIR, "frontend")
IMG_DIR = os.path.join(DASHBOARD_DIR, "img")
TIMELINE_DIR = os.path.join(DASHBOARD_DIR, "timeline")

# collector.builder(build_from_csv) 재사용 — pandas 만 있으면 동작한다.
sys.path.insert(0, DASHBOARD_DIR)
from collector.builder import build_from_csv  # noqa: E402
import pandas as pd  # noqa: E402


# ---------------------------------------------------------------------------
# 통계 계산 — backend/main.py 의 get_statistics 로직을 그대로 옮겨왔다.
# (backend.main 은 pymysql/genai/docx 를 import 하므로 직접 import 하지 않는다.)
# ---------------------------------------------------------------------------
def find_col_in_df(keys, df):
    for k in keys:
        for col in df.columns:
            if k.lower() == col.lower():
                return col
    for k in keys:
        for col in df.columns:
            if k.lower() in col.lower():
                if k == "피고" and "원고" in col:
                    continue
                if k == "원고" and "피고" in col:
                    continue
                return col
    return None


def _get_top_n(series, n=15, key_type=None):
    series = series.astype(str).str.strip()
    series = series[series.str.lower() != "unknown"]
    series = series[series != ""]
    case_count = len(series)

    if key_type == "defendant":
        series = series.str.split(',').explode().str.strip()

        def clean_def(name):
            return name.replace("et al.", "").replace("et al", "").strip()

        series = series.apply(clean_def)
        series = series[series != ""]

    if key_type == "target_data":
        def categorize_data(text):
            text = text.lower()
            mapping = {
                "Authors/Books": ["book", "text", "novel", "author", "책", "도서", "저서", "글", "문학", "작가"],
                "Music/Recordings": ["music", "audio", "song", "recording", "음악", "음원", "노래", "오디오", "가수"],
                "Visual Art": ["image", "art", "picture", "photo", "drawing", "painting", "이미지", "그림", "사진", "미술", "예술", "작품"],
                "Video/Film": ["video", "movie", "film", "youtube", "비디오", "영상", "영화", "유튜브"],
                "Voice/Likeness": ["voice", "face", "likeness", "biometric", "목소리", "얼굴", "초상", "음성"],
                "News": ["news", "article", "journalism", "뉴스", "기사", "언론"],
                "Publishers": ["publish", "publisher", "press", "출판", "신문사"],
                "Code/Software": ["code", "software", "programming", "github", "코드", "소프트웨어", "프로그래밍", "깃허브"],
            }
            for cat, keywords in mapping.items():
                if any(kw in text for kw in keywords):
                    return cat
            return "Other"

        series = series.apply(categorize_data)

    if key_type == "claim":
        def categorize_claim(text):
            text = text.lower()
            mapping = {
                "Direct copyright": ["direct", "copyright infringement", "저작권 침해", "복제", "무단 사용", "무단 수집"],
                "Vicarious infringement": ["vicarious", "대위"],
                "Contributory infringement": ["contributory", "기여", "방조"],
                "Inducement": ["inducement", "유도", "권장"],
                "DMCA": ["dmca", "digital millennium", "저작권 보호"],
                "Latham Act": ["latham", "lanham", "상표", "부정경쟁"],
                "Sate law claims": ["state law", "common law", "주법", "관습법", "불공정", "퍼블리시티"],
            }
            for cat, keywords in mapping.items():
                if any(kw in text for kw in keywords):
                    return cat
            return "기타"

        series = series.apply(categorize_claim)

    return series.value_counts().head(n).to_dict(), case_count


def compute_statistics(csv_path):
    df = pd.read_csv(csv_path, skiprows=2).fillna("")
    title_col = find_col_in_df(["소송제목 (원고 v. 피고)*", "소송제목 (원고 v. 피고)", "Case Name"], df)
    if title_col:
        df = df[df[title_col].astype(str).str.strip() != ""]

    col_mapping = {
        "claim": ["청구 내용", "Reason", "소송 사유", "Claim", "소송이유"],
        "defendant": ["피고", "Defendant", "피고*"],
        "country": ["국가", "Country", "국가*"],
        "decision": ["진행현황", "Status", "진행현황*", "Decision"],
        "target_data": ["대상 데이터", "Target Data", "대상 데이터*", "대상 데이타"],
    }
    stats = {}
    for key, keys in col_mapping.items():
        col = find_col_in_df(keys, df)
        if col:
            data_dict, total_count = _get_top_n(df[col], key_type=key)
            stats[key] = {"data": data_dict, "total": total_count}
        else:
            stats[key] = {"data": {}, "total": 0}
    return stats


def git_version():
    def run(args):
        return subprocess.check_output(args, cwd=REPO_ROOT, stderr=subprocess.STDOUT).decode().strip()

    try:
        try:
            version = run(["git", "tag", "--sort=-v:refname"]).split("\n")[0].strip()
            if not version:
                version = run(["git", "describe", "--tags", "--always"])
        except Exception:
            version = run(["git", "describe", "--tags", "--always"])
        commit = run(["git", "rev-parse", "HEAD"])
        env = os.environ.copy()
        env["LC_ALL"] = "C"
        date = subprocess.check_output(
            ["git", "show", "-s", "--format=%cd", "--date=format:%b %-d %H:%M:%S %Y", "HEAD"],
            cwd=REPO_ROOT, stderr=subprocess.STDOUT, env=env,
        ).decode().strip()
        return {"version": version or "unknown", "commit": commit, "date": date}
    except Exception as e:  # noqa: BLE001
        return {"version": f"static-build", "commit": "unknown", "date": str(e)[:40]}


# ---------------------------------------------------------------------------
# HTML/JS 변환
# ---------------------------------------------------------------------------
SHIM_TAG = '<script src="js/pages-shim.js"></script>'


def inject_shim(html):
    """<head> 안(가능한 앞쪽)에 pages-shim.js 를 넣어 다른 스크립트보다 먼저 실행."""
    if "js/pages-shim.js" in html:
        return html
    # <head ...> 바로 뒤에 삽입 (charset meta 보다 뒤여도 무방하나 다른 <script>보다 앞이어야 함)
    m = re.search(r"<head[^>]*>", html, flags=re.IGNORECASE)
    if m:
        idx = m.end()
        return html[:idx] + "\n    " + SHIM_TAG + html[idx:]
    # <head> 가 없으면 첫 <script> 앞에
    return re.sub(r"(<script)", SHIM_TAG + r"\n\1", html, count=1, flags=re.IGNORECASE)


def rewrite_nav_paths(text):
    """절대경로 네비게이션을 GitHub Pages 하위경로에서도 동작하도록 상대경로로."""
    replacements = [
        # 로고/홈 링크
        ('href="/"', 'href="index.html"'),
        ("href='/'", "href='index.html'"),
        ("location.href='/'", "location.href='index.html'"),
        ('location.href="/"', 'location.href="index.html"'),
        ("location.href = '/'", "location.href = 'index.html'"),
        ('location.href = "/"', 'location.href = "index.html"'),
        ("window.location.href = '/'", "window.location.href = 'index.html'"),
        ('window.location.href = "/"', 'window.location.href = "index.html"'),
        # 타임라인(절대 → 상대)
        ("'/timeline/", "'timeline/"),
        ('"/timeline/', '"timeline/'),
        # 지도 라우트: 백엔드는 /map.html 로 서빙했지만 정적 파일도 map.html 이므로 그대로 OK
    ]
    for a, b in replacements:
        text = text.replace(a, b)
    return text


def process_html(src_path, dst_path):
    with open(src_path, encoding="utf-8") as f:
        html = f.read()
    html = rewrite_nav_paths(html)
    html = inject_shim(html)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# pages-shim.js — 런타임 fetch 재매핑 스크립트 (정적 배포 전용)
# ---------------------------------------------------------------------------
PAGES_SHIM_JS = r"""/*
 * pages-shim.js — GitHub Pages 정적 배포 어댑터
 *
 * 원본 대시보드는 FastAPI 백엔드의 /api/* 엔드포인트를 fetch 한다.
 * 정적 호스팅(GitHub Pages)에는 백엔드가 없으므로, 빌드 시 미리 계산해 둔
 * 정적 JSON 파일로 fetch 요청을 투명하게 재매핑한다.
 *
 *  /api/files                       -> api/files.json
 *  /api/cases?file_name=<f>         -> api/cases/<f>.json
 *  /api/statistics?file_name=<f>    -> api/statistics/<f>.json
 *  /api/version                     -> api/version.json
 *  /api/report/generate (POST)      -> 정적 안내 메시지(백엔드 필요 기능)
 *  /img/... , /timeline/... 등 절대경로 -> 상대경로(GitHub Pages 하위경로 대응)
 *
 * 모든 경로는 현재 페이지 기준 상대경로로 변환되므로, 사용자/조직 페이지(루트)
 * 와 프로젝트 페이지(/<repo>/) 어디에 배포되든 동일하게 동작한다.
 */
(function () {
  "use strict";
  var origFetch = window.fetch.bind(window);

  var STATIC_REPORT_NOTICE = [
    "### 🛈 정적 배포 안내 (GitHub Pages)",
    "",
    "**AI 월간 보고서 생성**은 서버(백엔드)와 Google Gemini API 키가 필요한 기능이라,",
    "백엔드가 없는 GitHub Pages 정적 배포에서는 실행할 수 없습니다.",
    "",
    "이 대시보드의 **지도·통계·리니지·타임라인·데이터 열람/필터링**은 모두 정상 동작합니다.",
    "",
    "월간 보고서가 필요하면 아래 중 하나로 백엔드를 실행하세요:",
    "",
    "```bash",
    "GEMINI_API_KEY=\"<your_key>\" docker-compose -f dashboard/docker/docker-compose.yml up -d",
    "# 또는",
    "cd dashboard && uvicorn backend.main:app --port 8007",
    "```",
  ].join("\n");

  function jsonResponse(obj, status) {
    return new Response(JSON.stringify(obj), {
      status: status || 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 절대경로/‐API 경로를 정적 파일 상대경로로 변환. null 반환 시 원본 그대로 사용.
  function rewrite(rawUrl) {
    var path, search;
    try {
      var u = new URL(rawUrl, window.location.href);
      // 외부 오리진(CDN 등)은 건드리지 않는다.
      if (u.origin !== window.location.origin) return null;
      path = u.pathname;
      search = u.searchParams;
    } catch (e) {
      return null;
    }

    // 페이지가 위치한 디렉토리(배포 베이스). 예: /ai-suit-sensing/index.html -> /ai-suit-sensing/
    var baseDir = window.location.pathname.replace(/[^/]*$/, "");

    function fileParam() {
      var f = search.get("file_name");
      return f ? encodeURIComponent(f) : null;
    }

    // /api/* 매핑
    var apiIdx = path.indexOf("/api/");
    if (apiIdx !== -1) {
      var apiPath = path.slice(apiIdx); // "/api/..."
      if (apiPath.indexOf("/api/files") === 0) return baseDir + "api/files.json";
      if (apiPath.indexOf("/api/version") === 0) return baseDir + "api/version.json";
      if (apiPath.indexOf("/api/cases") === 0) {
        var cf = fileParam();
        return baseDir + (cf ? "api/cases/" + cf + ".json" : "api/cases.json");
      }
      if (apiPath.indexOf("/api/statistics") === 0) {
        var sf = fileParam();
        return baseDir + (sf ? "api/statistics/" + sf + ".json" : "api/statistics.json");
      }
      // 그 외 /api/* 는 정적으로 제공 불가 → null(원본 유지, 자연스러운 실패)
      return null;
    }

    // 절대경로 정적 자산(/img, /timeline, /css, /js, /assets, /manual ...) → 베이스 기준 상대
    if (path.charAt(0) === "/") {
      // 이미 베이스 디렉토리로 시작하면 그대로, 아니면 루트 기준 → 베이스로 이동
      var rel = path.replace(/^\//, "");
      return baseDir + rel;
    }
    return null;
  }

  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : (input && input.url) || "";
    var method = (init && init.method) || (input && input.method) || "GET";

    // 보고서 생성(POST)은 정적 안내로 대체
    if (url.indexOf("/api/report/generate") !== -1) {
      return Promise.resolve(jsonResponse({ report: STATIC_REPORT_NOTICE }, 200));
    }

    if (typeof input === "string") {
      var mapped = rewrite(input);
      if (mapped !== null) return origFetch(mapped, init);
    }
    return origFetch(input, init);
  };

  console.info("%c[pages-shim] 정적 배포 어댑터 활성화 — /api/* → 정적 JSON", "color:#3b82f6");
})();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "docs"))
    args = ap.parse_args()
    docs = os.path.abspath(args.out)

    print(f"[build] repo root : {REPO_ROOT}")
    print(f"[build] output    : {docs}")

    # 기존 산출물 정리(빌드가 전적으로 소유하는 디렉토리만 초기화).
    # img/ 는 다른 워크플로(lawsuit-monitor 의 daily_visual_report.png 등)가
    # 함께 쓸 수 있으므로 통째로 지우지 않고 병합 복사한다.
    for sub in ["api", "css", "js", "assets", "manual", "timeline"]:
        p = os.path.join(docs, sub)
        if os.path.isdir(p):
            shutil.rmtree(p)
    os.makedirs(docs, exist_ok=True)

    # 1) 정적 자산 복사
    shutil.copytree(os.path.join(FRONTEND_DIR, "css"), os.path.join(docs, "css"))
    shutil.copytree(os.path.join(FRONTEND_DIR, "js"), os.path.join(docs, "js"))
    if os.path.isdir(os.path.join(FRONTEND_DIR, "assets")):
        shutil.copytree(os.path.join(FRONTEND_DIR, "assets"), os.path.join(docs, "assets"))
    if os.path.isdir(os.path.join(FRONTEND_DIR, "manual")):
        shutil.copytree(os.path.join(FRONTEND_DIR, "manual"), os.path.join(docs, "manual"))
    if os.path.isdir(IMG_DIR):
        # 병합 복사: 기존 파일(타 워크플로 산출물)을 지우지 않고 덮어쓴다.
        shutil.copytree(IMG_DIR, os.path.join(docs, "img"), dirs_exist_ok=True)
    if os.path.isdir(TIMELINE_DIR):
        shutil.copytree(TIMELINE_DIR, os.path.join(docs, "timeline"))

    # app.js 등 JS 내부 절대경로 네비게이션 치환
    for root, _, filenames in os.walk(os.path.join(docs, "js")):
        for fn in filenames:
            if fn.endswith(".js"):
                fp = os.path.join(root, fn)
                with open(fp, encoding="utf-8") as f:
                    txt = f.read()
                new = rewrite_nav_paths(txt)
                if new != txt:
                    with open(fp, "w", encoding="utf-8") as f:
                        f.write(new)

    # pages-shim.js 기록
    with open(os.path.join(docs, "js", "pages-shim.js"), "w", encoding="utf-8") as f:
        f.write(PAGES_SHIM_JS)

    # timeline HTML 도 절대경로 치환(내부 링크 대비)
    for root, _, filenames in os.walk(os.path.join(docs, "timeline")):
        for fn in filenames:
            if fn.endswith(".html"):
                fp = os.path.join(root, fn)
                with open(fp, encoding="utf-8") as f:
                    txt = f.read()
                new = rewrite_nav_paths(txt)
                if new != txt:
                    with open(fp, "w", encoding="utf-8") as f:
                        f.write(new)

    # 2) HTML 라우팅: overview -> index, index -> map, lineage 그대로
    process_html(os.path.join(FRONTEND_DIR, "overview.html"), os.path.join(docs, "index.html"))
    process_html(os.path.join(FRONTEND_DIR, "index.html"), os.path.join(docs, "map.html"))
    process_html(os.path.join(FRONTEND_DIR, "lineage.html"), os.path.join(docs, "lineage.html"))

    # 3) API JSON pre-compute
    api_dir = os.path.join(docs, "api")
    os.makedirs(os.path.join(api_dir, "cases"), exist_ok=True)
    os.makedirs(os.path.join(api_dir, "statistics"), exist_ok=True)

    csv_files = sorted(
        [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")], reverse=True
    ) if os.path.isdir(DATA_DIR) else []

    with open(os.path.join(api_dir, "files.json"), "w", encoding="utf-8") as f:
        json.dump(csv_files, f, ensure_ascii=False)

    with open(os.path.join(api_dir, "version.json"), "w", encoding="utf-8") as f:
        json.dump(git_version(), f, ensure_ascii=False)

    for i, fn in enumerate(csv_files):
        csv_path = os.path.join(DATA_DIR, fn)
        print(f"[build] ({i + 1}/{len(csv_files)}) {fn}")
        # cases
        try:
            data = build_from_csv(csv_path)
        except Exception as e:  # noqa: BLE001
            print(f"        ! cases 실패: {e}")
            data = []
        cases_obj = {"source": "csv", "file": fn, "count": len(data), "data": data}
        with open(os.path.join(api_dir, "cases", fn + ".json"), "w", encoding="utf-8") as f:
            json.dump(cases_obj, f, ensure_ascii=False)
        # statistics
        try:
            stats = compute_statistics(csv_path)
        except Exception as e:  # noqa: BLE001
            print(f"        ! statistics 실패: {e}")
            stats = {}
        with open(os.path.join(api_dir, "statistics", fn + ".json"), "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False)

        # 최신 파일은 default 로도 복사
        if i == 0:
            with open(os.path.join(api_dir, "cases.json"), "w", encoding="utf-8") as f:
                json.dump(cases_obj, f, ensure_ascii=False)
            with open(os.path.join(api_dir, "statistics.json"), "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False)

    # 4) Jekyll 우회(폴더/파일명이 _ 로 시작하는 경우 대비) + 빌드 표식
    open(os.path.join(docs, ".nojekyll"), "w").close()

    print(f"[build] 완료: {len(csv_files)}개 데이터셋, index.html/map.html/lineage.html 생성")


if __name__ == "__main__":
    main()
