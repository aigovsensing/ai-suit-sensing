from __future__ import annotations
import re
from typing import List, Set, Tuple
from .utils import debug_log
from .gemini import get_embeddings, calculate_cosine_similarity
import os

def extract_section(md_text: str, section_title: str) -> str:
    """Markdown 텍스트에서 특정 섹션 제목 아래의 내용을 추출합니다."""
    lines = md_text.split("\n")
    start = None
    end = None
    started_with_tag = False
    
    for i, line in enumerate(lines):
        s_line = line.strip()
        # 제목이 포함되어 있고, 헤더 형식이거나 summary 태그인 경우 시작점으로 간주
        if section_title in s_line and (s_line.startswith("#") or "<summary>" in s_line):
            start = i + 1
            started_with_tag = "<summary>" in s_line
            continue
        
        if start is not None:
            # 헤더로 시작한 경우, 다음 헤더 또는 새로운 섹션 태그를 만나면 종료
            if not started_with_tag:
                if s_line.startswith("#") or s_line.startswith("<details>") or s_line.startswith("<summary>"):
                    end = i
                    break
            # 태그로 시작한 경우, </details>를 만나면 종료
            else:
                if "</details>" in s_line:
                    end = i
                    break
    
    if start is None:
        return ""
    if end is None:
        end = len(lines)
    return "\n".join(lines[start:end])

def parse_table(section_md: str) -> Tuple[List[str], List[List[str]], Tuple[str, str]]:
    """Markdown 테이블을 헤더, 행 데이터, 메타데이터(헤더/구분선 라인)로 파싱합니다."""
    all_lines = section_md.split("\n")
    lines = []
    for l in all_lines:
        if l.strip().startswith("|"):
            lines.append(l)
        elif lines:
            break

    if len(lines) < 3:
        return [], [], ("", "")

    header = lines[0]
    separator = lines[1]
    rows = lines[2:]

    def split_row(row_text: str) -> List[str]:
        # 역슬래시로 이스케이프되지 않은 파이프만 분할
        return [c.strip() for c in re.split(r'(?<!\\)\|', row_text.strip())[1:-1]]

    header_cols = split_row(header)
    parsed_rows = []
    for row in rows:
        cols = split_row(row)
        if len(cols) == len(header_cols):
            parsed_rows.append(cols)
        else:
            debug_log(f"Table row column mismatch: expected {len(header_cols)}, got {len(cols)}. Row: {row[:100]}...")

    return header_cols, parsed_rows, (header, separator)

def extract_article_title(cell: str) -> str:
    """Markdown 링크 셀에서 제목 텍스트를 추출합니다."""
    # 예: "📝 [Title](URL)" -> "Title"
    m = re.search(r"\[([^\]]+)\]", cell)
    if m:
        return m.group(1).strip()
    # 링크 형식이 아니면 아이콘 등을 제거하고 반환
    t = cell.strip()
    t = re.sub(r"^[^\w]+", "", t) # 앞쪽 특수문자/아이콘 제거
    return t

def extract_article_url(cell: str) -> str | None:
    """Markdown 링크 셀에서 URL을 추출합니다."""
    m = re.search(r"\((https?://[^\)]+)\)", cell)
    if m:
        return m.group(1).split("&hl=")[0]
    return None

