
import pandas as pd
import sys
import os

def estimate_memory(num_cases):
    # Simulate a case dictionary
    sample_case = {
        "case_name": "Plaintiff v. Defendant " * 5,
        "file_date": "2026-04-30",
        "case_no": "1:26-cv-12345",
        "plaintiff": "Example Plaintiff LLC",
        "defendant": "Global Tech Corp",
        "country": "USA",
        "court": "N.D. Cal.",
        "status": "1심 진행중 (1st Instance)",
        "reason": "Copyright Infringement for AI training data collection without permission",
        "url": "https://example.com/legal/tracker/12345",
        "summary": "This is a detailed summary of the case background and legal implications." * 5,
        "system_id": "SYS-987654321",
        "last_update": "2026-04-30 10:00:00",
        "history": "2026-04-01: Filed; 2026-04-15: Answered",
        "result": "Pending",
        "target_data": "Books3, Common Crawl",
        "target_product": "Large Language Model v2"
    }
    
    # Create a list of N cases
    data = [sample_case for _ in range(num_cases)]
    
    # Measure memory of the list of dicts
    list_mem = sys.getsizeof(data) + sum(sys.getsizeof(d) for d in data)
    
    # Measure memory of DataFrame
    df = pd.DataFrame(data)
    df_mem = df.memory_usage(deep=True).sum()
    
    return {
        "count": num_cases,
        "list_mb": list_mem / (1024 * 1024),
        "df_mb": df_mem / (1024 * 1024)
    }

results = []
for n in [100, 500, 1000, 5000, 10000]:
    results.append(estimate_memory(n))

for r in results:
    print(f"Cases: {r['count']}, List Mem: {r['list_mb']:.2f} MB, DF Mem: {r['df_mb']:.2f} MB")
