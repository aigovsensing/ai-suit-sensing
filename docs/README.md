# AI Litigation Dashboard — GitHub Pages 정적 배포

이 폴더(`docs/`)는 **개인 서버(Ubuntu) 없이 GitHub 인프라만으로** AI 소송 대시보드를
호스팅하기 위한 정적 사이트입니다.

- **배포 주소**: <https://aigovsensing.github.io/ai-suit-sensing/>
- **빌드/배포**: GitHub Actions 워크플로 [`.github/workflows/pages.yml`](../.github/workflows/pages.yml)
- **빌드 스크립트**: [`dashboard/scripts/build_pages.py`](../dashboard/scripts/build_pages.py)

> ⚠️ 이 폴더의 대부분은 **빌드 산출물(자동 생성)** 입니다. 직접 수정하지 말고,
> 원본(`dashboard/frontend/`, `dashboard/data/` 등)을 고친 뒤 다시 빌드하세요.

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

## ✅ 정적 배포에서 되는 것 / ❌ 안 되는 것

**됩니다** — 지도 히트맵·대륙별 줌인·다차원 필터링, 통계/시계열 차트, 리니지 그래프,
타임라인, 데이터셋 드롭다운(과거 스냅샷 전환), KO/EN 전환, 매뉴얼 열람.

**안 됩니다** — **AI 월간 보고서 생성(`/api/report/generate`)**. 이 기능만은 서버와
Google Gemini API 키가 필요해 정적 호스팅에서 실행할 수 없습니다. 정적 배포에서는 해당
버튼을 누르면 안내 메시지가 표시됩니다. 보고서가 필요하면 백엔드를 직접 실행하세요
(`dashboard/README.md` 참고). 또한 간이 **로그인 게이트도 없습니다** — 정적 사이트는
공개 배포이므로 GitHub Pages 자체를 비공개로 두거나 민감 데이터를 올리지 마세요.

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
