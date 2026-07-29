/*
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
 *  /api/report/generate (POST)      -> api/report/<type>/<month>.json (빌드 시 Gemini 사전생성)
 *                                      없으면 안내 메시지
 *  /img/... , /timeline/... 등 절대경로 -> 상대경로(GitHub Pages 하위경로 대응)
 *
 * 모든 경로는 현재 페이지 기준 상대경로로 변환되므로, 사용자/조직 페이지(루트)
 * 와 프로젝트 페이지(/<repo>/) 어디에 배포되든 동일하게 동작한다.
 */
(function () {
  "use strict";
  var origFetch = window.fetch.bind(window);

  function reportUnavailableNotice(month, type) {
    return [
      "### 🛈 이 달의 AI 보고서가 아직 없습니다",
      "",
      "선택하신 **" + (month || "해당 월") + "** (" + (type || "") + ") 보고서가 정적 사이트에",
      "미리 생성돼 있지 않습니다.",
      "",
      "정적 배포(GitHub Pages)에서는 보고서를 **빌드 시점에 GitHub Actions 가 Gemini 로 미리 생성**해",
      "정적 파일로 제공합니다. 최신 데이터셋의 최근 개월분만 사전 생성되므로, 데이터에 없는 월이거나",
      "아직 빌드에 포함되지 않은 월은 표시되지 않습니다.",
      "",
      "**해결 방법**",
      "- 데이터가 있는 최근 월을 선택해 보세요.",
      "- 저장소 관리자라면 `main` 에 데이터를 push 하거나 Actions 에서 `deploy-dashboard-pages`",
      "  워크플로를 다시 실행하면 최신 월 보고서가 생성됩니다 (`GEMINI_API_KEY` 시크릿 필요).",
      "- 임의의 월을 즉석에서 생성하려면 백엔드를 직접 실행하세요:",
      "  `cd dashboard && GEMINI_API_KEY=\"<key>\" uvicorn backend.main:app --port 8007`",
    ].join("\n");
  }

  function jsonResponse(obj, status) {
    return new Response(JSON.stringify(obj), {
      status: status || 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 루트-절대경로(/로 시작)만 정적 파일 상대경로로 변환한다. null 반환 시 원본 그대로 사용.
  //
  // 중요: 이미 올바른 "상대경로"(예: manual/user_guide.md)는 절대 건드리지 않는다.
  //   브라우저가 현재 페이지 기준으로 알아서 해석하며(→ /<repo>/manual/...),
  //   여기서 다시 베이스를 붙이면 /<repo>/<repo>/manual/... 처럼 이중 접두가 되어 404 난다.
  //   그래서 raw 문자열이 단일 '/'로 시작할 때만(=루트-절대) 재배치한다.
  function rewrite(rawUrl) {
    if (typeof rawUrl !== "string") return null;
    // 외부 URL(스킴 포함 http:, //host), 상대경로(manual/…, ./, ../)는 그대로 둔다.
    if (rawUrl.charAt(0) !== "/" || rawUrl.charAt(1) === "/") return null;

    // 페이지가 위치한 디렉토리(배포 베이스). 예: /ai-suit-sensing/map.html -> /ai-suit-sensing/
    var baseDir = window.location.pathname.replace(/[^/]*$/, "");

    var path, search;
    try {
      var u = new URL(rawUrl, window.location.origin);
      path = u.pathname;         // 예: /api/cases
      search = u.searchParams;
    } catch (e) {
      return null;
    }

    function fileParam() {
      var f = search.get("file_name");
      return f ? encodeURIComponent(f) : null;
    }

    // /api/* 매핑
    if (path.indexOf("/api/") === 0) {
      if (path.indexOf("/api/files") === 0) return baseDir + "api/files.json";
      if (path.indexOf("/api/version") === 0) return baseDir + "api/version.json";
      if (path.indexOf("/api/cases") === 0) {
        var cf = fileParam();
        return baseDir + (cf ? "api/cases/" + cf + ".json" : "api/cases.json");
      }
      if (path.indexOf("/api/statistics") === 0) {
        var sf = fileParam();
        return baseDir + (sf ? "api/statistics/" + sf + ".json" : "api/statistics.json");
      }
      // 그 외 /api/* 는 정적으로 제공 불가 → null(원본 유지, 자연스러운 실패)
      return null;
    }

    // 기타 루트-절대 정적 자산(/img, /timeline, /css, /js, /assets, /manual ...) → 베이스 기준 상대
    return baseDir + path.replace(/^\//, "") + (u.search || "");
  }

  var baseDir = window.location.pathname.replace(/[^/]*$/, "");

  // 보고서 요청 → 사전 생성된 정적 파일(api/report/<type>/<month>.json) 서빙
  function handleReport(init) {
    var type = "", month = "";
    try {
      var body = init && init.body ? JSON.parse(init.body) : {};
      type = body.type || "";
      month = body.month || "";
    } catch (e) { /* 무시 */ }

    if (!type || !month) {
      return Promise.resolve(jsonResponse({ report: reportUnavailableNotice(month, type) }, 200));
    }
    var target = baseDir + "api/report/" + encodeURIComponent(type) + "/" + encodeURIComponent(month) + ".json";
    return origFetch(target)
      .then(function (res) {
        if (res.ok) return res; // {report: "..."} 형태의 정적 파일
        return jsonResponse({ report: reportUnavailableNotice(month, type) }, 200);
      })
      .catch(function () {
        return jsonResponse({ report: reportUnavailableNotice(month, type) }, 200);
      });
  }

  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : (input && input.url) || "";

    // 보고서 생성(POST)은 사전 생성된 정적 보고서로 대체
    if (url.indexOf("/api/report/generate") !== -1) {
      return handleReport(init);
    }

    if (typeof input === "string") {
      var mapped = rewrite(input);
      if (mapped !== null) return origFetch(mapped, init);
    }
    return origFetch(input, init);
  };

  console.info("%c[pages-shim] 정적 배포 어댑터 활성화 — /api/* → 정적 JSON", "color:#3b82f6");
})();
