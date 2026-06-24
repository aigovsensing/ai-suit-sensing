import pandas as pd
import sys
import os
from datetime import datetime

def convert_csv(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return

    print(f"Reading {input_path}...")
    
    # Read the first two lines to preserve them
    with open(input_path, 'r', encoding='utf-8') as f:
        title_line = f.readline().strip()
        extra_info_line = f.readline().strip()

    # Read the data (skipping first 2 lines)
    try:
        # Use pandas to handle CSV complexity (quoting, etc.)
        df = pd.read_csv(input_path, skiprows=2).fillna("")
        df.columns = df.columns.str.strip()
        
        # Robust filtering: Ensure only rows with a valid case title are kept
        # Identify title column (handles both before and after formats)
        possible_titles = ["소송제목 (원고 v. 피고)*", "소송제목 (원고 v. 피고)", "Case Name"]
        title_col = None
        for pt in possible_titles:
            if pt in df.columns:
                title_col = pt
                break
        
        if title_col:
            initial_count = len(df)
            df = df[df[title_col].astype(str).str.strip() != ""]
            print(f"Filtered {initial_count} rows down to {len(df)} valid cases.")
            
    except Exception as e:
        print(f"Error reading CSV with pandas: {e}")
        return

    # Define the After headers
    after_headers = [
        "No", "System ID", "진행현황", "소송제목 (원고 v. 피고)*", "소송번호*", "소송제기일*", 
        "원고", "피고", "대상 데이터", "대상 제품", "소송이유", "법원", "국가*", 
        "소송금액 (USD)", "개요 및 배경 (By Gauss)", "Tracker(업로드 시 제외)", 
        "관련 주소 (초기)(업로드 시 제외)", "Last Update(업로드 시 제외)", "진행결과", 
        "히스토리(업로드 시 제외)", "변호사(원고)", "변호사(피고)", "비고(업로드 시 제외)"
    ]

    # Mapping from Before to After (Handling missing columns like System ID)
    mapping = {
        "No": "No",
        "System ID": "", # New column, default to empty
        "진행현황": "진행현황",
        "소송제목 (원고 v. 피고)*": "소송제목 (원고 v. 피고)",
        "소송번호*": "소송번호",
        "소송제기일*": "소송제기일",
        "원고": "원고",
        "피고": "피고",
        "대상 데이터": "대상 데이터",
        "대상 제품": "대상 제품",
        "소송이유": "소송이유",
        "법원": "법원",
        "국가*": "국가",
        "소송금액 (USD)": "소송금액 (USD)",
        "개요 및 배경 (By Gauss)": "개요 및 배경 (By Gauss)",
        "Tracker(업로드 시 제외)": "Tracker",
        "관련 주소 (초기)(업로드 시 제외)": "관련 주소 (초기)",
        "Last Update(업로드 시 제외)": "Last Update",
        "진행결과": "진행결과",
        "히스토리(업로드 시 제외)": "히스토리",
        "변호사(원고)": "변호사(원고)",
        "변호사(피고)": "변호사(피고)",
        "비고(업로드 시 제외)": "비고"
    }

    # Construct the new DataFrame
    new_df_data = {}
    for after_h in after_headers:
        before_h = mapping.get(after_h)
        if before_h in df.columns:
            new_df_data[after_h] = df[before_h]
        else:
            # For new columns like "System ID", fill with empty if not found
            # (Note: In some 'After' data, System ID might already exist if it's being transformed again)
            if after_h in df.columns:
                 new_df_data[after_h] = df[after_h]
            else:
                 new_df_data[after_h] = [""] * len(df)

    new_df = pd.DataFrame(new_df_data)

    # Prepare Title and Metadata rows
    # The After title line usually has 22 commas (23 columns total)
    comma_count = len(after_headers) - 1
    new_title = "AI 데이터 소송 현황" + ("," * comma_count)
    
    # Update extraction date if it's today
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_extra_info = f"추출기간 : 2025-06-27 17:34 ~ {now_str}" + ("," * comma_count)

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_updated{ext}"

    print(f"Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write(new_title + "\n")
        f.write(new_extra_info + "\n")
        new_df.to_csv(f, index=False)

    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/csv_converter.py <input_csv_path> [output_csv_path]")
    else:
        convert_csv(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