def apply_deduplication(md: str, comments: List[dict]) -> tuple[str, int, int]:
    """
    이전 GitHub 댓글들을 분석하여 중복된 데이터를 'skip' 처리하고 요약을 추가합니다.
    """
    comments = comments or []


    # 1) Base Snapshot Key Set 생성 (모든 이전 댓글 대상)
    base_article_set: Set[str] = set()
    base_docket_set: Set[str] = set()

    for comment in comments:
        body = comment.get("body") or ""
        
        # News 처리 (제목 기준으로 체크)
        news_section_base = extract_section(body, "### 📰 AI Suit News")
        h_news, r_news, _ = parse_table(news_section_base)
        if not h_news: # H2 시절 데이터 호환성
             news_section_base = extract_section(body, "## 📰 AI Suit News")
             h_news, r_news, _ = parse_table(news_section_base)

        if "제목" in h_news:
            idx = h_news.index("제목")
            for r in r_news:
                title = extract_article_title(r[idx])
                if title:
                    base_article_set.add(title)
        
        # Cases 처리 (도켓번호 기준으로 체크)
        recap_section_base = extract_section(body, "### ⚖️ Cases")
        h_cases, r_cases, _ = parse_table(recap_section_base)
        if not h_cases: # H2 시절 데이터 호환성
             recap_section_base = extract_section(body, "## ⚖️ Cases")
             h_cases, r_cases, _ = parse_table(recap_section_base)

        if "도켓번호" in h_cases:
            idx = h_cases.index("도켓번호")
            for r in r_cases:
                docket_key = extract_article_title(r[idx])
                if docket_key:
                    base_docket_set.add(docket_key)

        # Docs 처리
        docs_section_base = extract_section(body, "📄 Cases: 법원 문서 기반")
        h_docs, r_docs, _ = parse_table(docs_section_base)
        if "법원 문서" in h_docs:
            idx = h_docs.index("법원 문서")
            for r in r_docs:
                url = extract_article_url(r[idx])
                if url:
                    base_docket_set.add(url) # 문서 URL도 중복 제거 대상에 포함

    # 2) 현재 Markdown 처리 (News - 새 이름 사용)
    current_md = md
    news_section = extract_section(current_md, "### 📰 AI Suit News")
    n_headers, n_rows, n_table_meta = parse_table(news_section)

    new_article_count = 0
    total_article_count = len(n_rows)

    if n_headers and "제목" in n_headers:
        title_idx = n_headers.index("제목")
        no_idx = n_headers.index("No.") if "No." in n_headers else None
        date_idx = n_headers.index("기사일자") if "기사일자" in n_headers else None
        risk_idx = n_headers.index("감지 레벨⬇️") if "감지 레벨⬇️" in n_headers else None
        dup_idx = n_headers.index("중복건수") if "중복건수" in n_headers else None

        header_line, separator_line = n_table_meta
        non_skip_rows = []

        # 의미론적 중복 체크를 위한 임베딩 준비
        current_titles = [extract_article_title(r[title_idx]) for r in n_rows]
        base_titles = list(base_article_set)
        
        # 1단계: 정확한 문자열 일치 제거
        remaining_indices = []
        for i, title in enumerate(current_titles):
            if title in base_article_set:
                debug_log(f"Skipping exact duplicate News: {title}")
            else:
                remaining_indices.append(i)
        
        # 2단계: BM25 기반 텍스트 유사도 체크 (옵션 활성화 시)
        enable_bm25 = os.environ.get("BM25_SEMANTIC_DEDUP", "0") == "1"
        bm25_duplicates = set()
        
        if remaining_indices and base_titles and enable_bm25:
            debug_log(f"Performing BM25 dedup for {len(remaining_indices)} news items against {len(base_titles)} baselines...")
            try:
                from rank_bm25 import BM25Okapi
                
                tokenized_corpus = [t.lower().split() for t in base_titles]
                bm25 = BM25Okapi(tokenized_corpus)
                
                bm25_threshold = float(os.environ.get("BM25_DEDUP_THRESHOLD", "3.0"))
                
                for i in remaining_indices:
                    title = current_titles[i]
                    tokenized_query = title.lower().split()
                    if not tokenized_query:
                        continue
                        
                    scores = bm25.get_scores(tokenized_query)
                    max_score = max(scores) if len(scores) > 0 else 0
                    
                    if max_score >= bm25_threshold:
                        max_idx = list(scores).index(max_score)
                        debug_log(f"Skipping BM25 duplicate: '{title}' is similar to '{base_titles[max_idx]}' (score: {max_score:.4f})")
                        bm25_duplicates.add(i)
                        
            except ImportError:
                debug_log("rank_bm25 library not installed. Skipping BM25 deduplication.")

        remaining_indices = [i for i in remaining_indices if i not in bm25_duplicates]

        # 3단계: 의미론적 유사도 체크 (Gemini API 및 옵션 활성화 시)
        semantic_duplicates = set()
        enable_semantic = os.environ.get("GEMINI_SEMANTIC_DEDUP", "0") == "1"
        current_embeddings = None
        
        if remaining_indices and os.environ.get("GEMINI_API_KEY") and enable_semantic:
            debug_log(f"Fetching embeddings for {len(remaining_indices)} current news items...")
            current_embeddings = get_embeddings([current_titles[i] for i in remaining_indices])
            
            if base_titles:
                debug_log(f"Performing semantic dedup for {len(remaining_indices)} news items against {len(base_titles)} baselines...")
                base_embeddings = get_embeddings(base_titles)
                
                if current_embeddings and base_embeddings:
                    threshold = float(os.environ.get("SEMANTIC_DEDUP_THRESHOLD", "0.85"))
                    for i_idx, i in enumerate(remaining_indices):
                        curr_emb = current_embeddings[i_idx]
                        for j_idx, base_emb in enumerate(base_embeddings):
                            similarity = calculate_cosine_similarity(curr_emb, base_emb)
                            if similarity >= threshold:
                                debug_log(f"Skipping semantic duplicate: '{current_titles[i]}' is similar to '{base_titles[j_idx]}' (sim: {similarity:.4f})")
                                semantic_duplicates.add(i)
                                break

        emb_map = {}
        if current_embeddings:
            for idx_in_rem, i in enumerate(remaining_indices):
                if idx_in_rem < len(current_embeddings):
                    emb_map[i] = current_embeddings[idx_in_rem]

        surviving_baseline_indices = [i for i in remaining_indices if i not in semantic_duplicates]

        # 4단계: 현재 배치 내의 기사들 간 중복 체크 (Intra-batch deduplication 및 중복건수 계산)
        accepted_indices = []
        dup_details = {}  # index -> {"제목": count, "키워드": count, "의미": count}

        for i in surviving_baseline_indices:
            title_i = current_titles[i]
            is_dup = False
            matched_acc_idx = None
            dup_type = None

            for acc_idx in accepted_indices:
                title_acc = current_titles[acc_idx]

                # 1. 정확한 제목 일치 (대소문자 및 공백 무시)
                if title_i.strip().lower() == title_acc.strip().lower():
                    is_dup = True
                    dup_type = "제목"
                    matched_acc_idx = acc_idx
                    debug_log(f"Intra-batch exact duplicate: '{title_i}' matches '{title_acc}'")
                    break

                # 2. BM25 유사도 매칭 (옵션)
                if enable_bm25:
                    try:
                        from rank_bm25 import BM25Okapi
                        tokenized_acc = [title_acc.lower().split()]
                        bm25_acc = BM25Okapi(tokenized_acc)
                        tokenized_query = title_i.lower().split()
                        if tokenized_query:
                            bm25_threshold = float(os.environ.get("BM25_DEDUP_THRESHOLD", "3.0"))
                            scores = bm25_acc.get_scores(tokenized_query)
                            max_score = max(scores) if len(scores) > 0 else 0
                            if max_score >= bm25_threshold:
                                is_dup = True
                                dup_type = "키워드"
                                matched_acc_idx = acc_idx
                                debug_log(f"Intra-batch BM25 duplicate: '{title_i}' is similar to '{title_acc}' (score: {max_score:.4f})")
                                break
                    except Exception:
                        pass

                # 3. 의미론적 유사도 매칭 (옵션)
                if enable_semantic and i in emb_map and acc_idx in emb_map:
                    threshold = float(os.environ.get("SEMANTIC_DEDUP_THRESHOLD", "0.85"))
                    sim = calculate_cosine_similarity(emb_map[i], emb_map[acc_idx])
                    if sim >= threshold:
                        is_dup = True
                        dup_type = "의미"
                        matched_acc_idx = acc_idx
                        debug_log(f"Intra-batch semantic duplicate: '{title_i}' is similar to '{title_acc}' (sim: {sim:.4f})")
                        break

            if is_dup:
                if matched_acc_idx in dup_details:
                    dup_details[matched_acc_idx][dup_type] = dup_details[matched_acc_idx].get(dup_type, 0) + 1
            else:
                accepted_indices.append(i)
                dup_details[i] = {"제목": 0, "키워드": 0, "의미": 0}

        for i in accepted_indices:
            row = n_rows[i]
            if dup_idx is not None:
                details = dup_details[i]
                total_dup = sum(details.values())
                if total_dup == 0:
                    row[dup_idx] = "0"
                else:
                    # 3종(제목/키워드/의미) 모두 표시하되, GitHub 표 폭을 고려해 약어로 압축
                    # 예: "8 (제:6 키:2 의:0)"  (제=제목 일치, 키=BM25 키워드, 의=의미론적)
                    row[dup_idx] = (
                        f"{total_dup} (제:{details.get('제목', 0)} "
                        f"키:{details.get('키워드', 0)} "
                        f"의:{details.get('의미', 0)})"
                    )
            non_skip_rows.append(row)
            new_article_count += 1

        if new_article_count == 0:
            new_news_section = "\n새로운 소식이 0건입니다.\n"
        else:
            final_rows = non_skip_rows
            new_lines = ["", header_line, separator_line]
            for row_idx, r in enumerate(final_rows, start=1):
                if no_idx is not None:
                    r[no_idx] = str(row_idx)
                new_lines.append("| " + " | ".join(r) + " |")
            new_news_section = "\n".join(new_lines)
        current_md = current_md.replace(news_section, new_news_section)

    # 3) 현재 Markdown 처리 (Cases)
    recap_section = extract_section(current_md, "### ⚖️ Cases")
    c_headers, c_rows, c_table_meta = parse_table(recap_section)

    new_docket_count = 0
    total_docket_count = len(c_rows)

    if c_headers and "도켓번호" in c_headers:
        docket_idx = c_headers.index("도켓번호")
        no_idx = c_headers.index("No.") if "No." in c_headers else None
        risk_idx = c_headers.index("감지 레벨⬇️") if "감지 레벨⬇️" in c_headers else None
        status_idx = c_headers.index("상태") if "상태" in c_headers else None
        case_idx = c_headers.index("케이스명") if "케이스명" in c_headers else None

        header_line, separator_line = c_table_meta
        non_skip_rows = []

        for r in c_rows:
            docket_val = r[docket_idx]
            docket_key = extract_article_title(docket_val)
            if docket_key in base_docket_set:
                debug_log(f"Skipping duplicate Case (based on Docket): {r[case_idx]} ({docket_key})")
            else:
                non_skip_rows.append(r)
                new_docket_count += 1

        if new_docket_count == 0:
            new_recap_section = "\n새로운 소식이 0건입니다.\n"
        else:
            final_rows = non_skip_rows
            new_lines = ["", header_line, separator_line]
            for row_idx, r in enumerate(final_rows, start=1):
                if no_idx is not None:
                    r[no_idx] = str(row_idx)
                new_lines.append("| " + " | ".join(r) + " |")
            new_recap_section = "\n".join(new_lines)
        current_md = current_md.replace(recap_section, new_recap_section)

    # 3.5) 법원 문서(Docs) 처리
    docs_section = extract_section(current_md, "📄 Cases: 법원 문서 기반")
    d_headers, d_rows, d_table_meta = parse_table(docs_section)
    new_doc_count = 0
    if d_headers and "법원 문서" in d_headers:
        url_idx = d_headers.index("법원 문서")
        header_line, separator_line = d_table_meta
        non_skip_rows = []
        for r in d_rows:
            url = extract_article_url(r[url_idx])
            if url in base_docket_set: # 위에서 문서 URL도 여기에 담았다고 가정
                continue
            else:
                non_skip_rows.append(r)
                new_doc_count += 1
        
        if new_doc_count == 0:
            new_docs_section = "\n새로운 법원 문서가 0건입니다.\n"
        else:
            new_lines = ["", header_line, separator_line]
            for row_idx, r in enumerate(non_skip_rows, start=1):
                # No. 업데이트 (만약 있으면)
                if "No." in d_headers:
                    r[d_headers.index("No.")] = str(row_idx)
                new_lines.append("| " + " | ".join(r) + " |")
            new_docs_section = "\n".join(new_lines) + "\n"
        
        current_md = current_md.replace(docs_section, new_docs_section)

    # 4) 중복 제거 요약 생성
    base_news = len(base_article_set)
    base_cases = len(base_docket_set) # 사실 여기엔 docket + doc urls가 섞여있음
    dup_news = total_article_count - new_article_count
    dup_cases = total_docket_count - new_docket_count

    new_news_label = f"**{new_article_count} (New)**" + (" 🔴" if new_article_count > 0 else "")
    new_cases_label = f"**{new_docket_count} (New)**" + (" 🔴" if new_docket_count > 0 else "")
    new_docs_label = f"**{new_doc_count} (New)**" + (" 🔴" if new_doc_count > 0 else "")

    summary_header = (
        "### 중복 제거 요약:\n"
        "🔁 Dedup Summary\n"
        f"└ News {base_news} (Baseline): "
        f"{dup_news} (Dup), "
        f"{new_news_label}\n"
        f"└ Cases {base_cases} (Baseline): "
        f"{dup_cases} (Dup), "
        f"{new_cases_label}\n"
        f"└ Docs: {new_docs_label}\n\n"
    )

    return summary_header + current_md, new_article_count, new_docket_count + new_doc_count


