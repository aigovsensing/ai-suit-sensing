from __future__ import annotations
import os
import sys

# Ensure src is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extract import Lawsuit
from src.render import render_markdown
from src.dedup import apply_deduplication, generate_consolidated_report, parse_table, extract_section

def test_rendering_and_deduplication():
    print("=== Running Test for Rendering and Deduplication ===")
    
    # 1. Mock Lawsuits (some duplicate titles within the batch)
    lawsuits = [
        Lawsuit(
            update_or_filed_date="2026-06-15",
            case_title="Meta v. Porn Producer",
            article_title="Meta can't dodge porn producer's copyright claims",
            case_number="미확인",
            reason="AI 모델 학습 관련 소송",
            article_urls=["https://example.com/1"]
        ),
        # Duplicate of index 0 (exact match)
        Lawsuit(
            update_or_filed_date="2026-06-15",
            case_title="Meta v. Porn Producer",
            article_title="Meta can't dodge porn producer's copyright claims",
            case_number="미확인",
            reason="AI 모델 학습 관련 소송",
            article_urls=["https://example.com/2"]
        ),
        # Another duplicate (exact match)
        Lawsuit(
            update_or_filed_date="2026-06-15",
            case_title="Meta v. Porn Producer",
            article_title="Meta can't dodge porn producer's copyright claims",
            case_number="미확인",
            reason="AI 모델 학습 관련 소송",
            article_urls=["https://example.com/3"]
        ),
        # Unique lawsuit
        Lawsuit(
            update_or_filed_date="2026-06-14",
            case_title="Google Lyria Suit",
            article_title="Google Sued Over Alleged Use Of Copyrighted Music To Train Lyria 3 AI",
            case_number="미확인",
            reason="음악 무단 학습 침해 주장",
            article_urls=["https://example.com/4"]
        ),
        # Duplicate of index 3 (exact match)
        Lawsuit(
            update_or_filed_date="2026-06-14",
            case_title="Google Lyria Suit",
            article_title="Google Sued Over Alleged Use Of Copyrighted Music To Train Lyria 3 AI",
            case_number="미확인",
            reason="음악 무단 학습 침해 주장",
            article_urls=["https://example.com/5"]
        ),
        # Baseline match (already reported)
        Lawsuit(
            update_or_filed_date="2026-06-12",
            case_title="Old Baseline Case",
            article_title="Baseline News Article Already Reported Yesterday",
            case_number="미확인",
            reason="기존 보고 소송",
            article_urls=["https://example.com/6"]
        )
    ]
    
    # 2. Render to Markdown
    rendered_md = render_markdown(
        lawsuits=lawsuits,
        cl_docs=[],
        cl_cases=[],
        recap_doc_count=0,
        lookback_days=3
    )
    
    print("\n[Rendered MD Check]")
    if "중복건수" in rendered_md:
        print("✅ '중복건수' column exists in header.")
    else:
        print("❌ '중복건수' column NOT found in header.")
        sys.exit(1)
        
    # 3. Apply Deduplication with baseline comments
    baseline_comments = [
        {
            "body": (
                "### 📰 AI Suit News\n"
                "| No. | 기사일자 | 제목 | 소송번호 | 조건 (주요 키워드) | 소송사유 | 감지 레벨⬇️ | 중복건수 |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| 1 | 2026-06-12 | 📝 [Baseline News Article Already Reported Yesterday](https://example.com/6) | 미확인 | - | 기존 보고 소송 | 🟢 0 | 0 |\n"
            )
        }
    ]
    
    deduped_md, new_news_count, new_cases_count = apply_deduplication(rendered_md, baseline_comments)
    print("\n[Deduplication Check]")
    print(f"New news count: {new_news_count} (Expected: 2)")
    print(f"New cases count: {new_cases_count}")
    
    # Parse table to verify actual rows and duplicate counts
    news_section = extract_section(deduped_md, "### 📰 AI Suit News")
    headers, rows, _ = parse_table(news_section)
    
    print("\nParsed Rows:")
    for r in rows:
        print(r)
        
    if len(rows) != 2:
        print(f"❌ Expected 2 rows in final table, got {len(rows)}")
        sys.exit(1)
        
    title_idx = headers.index("제목")
    dup_idx = headers.index("중복건수")
    
    # Row 1 check
    r1_title = extract_article_title(rows[0][title_idx])
    r1_dup = rows[0][dup_idx]
    print(f"Row 1: Title='{r1_title}', DupCount={r1_dup}")
    if "Meta" in r1_title and r1_dup == "2 (제목:2)":
        print("✅ Row 1 is correct (Meta with 2 duplicates).")
    else:
        print("❌ Row 1 is incorrect.")
        sys.exit(1)
        
    # Row 2 check
    r2_title = extract_article_title(rows[1][title_idx])
    r2_dup = rows[1][dup_idx]
    print(f"Row 2: Title='{r2_title}', DupCount={r2_dup}")
    if "Google" in r2_title and r2_dup == "1 (제목:1)":
        print("✅ Row 2 is correct (Google with 1 duplicate).")
    else:
        print("❌ Row 2 is incorrect.")
        sys.exit(1)
        
    # Verify baseline match is completely absent
    for r in rows:
        title = extract_article_title(r[title_idx])
        if "Baseline" in title:
            print("❌ Baseline duplicate news was not filtered out!")
            sys.exit(1)
    print("✅ Baseline duplicate news was filtered out correctly.")

def test_consolidation_compatibility():
    print("\n=== Running Test for Consolidation Compatibility ===")
    
    # Mocking comments: one with old 7-column news table and one with new 8-column news table
    comments = [
        # Comment 1: Old format (7 columns)
        {
            "body": (
                "### 📰 AI Suit News\n"
                "| No. | 기사일자 | 제목 | 소송번호 | 조건 (주요 키워드) | 소송사유 | 감지 레벨⬇️ |\n"
                "|---|---|---|---|---|---|---|\n"
                "| 1 | 2026-06-12 | 📝 [Old Article 1](https://example.com/old1) | 미확인 | - | 옛날 기사 | 🟢 0 |\n"
            )
        },
        # Comment 2: New format (8 columns)
        {
            "body": (
                "### 📰 AI Suit News\n"
                "| No. | 기사일자 | 제목 | 소송번호 | 조건 (주요 키워드) | 소송사유 | 감지 레벨⬇️ | 중복건수 |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| 1 | 2026-06-15 | 📝 [New Article 2](https://example.com/new2) | 미확인 | - | 새 기사 | 🟢 0 | 3 |\n"
            )
        }
    ]
    
    consolidated = generate_consolidated_report(comments)
    print("\nConsolidated Report Output:")
    print(consolidated)
    
    # Extract and parse consolidated news table
    cons_section = extract_section(consolidated, "### 📰 통합 AI Suit News")
    headers, rows, _ = parse_table(cons_section)
    
    print(f"Consolidated Headers: {headers}")
    print("Consolidated Rows:")
    for r in rows:
        print(r)
        
    # Verify row lengths
    expected_len = len(headers)
    for r in rows:
        if len(r) != expected_len:
            print(f"❌ Column mismatch: expected {expected_len} elements, got {len(r)}")
            sys.exit(1)
            
    print("✅ Consolidation compatibility check passed successfully.")

if __name__ == "__main__":
    test_rendering_and_deduplication()
    test_consolidation_compatibility()
    print("\n🎉 All tests passed successfully!")
