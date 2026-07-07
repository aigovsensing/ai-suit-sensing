# AI Litigation Dashboard (v1.5)

**AI Litigation Dashboard**는 인공지능(AI)과 관련된 글로벌 소송 데이터를 실시간으로 수집하고, 이를 지리적/통계적으로 시각화하는 전문 분석 플랫폼입니다. 법적 리스크와 트렌드를 데이터 기반으로 추적할 수 있도록 설계되었습니다.

---

## 1. 프로젝트 개요 (Project Overview)
본 프로젝트는 단순히 정적인 정보를 보여주는 것을 넘어, 최신 소송 데이터를 API로부터 실시간 빌드하거나 기존 축적된 데이터(CSV)를 선택하여 상호작용 가능한 대시보드를 제공합니다. 인공지능 기술의 급격한 발전과 함께 전 세계적으로 급증하는 법적 분쟁을 통합적으로 관리하는 데 최적화되어 있습니다.

## 2. 주요 기능 및 강점 (Key Features & Strengths)
### 2.1 지능형 분석 및 리니지 그래프
*   **인터랙티브 리니지 그래프 (Lineage Graph)**: 원고, 피고, 데이터셋, AI 제품 간의 복잡한 관계를 시각화하고, 특정 대상을 포커싱하여 분석할 수 있는 고급 시각화 기능을 제공합니다.
*   **Gemini AI 기반 월간 보고서**: 소송 데이터를 바탕으로 전문적인 법적 트렌드 보고서(Executive Summary, 기업 영향 분석 포함)를 자동으로 생성합니다.
*   **대화형 통계 및 시기별 추이**: 청구 내용, 피고, 판결 결과, 대상 데이터별 실시간 집계뿐만 아니라 **시계열 소송 트렌드(Trend Analysis)** 차트를 제공합니다.

### 2.2 인터랙티브 소송 히트맵 & 내비게이션
*   **대륙별 줌인 (Continental Zoom)**: 전 세계 지도를 대륙별(AMERICAS, EUROPE, ASIA PACIFIC 등) 영역으로 즉시 확대하여 국가별 상세 데이터를 확인할 수 있습니다.
*   **고급 다차원 필터링**: 진행 상태뿐만 아니라 **피고(Defendant)** 및 **학습 데이터 분야(Theme)**별로 정밀한 데이터 필터링이 가능합니다.
*   **실시간 티커 (Live Tickers)**: 최신 소송 건과 뉴스 정보를 실시간으로 스크롤하여 보여주며, 사용자가 직접 표시 여부 및 노출 개수를 제어할 수 있습니다.
*   **자동 시각화 (Auto-Visualizer)**: 앱 실행 시 가장 최근의 데이터셋을 자동으로 감지하여 지도를 즉시 렌더링합니다.

### 2.3 사용자 편의성 (UX/UI)
*   **다국어 지원 (KO/EN Localization)**: 한국어와 영어 모드를 자유롭게 전환할 수 있으며, 모든 UI 요소와 데이터 라벨이 실시간으로 현지화됩니다.
*   **빌드 버전 정보 (Build Versioning)**: 로고 마우스 오버 시 현재 배포된 앱의 Git 태그 및 커밋 정보를 실시간으로 확인할 수 있습니다.
*   **반응형 디자인**: 데스크탑뿐만 아니라 스마트폰 모바일 환경에서도 최적화된 레이아웃과 가독성을 제공합니다.
*   **지능형 가이드 및 복구**: 첫 방문 사용자를 위한 자동 가이드와 함께, 숨겨진 티커 설정을 언제든 되돌릴 수 있는 '표시 설정 초기화' 기능을 지원합니다.

## 3. 기술 스택 및 구조 (Tech Stack & Structure)
### 3.1 기술 스택
- **Backend**: FastAPI (Python 3.10+), Uvicorn
- **Database**: MariaDB 10.6 (or SQLite fallback)
- **Frontend**: Vanilla JS, React 18 (Lineage UI), Cytoscape.js, CSS3 (Glassmorphism)
- **AI**: Google Gemini Pro API (Report Generation)
- **Containerization**: Docker, Docker-compose

### 3.2 프로젝트 구조
```bash
/work/github-aigovsensing/ai-suit-dashboard/
├── backend/            # FastAPI 라우터 및 비즈니스 로직
├── collector/          # 데이터 수집 및 정제 (ELT)
├── data/               # 소송 데이터셋 (CSV 형식) 저장소
├── manual/             # API 가이드 및 사용자 매뉴얼
├── frontend/           # 대시보드 UI (JS, React, HTML)
├── img/                # 벡터 맵(SVG) 및 데모 이미지
└── scripts/            # 유틸리티 및 데이터 변환 스크립트
```