def get_consolidated_data(comments: List[dict]) -> tuple[dict, dict, dict]:
    """모든 댓글에서 유니크한 뉴스/사례 데이터를 추출하여 반환합니다."""
    unique_news = {}
    unique_cases = {}
    meta = {"news_header": None, "news_sep": None, "case_header": None, "case_sep": None, "news_cols": [], "case_cols": []}

    for comment in comments:
        body = comment.get("body") or ""
        # News 파싱
        news_section = extract_section(body, "### 📰 AI Suit News") or extract_section(body, "## 📰 AI Suit News")
        h_news, r_news, m_news = parse_table(news_section)
        if h_news and "제목" in h_news:
            idx = h_news.index("제목")
            if not meta["news_header"]:
                meta["news_header"], meta["news_sep"] = m_news
                meta["news_cols"] = h_news
            for r in r_news:
                key = extract_article_url(r[idx]) or r[idx]
                if key not in unique_news: unique_news[key] = r

        # Cases 파싱
        recap_section = extract_section(body, "### ⚖️ Cases") or extract_section(body, "## ⚖️ Cases")
        h_cases, r_cases, m_cases = parse_table(recap_section)
        if h_cases and "도켓번호" in h_cases:
            idx = h_cases.index("도켓번호")
            if not meta["case_header"]:
                meta["case_header"], meta["case_sep"] = m_cases
                meta["case_cols"] = h_cases
            for r in r_cases:
                if r[idx] not in unique_cases: unique_cases[r[idx]] = r
    
    return unique_news, unique_cases, meta

