# AI Litigation Dashboard — GitHub Pages 정적 배포

이 폴더(`docs/`)는 **개인 서버(Ubuntu) 없이 GitHub 인프라만으로** AI 소송 대시보드를
호스팅하기 위한 정적 사이트입니다.

- **배포 주소**: <https://aigovsensing.github.io/ai-suit-sensing/>
- **빌드/배포**: GitHub Actions 워크플로 [`.github/workflows/pages.yml`](../.github/workflows/pages.yml)
- **빌드 스크립트**: [`dashboard/scripts/build_pages.py`](../dashboard/scripts/build_pages.py)

> ⚠️ 이 폴더의 대부분은 **빌드 산출물(자동 생성)** 입니다. 직접 수정하지 말고,
> 원본(`dashboard/frontend/`, `dashboard/data/` 등)을 고친 뒤 다시 빌드하세요.

---

## 법적 리스크 데이터셋 게시판

홈 화면 최상단의 **AI 소송 사건에 연관된 데이터셋 현황**은
`tracker/data/risky-open-datasets.csv`를 빌드한 `api/risky-open-datasets.json`을 읽습니다.
수집기는 데이터셋 이름을 대소문자 구분 없이 하나의 행으로 유지하면서 새로운 연관 소송,
확인 근거와 출처 URL만 누적합니다. 게시판은 기본 10개씩 표시하며 5·10·20·30·50·70·100개
보기와 데이터셋명·소송명·근거 통합 검색을 지원합니다. 게시판과 동일한 내용을
[`data/risky-open-datasets.csv`](./data/risky-open-datasets.csv)에서 내려받을 수 있으며,
수집 워크플로가 카탈로그를 갱신하면 Pages 배포도 자동으로 실행됩니다.

---

## 어떻게 백엔드 없이 동작하나요?

원본 대시보드는 FastAPI 백엔드의 `/api/*` 엔드포인트를 호출합니다. 그런데 이 API들은
대부분 **`data/*.csv` 를 가공해서 돌려주는 읽기 전용** 응답입니다. 그래서 빌드 시점에
이 응답들을 **미리 계산해 정적 JSON 파일**로 만들어 둡니다.

| 원래 API (백엔드) | 정적 파일 (Pages) |
| --- | --- |
| `GET /api/files` | `api/files.json` |
| `GET /api/cases?file_name=<f>` | `api/cases/<f>.json` |
| `GET /api/statistics?file_name=<f>` | `api/statistics/<f>.json` |
| `GET /api/version` | `api/version.json` |
| `POST /api/report/generate` | `api/report/<type>/<month>.json` (빌드 시 Gemini 사전 생성) |

브라우저에서는 [`js/pages-shim.js`](./js/pages-shim.js) 가 `window.fetch` 를 감싸서
`/api/*` 요청과 절대경로(`/img`, `/timeline` …) 요청을 위 정적 파일의 **상대경로**로
투명하게 바꿔치기합니다. 덕분에 프론트엔드 코드를 거의 손대지 않고, 사용자/조직 페이지든
프로젝트 하위 경로(`/ai-suit-sensing/`)든 동일하게 동작합니다.

### 페이지 구성
| 파일 | 설명 | 원본 |
| --- | --- | --- |
| `index.html` | 메인 현황판(첫 화면) | `frontend/overview.html` |
| `map.html` | 인터랙티브 소송 히트맵 | `frontend/index.html` |
| `lineage.html` | 소송 관계 리니지 그래프 | `frontend/lineage.html` |
| `timeline/` | 소송/규제 타임라인 | `dashboard/timeline/` |

## 🤖 AI 월간 보고서 (Gemini) — 사전 생성 방식

원래 이 기능은 서버가 실행 중에 Gemini API 를 호출합니다. 정적 사이트에는 실행 서버가
없으므로, **빌드 시점(GitHub Actions)에 Gemini 로 보고서를 미리 생성**해 정적 파일로
제공합니다. 런타임에는 백엔드 없이 그 파일을 받아 표시합니다.

- 워크플로 [`pages.yml`](../.github/workflows/pages.yml) 이 저장소 시크릿
  **`GEMINI_API_KEY`** (이미 `lawsuit-monitor` 에서 쓰던 것)로
  [`dashboard/scripts/generate_reports.py`](../dashboard/scripts/generate_reports.py) 를 실행합니다.
- **최신 데이터셋**의 각 유형(`filing_date`, `last_update`)에 대해 **데이터가 있는 최근 N개월**
  (`REPORT_MAX_MONTHS`, 기본 24)을 생성 → `api/report/<type>/<month>.json`.
- **캐시**: 입력(해당 월 데이터)이 바뀌지 않으면 재호출하지 않습니다(`manifest.json` + Actions 캐시).
  즉 최초 1회만 비용이 크고, 이후에는 새/변경 월만 생성합니다.
- 키가 없으면(포크 등) 스크립트는 조용히 건너뛰고, 프론트엔드는 안내 메시지를 표시합니다.
- 프롬프트/폴백 로직은 백엔드 `backend/main.py` 와 동일합니다.

**제약**: 데이터에 없는 월, 사전 생성 범위(최근 N개월) 밖의 월, 또는 최신이 아닌 데이터셋에
대한 보고서는 정적 배포에 없을 수 있습니다. 그런 경우 임의 월 즉석 생성이 필요하면 백엔드를
직접 실행하세요 (`dashboard/README.md` 4.1/4.2 참고).

## ✅ 그 밖에 되는 것 / 보안 주의

**됩니다** — 지도 히트맵·대륙별 줌인·다차원 필터링, 통계/시계열 차트, 리니지 그래프,
타임라인, 데이터셋 드롭다운(과거 스냅샷 전환), KO/EN 전환, 매뉴얼 열람.

**보안** — 정적 사이트는 공개 배포이며 간이 **로그인 게이트가 없습니다**. 민감 데이터라면
GitHub Pages 자체를 비공개로 두거나, 로컬/도커 백엔드 운영을 사용하세요. (`GEMINI_API_KEY`
는 Actions 시크릿에만 있고, 생성된 보고서 텍스트만 정적으로 배포되므로 키는 노출되지 않습니다.)

---

## GitHub Pages 활성화 (최초 1회)

레포 **Settings → Pages** 에서 다음 중 하나를 선택합니다.

1. **(권장) GitHub Actions**
   `Build and deployment → Source` 를 **GitHub Actions** 로 설정합니다.
   이후 `main` 에 push 되면 [`pages.yml`](../.github/workflows/pages.yml) 이
   `docs/` 를 새로 빌드해 자동 배포합니다. (레포에 커밋된 `docs/` 는 빌드 입력 스냅샷일 뿐)

2. **Deploy from a branch**
   `Source → Deploy from a branch`, 브랜치 `main` / 폴더 `/docs` 를 선택합니다.
   이 경우 커밋된 `docs/` 가 그대로 서빙됩니다(Actions 불필요).

두 방식 모두 최종 주소는 <https://aigovsensing.github.io/ai-suit-sensing/> 입니다.

## 데이터 갱신 후 다시 빌드

`dashboard/data/` 에 새 CSV(`aisuit_YYYYMMDD_HHMM.csv`)가 추가/변경되면 사이트를
다시 빌드해야 최신 데이터가 반영됩니다.

```bash
pip install pandas
python dashboard/scripts/build_pages.py   # docs/ 재생성
```

- **Actions 방식**: 위 경로가 바뀐 채로 `main` 에 push 하면 워크플로가 자동 재빌드/배포.
- **branch 방식**: 재빌드된 `docs/` 를 커밋/push.
