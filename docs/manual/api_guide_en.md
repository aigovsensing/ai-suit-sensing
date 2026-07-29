# AI Litigation Dashboard API Guide
**Current Version**: `{{APP_VERSION}}` (Commit: `{{COMMIT_HASH}}`, `{{COMMIT_DATE}}`)

This document provides technical details for the REST API endpoints available in the AI Litigation Dashboard.

## Base URL
The default base URL for the API is:
`http://localhost:8007`

---

## 1. Data Retrieval Endpoints

### 1.1 List Available Files
Returns a list of available CSV datasets in the `./data` directory, sorted by name descending (latest first).

*   **URL**: `/api/files`
*   **Method**: `GET`
*   **Response**: `List[str]` (Array of filenames)
*   **Example**: `["aisuit_20260429_1700.csv", "aisuit_20260414.csv"]`

### 1.2 Fetch Cases
The main endpoint to fetch litigation data. It can load a specific CSV file or fetch real-time data from the CourtListener API.

*   **URL**: `/api/cases`
*   **Method**: `GET`
*   **Parameters**:
    *   `file_name` (optional): Name of a specific CSV file in the `./data/` directory.
*   **Response**: `dict`
    *   `source`: "csv" or "api"
    *   `file`: Filename (if CSV)
    *   `count`: Number of cases
    *   `data`: List of case objects
*   **Example**: `/api/cases?file_name=aisuit_20260429_1700.csv`

### 1.3 Fetch Database Data (Legacy)
Fetches litigation data directly from the MariaDB database.

*   **URL**: `/api/db-cases`
*   **Method**: `GET`
*   **Response**: `dict` containing the list of cases from the DB.

### 1.4 System Version Information
Returns the Git Tag and Commit Hash information of the currently running application.

*   **URL**: `/api/version`
*   **Method**: `GET`
*   **Response**: `{"version": "tag_name", "commit": "full_hash", "date": "commit_date"}`
*   **Example**: `{"version": "ver.20260503", "commit": "721404f9...", "date": "May 3 19:14:33 2026"}`

---

## 2. Analysis & Statistics Endpoints

### 2.1 Get Statistics
Returns aggregated statistics for dashboard visualization (claims, defendants, countries, status, etc.).

*   **URL**: `/api/statistics`
*   **Method**: `GET`
*   **Parameters**:
    *   `file_name` (optional): Name of the CSV file to analyze.
*   **Response**: `dict` containing categorized counts and totals.

---

## 3. Report Generation Endpoints

### 3.1 Generate Monthly Report
Triggers AI analysis using Gemini to generate a professional monthly trend report.

*   **URL**: `/api/report/generate`
*   **Method**: `POST`
*   **Payload (JSON)**:
    ```json
    {
      "type": "filing_date" | "last_update",
      "month": "YYYY-MM",
      "file_name": "filename.csv" (optional)
    }
    ```
*   **Response**: `{"report": "Report content in Markdown format"}`

### 3.2 Download Report (DOCX)
Converts Markdown report content into a Word (`.docx`) file for download.

*   **URL**: `/api/report/download`
*   **Method**: `POST`
*   **Payload (JSON)**:
    ```json
    {
      "content": "Markdown text...",
      "title": "Report Title"
    }
    ```
*   **Response**: Binary stream of the Word document.

---

## 4. Static Files & UI Routes
*   `/`: Main dashboard (index.html)
*   `/css/*`: Stylesheets
*   `/js/*`: JavaScript files
*   `/assets/*`: Icons and static assets
*   `/img/*`: SVG maps and demo images
*   `/manual/*`: Documentation files (including this guide)