def generate_consolidated_report(comments: List[dict]) -> str:
    """모든 댓글 취합하여 통합 리포트 문자열 생성"""
    unique_news, unique_cases, meta = get_consolidated_data(comments)
    if not unique_news and not unique_cases:
        return "수집된 리포트 내용이 없습니다."

    lines = ["## 📑 당일 소송건들 통합 정리 자료\n"]
    
    # News 통합 출력
    lines.append("### 📰 통합 AI Suit News")
    if unique_news:
        lines.append("")
        lines.append(meta["news_header"]); lines.append(meta["news_sep"])
        news_rows = list(unique_news.values())
        if "감지 레벨⬇️" in meta["news_cols"]:
            det_idx = meta["news_cols"].index("감지 레벨⬇️")
            news_rows.sort(key=lambda r: int(re.search(r"(\d+)", r[det_idx]).group(1)) if re.search(r"(\d+)", r[det_idx]) else 0, reverse=True)
        no_idx = meta["news_cols"].index("No.") if "No." in meta["news_cols"] else None
        
        expected_len = len(meta["news_cols"])
        for i, row in enumerate(news_rows, 1):
            row = list(row)
            if len(row) < expected_len:
                row.extend(["0"] * (expected_len - len(row)))
            elif len(row) > expected_len:
                row = row[:expected_len]
            if no_idx is not None: 
                row[no_idx] = str(i)
            lines.append("| " + " | ".join(row) + " |")
    else: 
        lines.append("\n수집된 뉴스 소식이 없습니다.")
    lines.append("")

    # Cases 통합 출력
    lines.append("### ⚖️ 통합 Cases (Courtlistener+RECAP)")
    if unique_cases:
        lines.append("")
        lines.append(meta["case_header"]); lines.append(meta["case_sep"])
        case_rows = list(unique_cases.values())
        if "감지 레벨⬇️" in meta["case_cols"]:
            det_idx = meta["case_cols"].index("감지 레벨⬇️")
            case_rows.sort(key=lambda r: int(re.search(r"(\d+)", r[det_idx]).group(1)) if re.search(r"(\d+)", r[det_idx]) else 0, reverse=True)
        no_idx = meta["case_cols"].index("No.") if "No." in meta["case_cols"] else None
        
        expected_len = len(meta["case_cols"])
        for i, row in enumerate(case_rows, 1):
            row = list(row)
            if len(row) < expected_len:
                row.extend(["0"] * (expected_len - len(row)))
            elif len(row) > expected_len:
                row = row[:expected_len]
            if no_idx is not None: 
                row[no_idx] = str(i)
            lines.append("| " + " | ".join(row) + " |")
    else: 
        lines.append("\n수집된 사건 소식이 없습니다.")
    
    return "\n".join(lines)
