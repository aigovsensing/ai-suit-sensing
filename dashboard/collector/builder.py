
import pandas as pd
import os
import requests
import logging
from collector.courtlistener import fetch_cases
from collector.processor import process

logger = logging.getLogger(__name__)

def build_from_api(query="artificial intelligence"):
    """
    Method 1: Directly make raw data from Courtlistener.com and RECAP.
    """
    logger.info(f"Fetching data from CourtListener for query: {query}")
    raw_data = fetch_cases(query=query)
    processed_data = process(raw_data)
    return processed_data

def build_from_csv(file_path):
    """
    Method 2: Load and process raw data from a local CSV file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    logger.info(f"Loading data from CSV: {file_path}")
    # Skip first 2 lines based on format: 1. Title, 2. Extraction Date
    try:
        df = pd.read_csv(file_path, skiprows=2).fillna("")
        df.columns = df.columns.str.strip()
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return []

    # Mapping CSV columns to a structured format for the visualizer
    processed_data = []
    for _, row in df.iterrows():
        # Identify the case name and skip empty or invalid rows
        # Many CSVs have trailing empty rows or multi-line descriptions that pandas might misinterpret as new rows
        case_name = str(row.get("소송제목 (원고 v. 피고)*", row.get("소송제목 (원고 v. 피고)", ""))).strip()
        system_id = str(row.get("System ID", "")).strip()
        
        # A valid case must have a title and usually a System ID
        if not case_name or case_name.lower() == "unknown":
            continue
            
        case_data = {
            "case_name": case_name,
            "file_date": row.get("소송제기일*", row.get("소송제기일", "Unknown")),
            "case_no": row.get("소송번호*", row.get("소송번호", "Unknown")),
            "plaintiff": row.get("원고", "Unknown"),
            "defendant": row.get("피고", "Unknown"),
            "country": row.get("국가*", row.get("국가", row.get("Country", "USA"))),
            "court": row.get("법원", row.get("Court", "Unknown")),
            "status": row.get("진행현황", row.get("Status", "Unknown")),
            "reason": row.get("소송이유", row.get("Reason", row.get("Claim", "Unknown"))),
            "url": row.get("Tracker(업로드 시 제외)", row.get("Tracker", "")),
            "summary": row.get("개요 및 배경 (By Gauss)", ""),
            "system_id": system_id,
            "last_update": row.get("Last Update(업로드 시 제외)", row.get("Last Update", "")),
            "history": row.get("히스토리(업로드 시 제외)", row.get("히스토리", "")),
            "result": row.get("진행결과", ""),
            "plaintiff_lawyer": row.get("변호사(원고)", ""),
            "defendant_lawyer": row.get("변호사(피고)", ""),
            "remarks": row.get("비고(업로드 시 제외)", row.get("비고", "")),
            "target_data": row.get("대상 데이터", ""),
            "target_product": row.get("대상 제품", "")
        }
        processed_data.append(case_data)
    
    return processed_data

if __name__ == "__main__":
    # Example usage
    # api_data = build_from_api()
    # print(f"API Data: {len(api_data)} cases")
    
    csv_path = "data/aisuit_20260313.csv"
    if os.path.exists(csv_path):
        csv_data = build_from_csv(csv_path)
        print(f"CSV Data: {len(csv_data)} cases")
