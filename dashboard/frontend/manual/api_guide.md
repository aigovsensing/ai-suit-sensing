# AI Litigation Dashboard API 가이드
**현재 버전**: `{{APP_VERSION}}` (Commit: `{{COMMIT_HASH}}`, `{{COMMIT_DATE}}`)

이 문서는 AI Litigation Dashboard에서 제공하는 REST API 엔드포인트에 대한 기술적인 세부 정보를 제공합니다.

## 기본 URL (Base URL)
API의 기본 접속 주소는 다음과 같습니다:
`http://localhost:8007`

---

## 1. 데이터 조회 엔드포인트 (Data Retrieval)

### 1.1 사용 가능한 파일 목록 조회
`./data` 디렉토리에 있는 CSV 데이터셋 목록을 반환합니다. 이름 내림차순(최신순)으로 정렬됩니다.

*   **URL**: `/api/files`
*   **Method**: `GET`
*   **응답**: `List[str]` (파일명 배열)
*   **예시**: `["aisuit_20260429_1700.csv", "aisuit_20260414.csv"]`

### 1.2 소송 사건 데이터 페치
소송 데이터를 가져오는 메인 엔드포인트입니다. 특정 CSV 파일을 로드하거나 CourtListener API에서 실시간 데이터를 가져올 수 있습니다.

*   **URL**: `/api/cases`
*   **Method**: `GET`
*   **파라미터**:
    *   `file_name` (선택): `./data/` 디렉토리 내의 특정 CSV 파일명.
*   **응답**: `dict`
    *   `source`: "csv" 또는 "api"
    *   `file`: 파일명 (CSV인 경우)
    *   `count`: 사건 수
    *   `data`: 사건 객체 리스트
*   **예시**: `/api/cases?file_name=aisuit_20260429_1700.csv`

### 1.3 데이터베이스 데이터 조회 (Legacy)
MariaDB 데이터베이스에서 직접 소송 데이터를 가져옵니다.

*   **URL**: `/api/db-cases`
*   **Method**: `GET`
*   **응답**: DB의 사건 목록을 포함한 `dict`.

### 1.4 시스템 버전 정보 조회
현재 실행 중인 애플리케이션의 Git Tag와 Commit Hash 정보를 반환합니다.

*   **URL**: `/api/version`
*   **Method**: `GET`
*   **응답**: `{"version": "tag_name", "commit": "full_hash", "date": "commit_date"}`
*   **예시**: `{"version": "ver.20260503", "commit": "721404f9...", "date": "May 3 19:14:33 2026"}`

---

## 2. 분석 및 통계 엔드포인트 (Analysis & Statistics)

### 2.1 통계 데이터 조회
대시보드 시각화(청구항, 피고, 국가, 상태 등)를 위한 집계된 통계 데이터를 반환합니다.

*   **URL**: `/api/statistics`
*   **Method**: `GET`
*   **파라미터**:
    *   `file_name` (선택): 분석할 CSV 파일명.
*   **응답**: 카테고리별 건수와 합계를 포함한 `dict`.

---

## 3. 보고서 생성 엔드포인트 (Report Generation)

### 3.1 월간 보고서 생성
Gemini AI를 사용하여 전문적인 월간 동향 보고서를 생성합니다.

*   **URL**: `/api/report/generate`
*   **Method**: `POST`
*   **페이로드 (JSON)**:
    ```json
    {
      "type": "filing_date" | "last_update",
      "month": "YYYY-MM",
      "file_name": "filename.csv" (선택)
    }
    ```
*   **응답**: `{"report": "마크다운 형식의 보고서 내용"}`

### 3.2 보고서 다운로드 (DOCX)
마크다운 형식의 보고서 내용을 워드(`.docx`) 파일로 변환하여 다운로드합니다.

*   **URL**: `/api/report/download`
*   **Method**: `POST`
*   **페이로드 (JSON)**:
    ```json
    {
      "content": "마크다운 텍스트...",
      "title": "보고서 제목"
    }
    ```
*   **응답**: Word 문서의 바이너리 스트림.

---

## 4. 정적 파일 및 UI 경로
*   `/`: 메인 대시보드 (index.html)
*   `/css/*`: 스타일시트
*   `/js/*`: 자바스크립트 파일
*   `/assets/*`: 아이콘 및 정적 자산
*   `/img/*`: SVG 지도 및 데모 이미지
*   `/manual/*`: 문서 파일 (본 가이드 포함)