## 4. 시작하기 (Getting Started)
### 4.1 Docker를 사용한 실행 (권장)
```bash
# Docker Compose 실행
docker-compose -f docker/docker-compose.yml up -d

# API Key를 포함하여 실행 시
GEMINI_API_KEY="your_actual_api_key" docker-compose -f docker/docker-compose.yml up -d
```
*   **접속 주소**: `http://localhost:8007`

#### 🔐 접속 암호 (로그인)
외부에 노출된 대시보드에 아무나 접속하지 못하도록 간이 로그인 게이트가 적용되어 있습니다.
첫 접속 시 로그인 페이지(`/login`)로 이동하며, 암호 입력 후 7일간 세션이 유지됩니다.

*   **기본 암호**: `guest2848`
*   **암호 변경**: `DASHBOARD_PASSWORD` 환경변수로 설정합니다.
    ```bash
    DASHBOARD_PASSWORD="my_secret" GEMINI_API_KEY="your_actual_api_key" docker-compose -f docker/docker-compose.yml up -d
    ```
*   **로그아웃**: `http://localhost:8007/logout`

> [!NOTE]
> 공용 계정 하나로 쓰는 최소한의 접근 제한입니다. 민감 데이터를 다루게 되면 HTTPS(리버스 프록시)와 개별 계정 인증 도입을 권장합니다.

#### ⚠️ Troubleshooting: docker-compose client version error
실행 시 `client version 1.43 is too old. Minimum supported API version is 1.44` 오류가 발생한다면, 구형 `docker-compose` 바이너리를 최신 버전으로 업데이트해야 합니다. (Docker Engine v29.1.3 이상은 API 1.44를 요구하지만, 구형 `docker-compose`는 API 1.43까지만 지원하기 때문에 발생하는 문제입니다.)

아래 명령어로 로컬 환경(`~/bin`)에 최신 버전을 다운로드하여 해결할 수 있습니다:

```bash
# 로컬 바이너리 디렉토리에 최신 버전 다운로드 및 실행 권한 부여
mkdir -p ~/bin
curl -SL https://github.com/docker/compose/releases/download/v5.1.3/docker-compose-linux-x86_64 -o ~/bin/docker-compose
chmod +x ~/bin/docker-compose

# 쉘 명령어 경로 캐시 초기화
hash -r
```

**(Optional)** If you want to update the system-wide binary so the fix applies permanently for all users, you can overwrite the old installation using `sudo`:
```bash
sudo mv ~/bin/docker-compose /usr/local/bin/docker-compose
```

### 4.2 로컬 개발 환경에서 실행
```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 서버 실행
uvicorn backend.main:app --host 0.0.0.0 --port 8007 --reload
```

## 5. 사용 가이드 (How to Use)
1.  **데이터셋 선택**: 헤더의 `DATASET` 드롭다운에서 파일을 선택합니다. (최신 파일 자동 선택)
2.  **대륙별 상세 분석**: 우측 하단의 `대륙별줌인` 메뉴를 통해 특정 지역으로 즉시 이동합니다.
3.  **리니지 분석**: **[리니지 (Lineage)]** 버튼을 클릭하여 소송 관계망 그래프를 분석합니다.
4.  **검색 및 필터**: 피고별, 대상 데이터별 검색 창을 활용하여 정밀 분석을 수행합니다.
5.  **통계 및 보고서**: 상단의 **[STATISTICS]**와 **[REPORT]** 버튼을 통해 데이터 인사이트를 도출합니다.

## 6. 데모 스크린샷 (Demo Screenshots)
| 메인 대시보드 및 히트맵 | 소송 관계 리니지 그래프 | 통계 분석 및 AI 보고서 |
| :---: | :---: | :---: |
| ![Dashboard](./img/dashboard.png) | ![Lineage](./img/lineage.png) | ![Statistics](./img/api_docs.png) |

## 7. 데이터 관리 및 유지보수
### 7.1 데이터 포맷 (CSV v2.1)
*   `aisuit_YYYYMMDD_HHMM.csv` 형식을 사용하며, 데이터 폴더에 저장 시 자동으로 인식됩니다.
*   다중 피고(Multiple Defendants) 지원: 콤마(`,`)로 구분된 피고 데이터를 개별적으로 집계합니다.

### 7.2 메모리 프로파일 (Memory Profile)
| 소송 건수 | 평균 메모리 사용량 | 최대 메모리 점유율 | 비고 |
| :--- | :--- | :--- | :--- |
| 1,000건 | ~70 MB | ~90 MB | 표준 운영 수준 |
| 5,000건 | ~95 MB | ~130 MB | 대규모 분석 환경 |
| 10,000건 | ~120 MB | ~180 MB | 고부하 분석 환경 |

---
**AI Litigation Dashboard Team**
*For questions and issues, please use the issue tracker.*
