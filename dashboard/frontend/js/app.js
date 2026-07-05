const STATE_ABBR = {
    // English Full Names
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
    'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
    'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA',
    'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO',
    'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH',
    'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
    'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY',
    'DISTRICT OF COLUMBIA': 'DC', 'WASHINGTON D.C.': 'DC',
    
    // Common Court Abbreviations
    'CAL.': 'CA', 'N.Y.': 'NY', 'TEX.': 'TX', 'DEL.': 'DE', 'FLA.': 'FL', 'GA.': 'GA',
    'ILL.': 'IL', 'MASS.': 'MA', 'MICH.': 'MI', 'MINN.': 'MN', 'MO.': 'MO', 'N.C.': 'NC',
    'N.J.': 'NJ', 'OHIO': 'OH', 'PA.': 'PA', 'TENN.': 'TN', 'VA.': 'VA', 'WASH.': 'WA',
    
    // Korean names
    '캘리포니아': 'CA', '뉴욕': 'NY', '버지니아': 'VA', '메사추세츠': 'MA', '매사추세츠': 'MA', '일리노이': 'IL',
    '조지아': 'GA', '네바다': 'NV', '플로리다': 'FL', '델라웨어': 'DE', '펜실베이니아': 'PA',
    '메릴랜드': 'MD', '애리조나': 'AZ', '몬태나': 'MT', '텍사스': 'TX', '워싱턴': 'WA',
    '콜로라도': 'CO', '뉴저지': 'NJ', '미시간': 'MI', '오하이오': 'OH', '코네티컷': 'CT', '테네시': 'TN'
};

const CONTINENTS = {
    'AMERICAS': ['us', 'ca', 'mx', 'br', 'ar', 'cl', 'co', 'pe', 've', 'ec', 'bo', 'py', 'uy'],
    'EUROPE': ['gb', 'fr', 'de', 'it', 'es', 'nl', 'be', 'ch', 'at', 'se', 'no', 'fi', 'dk', 'ie', 'pt', 'gr', 'pl', 'cz', 'hu', 'ro', 'bg', 'sk', 'hr', 'si', 'ee', 'lv', 'lt', 'mt', 'cy', 'is', 'li', 'mc', 'sm', 'va', 'ad', 'me', 'rs', 'mk', 'al', 'ba', 'xk', 'md', 'ua', 'by', 'ru'],
    'MIDDLE EAST': ['sa', 'ae', 'il', 'ir', 'iq', 'jo', 'lb', 'sy', 'tr', 'ye', 'om', 'kw', 'qa', 'bh', 'ps', 'eg'],
    'ASIA PACIFIC': ['cn', 'jp', 'kr', 'in', 'id', 'th', 'vn', 'ph', 'my', 'sg', 'tw', 'hk', 'mo', 'au'],
    'AFRICA': ['za', 'eg', 'ng', 'ke', 'ma', 'dz', 'et', 'gh', 'tz', 'ug', 'ci', 'sn', 'cm', 'ao', 'zm', 'zw', 'tn', 'ly', 'sd', 'ss', 'er', 'dj', 'so', 'rw', 'bi', 'mg', 'mu', 'sc', 'km', 're', 'yt', 'bw', 'na', 'ls', 'sz', 'mz', 'mw', 'cd', 'cg', 'ga', 'gq', 'st', 'cf', 'td', 'ne', 'ml', 'bf', 'mr', 'gm', 'gn', 'sl', 'lr', 'tg', 'bj', 'cv', 'sh']
};

const TRANSLATIONS = {
    ko: {
        nav_menu_label: "메뉴",
        nav_dataset_label: "데이터셋",
        btn_load_dataset: "📁 데이터셋 불러오기",
        nav_user_tools_label: "환경설정",
        btn_user_tools: "🛠️ 환경설정",
        nav_region_label: "지역",
        region_us: "국가: US (미국)",
        region_world: "국가: 전세계 (Global)",
        nav_status_label: "상태",
        status_all: "진행상태: 전체",
        st_ready: "준비 중 (Ready)",
        st_started: "소 제기됨 (Started)",
        st_first: "1심 진행중 (1st Instance)",
        st_second: "2심 진행중 (2nd Instance)",
        st_judgment: "판결 선고 (Decision)",
        st_appeal: "항소 제기됨 (Appeal)",
        st_closed: "사건 종결 (Closed)",
        nav_update_label: "갱신",
        btn_update_map: "지도 갱신 (Update Map)",
        nav_report_label: "AI REPORT",
        btn_monthly_report: "월간 보고서 생성",
        nav_stats_label: "통계",
        btn_stats: "📊 통계",
        nav_dataset_search_label: "조회",
        btn_dataset_search: "🔎 데이터셋 소송 조회",
        nav_relation_label: "관계",
        btn_lineage: "🕸️ Lineage (리니지)",
        nav_overview_label: "현황판",
        btn_overview: "📊 메인 현황판",
        nav_lab_label: "실험실",
        lab_placeholder: "🔒 실험실 기능...",
        nav_api_label: "API",
        btn_api_manual: "API 매뉴얼",
        nav_guide_label: "가이드",
        btn_user_guide: "사용자 가이드",
        heatmap_title: "AI Litigation Heatmap",
        total_cases_label: "총 사건 수",
        btn_regional_summary: "미국 주별 소송 현황",
        btn_regional_summary_world: "전세계 국가별 소송 현황",
        search_placeholder: "사건 검색 (소송명, 소송번호, 원고, 피고...)",
        summary_title_us: "미국 주별 소송 현황 상세",
        summary_title_world: "전세계 국가별 소송 현황 상세",
        col_loc_us: "주 (State)",
        col_loc_world: "국가",
        col_count: "소송 건수",
        col_share: "비중 (%)",
        summary_text_world: "현재 전세계 총 <b>{total}건</b>의 소송이 집계되었습니다. 주요 소송 발생 국가는 <b>{top3}</b> 순입니다.",
        summary_text_us: "현재 미국 내 총 <b>{total}건</b>의 소송이 집계되었습니다. 가장 많은 소송이 진행 중인 지역은 <b>{top3}</b> 등입니다.",
        close: "닫기 (Close)",
        share_info_label: "미국건수/전세계건수 (점유율)",
        user_tools_title: "🛠️ 환경설정 (Settings)",
        search_defendant_label: "1. 피고별 소송 조회",
        search_target_label: "2. 대상 데이터별 소송 조회",
        search_status_label: "3. 소송 상태별 조회",
        search_dataset_label: "4. 데이터셋별 소송 검색",
        search_dataset_desc: "Books3, Common Crawl 등 특정 데이터셋 이름이 포함된 소송을 검색합니다.",
        btn_view: "조회 (View)",
        btn_back_to_tools: "← 다시 검색",
        apply_to_map_label: "위의 설정값들을 지도 히트맵에 한꺼번에 반영하려면 아래 버튼을 누르세요.",
        btn_apply_to_map: "✅ 지도 필터 적용",
        results_title: "조회 결과",
        no_results: "조회 결과가 없습니다.",
        defendant_all: "피고: 전체",
        target_all: "대상: 전체",
        col_name: "사건명",
        col_defendant: "피고",
        col_target_data: "대상 데이터",
        col_filed_date: "제기일",
        col_status: "진행상태",
        page_size_label: "출력 개수:",
        dataset_search_placeholder: "조회할 데이터셋 이름을 입력하세요 (예: Books3, Common Crawl)...",
        load_dataset_title: "📁 데이터셋 불러오기 (Load Dataset)",
        select_dataset_label: "1. 데이터셋 선택 (Select Dataset)",
        select_region_label: "2. 지역 선택 (Select Region)",
        btn_reflect_data: "🚀 데이터 반영 및 지도 업데이트",
        logo_ai: "AI",
        logo_dashboard: "대시보드",
        theme_label: "스타일:",
        case_details_title: "사건 상세",
        stats_dashboard_title: "📊 AI 소송 데이터 종합 통계",
        stats_claim: "1. 청구 내용별 (By Claim)",
        stats_defendant: "2. 피고별 (By Defendant)",
        stats_country: "3. 국가별 (By Country)",
        stats_decision: "4. 판결 결과별 (By Decision)",
        stats_target_data: "5. 학습 데이터별 (By Target Data)",
        stats_trend: "6. 시기별 추이 (Litigation Trend)",
        stats_title: "AI 소송 통계",
        btn_reset_sidebar: "초기화",
        empty_msg_no_search: "선택한 필터에 해당하는 사건이 없습니다.",
        empty_msg_no_query: "\"{query}\"에 대한 검색 결과가 없습니다.",
        col_system_id: "시스템 ID",
        col_plaintiff: "원고",
        col_lawyer: "변호인",
        reason_label: "소송 이유 (Litigation Reason)",
        summary_label: "전체 사건 요약 (Full Summary)",
        count_unit: "건",
        category_count: "카테고리 개수",
        count_suffix: "개",
        item: "항목",
        count: "건수",
        status_none_selected: "소송 상태: 선택 없음",
        status_selected_label: "소송 상태: {first} 외 {count}건",
        alert_select_status: "적어도 하나의 진행상태를 선택해주세요.",
        updating: "갱신 중...",
        error_fetch_data: "데이터 로드 실패",
        unknown_court: "알 수 없는 법원",
        status_na: "상태 정보 없음",
        title_claim: "1. 청구 내용별",
        title_defendant: "2. 피고별",
        title_country: "3. 국가별",
        title_decision: "4. 판결 결과별",
        title_target_data: "5. 학습 데이터별",
        nav_doc_label: "MANUAL",
        select_doc: "매뉴얼 선택...",
        select_dataset: "데이터셋 선택...",
        continental_zoom_label: "대륙별줌인:",
        hide_forever: "다시 보지 않기",
        ticker_restore_label: "5. 티커 표시 설정 초기화 (Restore Tickers)",
        ticker_restore_desc: "숨겨진 실시간 티커(Live Tickers)를 다시 표시합니다.",
        btn_restore: "표시 설정 초기화 (Restore)",
        trend_unit: "단위:",
        trend_unit_month: "월별",
        trend_unit_year: "연도별",
        trend_type: "유형:",
        trend_stack: "누적대상:",
        trend_country: "국가별:",
        trend_period: "기간:",
        axis_y_cases: "소송 건수",
        axis_x_time: "시기",
        nav_radar_label: "레이더",
        btn_radar: "🛰️ 리스크 레이더 (Alpha)",
        radar_title: "🛰️ AI 리스크 레이더 (AI Risk Radar)",
        radar_potential_risks: "⚠️ 삼성 AI 제품/서비스별 잠재적 소송 리스크",
        radar_checklist: "✅ 사업부별 사전 체크리스트 & 유의사항",
        radar_select_region: "🌍 타겟 출시 국가 선택:",
        radar_readiness: "출시 준비도 (Readiness):"
    },

    en: {
        nav_menu_label: "MENU",
        nav_dataset_label: "DATASET",
        btn_load_dataset: "📁 Load Dataset",
        nav_user_tools_label: "SETTINGS",
        btn_user_tools: "🛠️ Settings",
        nav_region_label: "REGION",
        region_us: "Country: US (USA)",
        region_world: "Country: Global",
        nav_status_label: "STATUS",
        status_all: "Status: All",
        st_ready: "Ready",
        st_started: "Started",
        st_first: "1st Instance",
        st_second: "2nd Instance",
        st_judgment: "Decision",
        st_appeal: "Appeal",
        st_closed: "Closed",
        nav_update_label: "UPDATE",
        btn_update_map: "Update Map",
        nav_report_label: "AI REPORT",
        btn_monthly_report: "Monthly Report",
        nav_stats_label: "STATISTICS",
        btn_stats: "📊 Statistics",
        nav_dataset_search_label: "DATASET",
        btn_dataset_search: "🔎 Dataset Search",
        nav_relation_label: "RELATION",
        btn_lineage: "🕸️ Lineage",
        nav_overview_label: "OVERVIEW",
        btn_overview: "📊 Status Board",
        nav_lab_label: "LAB",
        lab_placeholder: "🔒 Lab Features...",
        nav_api_label: "API",
        btn_api_manual: "API Manual",
        nav_guide_label: "GUIDE",
        btn_user_guide: "User Guide",
        heatmap_title: "AI Litigation Heatmap",
        total_cases_label: "Total Cases",
        btn_regional_summary: "US Regional Status",
        btn_regional_summary_world: "Global Country Status",
        search_placeholder: "Search cases (Title, Case No, Plaintiff, Defendant...)",
        summary_title_us: "US Regional Litigation Status",
        summary_title_world: "Global Litigation Status",
        col_loc_us: "State",
        col_loc_world: "Country",
        col_count: "Cases",
        col_share: "Share (%)",
        summary_text_world: "Currently, a total of <b>{total}</b> litigation cases have been aggregated globally. The top countries are <b>{top3}</b>.",
        summary_text_us: "Currently, a total of <b>{total}</b> litigation cases have been aggregated in the US. The top regions are <b>{top3}</b>.",
        close: "Close",
        trend_unit: "Unit:",
        trend_unit_month: "Monthly",
        trend_unit_year: "Yearly",
        trend_type: "Type:",
        trend_stack: "Stack By:",
        trend_country: "Country:",
        trend_period: "Period:",
        axis_y_cases: "Cases",
        axis_x_time: "Time",
        share_info_label: "US Cases / Global Total (Share)",

        user_tools_title: "🛠️ Settings",
        search_defendant_label: "1. Search by Defendant",
        search_target_label: "2. Search by Target Data",
        search_status_label: "3. Search by Status",
        search_dataset_label: "4. Search by Dataset",
        search_dataset_desc: "Search for lawsuits involving specific datasets like Books3, Common Crawl, etc.",
        btn_view: "View",
        btn_back_to_tools: "← Back to Tools",
        apply_to_map_label: "Click below to apply all current filters to the global heatmap.",
        btn_apply_to_map: "✅ Apply to Map",
        results_title: "Results",
        no_results: "No results found.",
        defendant_all: "Defendant: All",
        target_all: "Target: All",
        col_name: "Case Name",
        col_defendant: "Defendant",
        col_target_data: "Target Data",
        col_filed_date: "Filed Date",
        col_status: "Status",
        page_size_label: "Page Size:",
        dataset_search_placeholder: "Enter dataset name (e.g., Books3, Common Crawl)...",
        load_dataset_title: "📁 Load Dataset",
        select_dataset_label: "1. Select Dataset",
        select_region_label: "2. Select Region",
        btn_reflect_data: "🚀 Load & Update Map",
        logo_ai: "AI",
        logo_dashboard: "Dashboard",
        theme_label: "Style:",
        case_details_title: "Case Details",
        stats_dashboard_title: "📊 AI Litigation Statistics Dashboard",
        stats_claim: "1. By Claim",
        stats_defendant: "2. By Defendant",
        stats_country: "3. By Country",
        stats_decision: "4. By Decision",
        stats_target_data: "5. By Target Data",
        stats_trend: "6. Litigation Trend",
        stats_title: "AI Litigation Statistics",
        btn_reset_sidebar: "Reset",
        empty_msg_no_search: "No cases match the selected filters.",
        empty_msg_no_query: "No cases found for \"{query}\".",
        col_system_id: "System ID",
        col_plaintiff: "Plaintiff",
        col_lawyer: "Lawyer",
        reason_label: "Litigation Reason",
        summary_label: "Full Case Summary",
        count_unit: " cases",
        category_count: "Categories",
        count_suffix: "",
        item: "Item",
        count: "Count",
        status_none_selected: "Status: None selected",
        status_selected_label: "Status: {first} & {count} more",
        alert_select_status: "Please select at least one status.",
        updating: "Updating...",
        error_fetch_data: "Failed to load data",
        unknown_court: "Unknown Court",
        status_na: "Status N/A",
        title_claim: "1. By Claim",
        title_defendant: "2. By Defendant",
        title_country: "3. By Country",
        title_decision: "4. By Decision",
        title_target_data: "5. By Target Data",
        nav_doc_label: "MANUAL",
        select_doc: "Select Manual...",
        select_dataset: "Select Dataset...",
        continental_zoom_label: "Continental Zoom:",
        hide_forever: "Don't show again",
        ticker_restore_label: "5. Dashboard Settings",
        ticker_restore_desc: "Restore hidden Live Tickers to the dashboard.",
        btn_restore: "Restore Tickers",
        nav_radar_label: "RADAR",
        btn_radar: "🛰️ Risk Radar (Alpha)",
        radar_title: "🛰️ AI Risk Radar",
        radar_potential_risks: "⚠️ Potential Litigation Risks by Product/Service",
        radar_checklist: "✅ Pre-launch Checklist & Precautions by Division",
        radar_select_region: "🌍 Select Target Launch Region:",
        radar_readiness: "Launch Readiness:"
    }
};

const COUNTRY_MAP = {
    '미국': 'us', 'USA': 'us', 'U.S.': 'us', 'UNITED STATES': 'us',
    '한국': 'kr', 'SOUTH KOREA': 'kr', 'KOREA': 'kr', '대한민국': 'kr',
    '독일': 'de', 'GERMANY': 'de',
    '영국': 'gb', 'UK': 'gb', 'UNITED KINGDOM': 'gb',
    '프랑스': 'fr', 'FRANCE': 'fr',
    '캐나다': 'ca', 'CANADA': 'ca',
    '일본': 'jp', 'JAPAN': 'jp',
    '중국': 'cn', 'CHINA': 'cn',
    '이탈리아': 'it', 'ITALY': 'it',
    '스페인': 'es', 'SPAIN': 'es',
    '이스라엘': 'il', 'ISRAEL': 'il',
    '호주': 'au', 'AUSTRALIA': 'au',
    '스위스': 'ch', 'SWITZERLAND': 'ch'
};
let trendZoomLevel = 1.0;


const COUNTRY_LABEL_OVERRIDE = {
    'kr': 'KO',
    'us': 'US',
    'gb': 'UK'
};

const CATEGORY_KEYWORDS = {
    'target_data': {
        "Authors/Books": ["book", "text", "novel", "author", "책", "도서", "저서", "글", "문학", "작가"],
        "Music/Recordings": ["music", "audio", "song", "recording", "음악", "음원", "노래", "오디오", "가수"],
        "Visual Art": ["image", "art", "picture", "photo", "drawing", "painting", "이미지", "그림", "사진", "미술", "예술", "작품"],
        "Video/Film": ["video", "movie", "film", "youtube", "비디오", "영상", "영화", "유튜브"],
        "Voice/Likeness": ["voice", "face", "likeness", "biometric", "목소리", "얼굴", "초상", "음성"],
        "News": ["news", "article", "journalism", "뉴스", "기사", "언론"],
        "Publishers": ["publish", "publisher", "press", "출판", "신문사"],
        "Code/Software": ["code", "software", "programming", "github", "코드", "소프트웨어", "프로그래밍", "깃허브"]
    },
    'claim': {
        "Direct copyright": ["direct", "copyright infringement", "저작권 침해", "복제", "무단 사용", "무단 수집"],
        "Vicarious infringement": ["vicarious", "대위"],
        "Contributory infringement": ["contributory", "기여", "방조"],
        "Inducement": ["inducement", "유도", "권장"],
        "DMCA": ["dmca", "digital millennium", "저작권 보호"],
        "Latham Act": ["latham", "lanham", "상표", "부정경쟁"],
        "Sate law claims": ["state law", "common law", "주법", "관습법", "불공정", "퍼블리시티"]
    }
};

const CATEGORY_ICONS = {
    claim: {
        "Direct copyright": "⚖️",
        "Vicarious infringement": "🤝",
        "Contributory infringement": "🔗",
        "Inducement": "📢",
        "DMCA": "📜",
        "Latham Act": "™️",
        "Sate law claims": "🏛️",
        "기타": "🔹"
    },
    defendant: {
        "OpenAI": "🤖",
        "Meta": "♾️",
        "Alphabet(Google)": "🔍",
        "Google": "🔍",
        "Microsoft": "💻",
        "Anthropic": "🧬",
        "Nvidia": "🎮",
        "Apple": "🍎",
        "Perplexity": "🌀",
        "Stability AI": "🎨",
        "Adobe": "🖍️",
        "Suno": "🎵",
        "Databricks": "🧱",
        "Runway AI": "📽️",
        "Uncharted Labs (Udio)": "📻",
        "기타": "🏢"
    },
    country: {
        "미국": "<img src='https://flagcdn.com/w20/us.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='US'>", "US": "<img src='https://flagcdn.com/w20/us.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='US'>", "United States": "<img src='https://flagcdn.com/w20/us.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='US'>",
        "독일": "<img src='https://flagcdn.com/w20/de.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Germany'>", "Germany": "<img src='https://flagcdn.com/w20/de.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Germany'>",
        "캐나다": "<img src='https://flagcdn.com/w20/ca.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Canada'>", "Canada": "<img src='https://flagcdn.com/w20/ca.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Canada'>",
        "한국": "<img src='https://flagcdn.com/w20/kr.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Korea'>", "Korea": "<img src='https://flagcdn.com/w20/kr.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Korea'>", "South Korea": "<img src='https://flagcdn.com/w20/kr.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Korea'>",
        "영국": "<img src='https://flagcdn.com/w20/gb.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='UK'>", "UK": "<img src='https://flagcdn.com/w20/gb.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='UK'>", "United Kingdom": "<img src='https://flagcdn.com/w20/gb.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='UK'>",
        "인도": "<img src='https://flagcdn.com/w20/in.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='India'>", "India": "<img src='https://flagcdn.com/w20/in.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='India'>",
        "일본": "<img src='https://flagcdn.com/w20/jp.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Japan'>", "Japan": "<img src='https://flagcdn.com/w20/jp.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Japan'>",
        "이탈리아": "<img src='https://flagcdn.com/w20/it.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Italy'>", "Italy": "<img src='https://flagcdn.com/w20/it.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Italy'>",
        "프랑스": "<img src='https://flagcdn.com/w20/fr.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='France'>", "France": "<img src='https://flagcdn.com/w20/fr.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='France'>",
        "브라질": "<img src='https://flagcdn.com/w20/br.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Brazil'>", "Brazil": "<img src='https://flagcdn.com/w20/br.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Brazil'>",
        "헝가리": "<img src='https://flagcdn.com/w20/hu.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Hungary'>", "Hungary": "<img src='https://flagcdn.com/w20/hu.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Hungary'>",
        "덴마크": "<img src='https://flagcdn.com/w20/dk.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Denmark'>", "Denmark": "<img src='https://flagcdn.com/w20/dk.png' width='16' style='vertical-align: middle; border-radius: 2px;' alt='Denmark'>"
    },
    decision: {
        "소 제기됨": "📁",
        "준비중": "⏳",
        "사건 종결": "✅",
        "판결 선고": "🔨",
        "항소 제기됨": "⤴️",
        "2심 진행중": "⚖️",
        "1심 진행중": "⚖️"
    },
    target_data: {
        "Authors/Books": "📚",
        "Music/Recordings": "🎶",
        "Visual Art": "🖼️",
        "Video/Film": "🎬",
        "Voice/Likeness": "🗣️",
        "News": "📰",
        "Publishers": "📇",
        "Code/Software": "💻",
        "Other": "📁"
    }
};

function getCategoryIcon(type, key) {
    if (!CATEGORY_ICONS[type]) return "🔹";
    const cleanKey = key.trim();
    if (CATEGORY_ICONS[type][cleanKey]) return CATEGORY_ICONS[type][cleanKey];
    for (const [k, v] of Object.entries(CATEGORY_ICONS[type])) {
        if (k.toLowerCase() === cleanKey.toLowerCase()) return v;
    }
    if (type === 'defendant') {
        if (cleanKey.toLowerCase().includes('openai')) return "🤖";
        if (cleanKey.toLowerCase().includes('meta')) return "♾️";
        if (cleanKey.toLowerCase().includes('microsoft')) return "💻";
        if (cleanKey.toLowerCase().includes('google') || cleanKey.toLowerCase().includes('alphabet')) return "🔍";
    }
    return "🔹";
}


const FULL_NAMES = {
    // US States
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia',
    
    // Global Countries (ISO 3166-1 alpha-2)
    'af': 'Afghanistan', 'al': 'Albania', 'dz': 'Algeria', 'ad': 'Andorra', 'ao': 'Angola',
    'ag': 'Antigua and Barbuda', 'ar': 'Argentina', 'am': 'Armenia', 'au': 'Australia', 'at': 'Austria',
    'az': 'Azerbaijan', 'bs': 'Bahamas', 'bh': 'Bahrain', 'bd': 'Bangladesh', 'bb': 'Barbados',
    'by': 'Belarus', 'be': 'Belgium', 'bz': 'Belize', 'bj': 'Benin', 'bt': 'Bhutan',
    'bo': 'Bolivia', 'ba': 'Bosnia and Herzegovina', 'bw': 'Botswana', 'br': 'Brazil', 'bn': 'Brunei',
    'bg': 'Bulgaria', 'bf': 'Burkina Faso', 'bi': 'Burundi', 'kh': 'Cambodia', 'cm': 'Cameroon',
    'ca': 'Canada', 'cv': 'Cape Verde', 'cf': 'Central African Republic', 'td': 'Chad', 'cl': 'Chile',
    'cn': 'China', 'co': 'Colombia', 'km': 'Comoros', 'cg': 'Congo', 'cd': 'DR Congo',
    'cr': 'Costa Rica', 'hr': 'Croatia', 'cu': 'Cuba', 'cy': 'Cyprus', 'cz': 'Czech Republic',
    'dk': 'Denmark', 'dj': 'Djibouti', 'dm': 'Dominica', 'do': 'Dominican Republic', 'ec': 'Ecuador',
    'eg': 'Egypt', 'sv': 'El Salvador', 'gq': 'Equatorial Guinea', 'er': 'Eritrea', 'ee': 'Estonia',
    'et': 'Ethiopia', 'fj': 'Fiji', 'fi': 'Finland', 'fr': 'France', 'ga': 'Gabon',
    'gm': 'Gambia', 'ge': 'Georgia', 'de': 'Germany', 'gh': 'Ghana', 'gr': 'Greece',
    'gd': 'Grenada', 'gt': 'Guatemala', 'gn': 'Guinea', 'gw': 'Guinea-Bissau', 'gy': 'Guyana',
    'ht': 'Haiti', 'hn': 'Honduras', 'hu': 'Hungary', 'is': 'Iceland', 'in': 'India',
    'id': 'Indonesia', 'ir': 'Iran', 'iq': 'Iraq', 'ie': 'Ireland', 'il': 'Israel',
    'it': 'Italy', 'jm': 'Jamaica', 'jp': 'Japan', 'jo': 'Jordan', 'kz': 'Kazakhstan',
    'ke': 'Kenya', 'ki': 'Kiribati', 'kp': 'North Korea', 'kr': 'South Korea', 'kw': 'Kuwait',
    'kg': 'Kyrgyzstan', 'la': 'Laos', 'lv': 'Latvia', 'lb': 'Lebanon', 'ls': 'Lesotho',
    'lr': 'Liberia', 'ly': 'Libya', 'li': 'Liechtenstein', 'lt': 'Lithuania', 'lu': 'Luxembourg',
    'mg': 'Madagascar', 'mw': 'Malawi', 'my': 'Malaysia', 'mv': 'Maldives', 'ml': 'Mali',
    'mt': 'Malta', 'mh': 'Marshall Islands', 'mr': 'Mauritania', 'mu': 'Mauritius', 'mx': 'Mexico',
    'fm': 'Micronesia', 'md': 'Moldova', 'mc': 'Monaco', 'mn': 'Mongolia', 'me': 'Montenegro',
    'ma': 'Morocco', 'mz': 'Mozambique', 'mm': 'Myanmar', 'na': 'Namibia', 'nr': 'Nauru',
    'np': 'Nepal', 'nl': 'Netherlands', 'nz': 'New Zealand', 'ni': 'Nicaragua', 'ne': 'Niger',
    'ng': 'Nigeria', 'mk': 'North Macedonia', 'no': 'Norway', 'om': 'Oman', 'pk': 'Pakistan',
    'pw': 'Palau', 'pa': 'Panama', 'pg': 'Papua New Guinea', 'py': 'Paraguay', 'pe': 'Peru',
    'ph': 'Philippines', 'pl': 'Poland', 'pt': 'Portugal', 'qa': 'Qatar', 'ro': 'Romania',
    'ru': 'Russia', 'rw': 'Rwanda', 'kn': 'Saint Kitts and Nevis', 'lc': 'Saint Lucia', 'vc': 'Saint Vincent and the Grenadines',
    'ws': 'Samoa', 'sm': 'San Marino', 'st': 'Sao Tome and Principe', 'sa': 'Saudi Arabia', 'sn': 'Senegal',
    'rs': 'Serbia', 'sc': 'Seychelles', 'sl': 'Sierra Leone', 'sg': 'Singapore', 'sk': 'Slovakia',
    'si': 'Slovenia', 'sb': 'Solomon Islands', 'so': 'Somalia', 'za': 'South Africa', 'ss': 'South Sudan',
    'es': 'Spain', 'lk': 'Sri Lanka', 'sd': 'Sudan', 'sr': 'Suriname', 'se': 'Sweden',
    'ch': 'Switzerland', 'sy': 'Syria', 'tw': 'Taiwan', 'tj': 'Tajikistan', 'tz': 'Tanzania',
    'th': 'Thailand', 'tl': 'Timor-Leste', 'tg': 'Togo', 'to': 'Tonga', 'tt': 'Trinidad and Tobago',
    'tn': 'Tunisia', 'tr': 'Turkey', 'tm': 'Turkmenistan', 'tv': 'Tuvalu', 'ug': 'Uganda',
    'ua': 'Ukraine', 'ae': 'United Arab Emirates', 'gb': 'United Kingdom', 'us': 'United States', 'uy': 'Uruguay',
    'uz': 'Uzbekistan', 'vu': 'Vanuatu', 've': 'Venezuela', 'vn': 'Vietnam', 'ye': 'Yemen',
    'zm': 'Zambia', 'zw': 'Zimbabwe', 'hk': 'Hong Kong', 'mo': 'Macau', 'pr': 'Puerto Rico'
};


let allCases = [];
let currentFilteredCases = [];
let currentVisibleCases = [];

// Ticker State
let suitTickerInterval, newsTickerInterval;
let suitTickerCount = 10;
let newsTickerCount = 10;

// Sidebar Pagination State
let sidebarAllCases = [];
let sidebarCurrentPage = 1;
let sidebarPageSize = 15;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Core UI Setup & Event Listeners (Priority - Must be attached BEFORE async work)
    initMobileMenu();
    initMapControls();
    
    // Attach header button listeners immediately
    const openDatasetModalBtn = document.getElementById('open-dataset-modal-btn');
    const datasetLoadModal = document.getElementById('dataset-load-modal');
    if (openDatasetModalBtn && datasetLoadModal) {
        openDatasetModalBtn.onclick = () => { datasetLoadModal.style.display = 'flex'; };
    }

    const openRadarBtn = document.getElementById('open-radar-btn');
    if (openRadarBtn) {
        openRadarBtn.onclick = () => {
            const overlay = document.getElementById('radar-overlay');
            if (overlay) {
                overlay.style.display = 'flex';
                // Hide background to focus on radar
                document.getElementById('map-viewport').style.display = 'none';
                document.querySelector('.sidebar').style.display = 'none';
                document.getElementById('status-display').style.display = 'none';
                document.getElementById('stats-container').style.display = 'none';
                
                initRadarContent();
            }
        };
    }

    const radarCloseBtn = document.getElementById('radar-close-btn');
    const radarCloseBtnTop = document.getElementById('radar-close-btn-top');
    const radarOverlay = document.getElementById('radar-overlay');

    const closeRadar = () => {
        if (radarOverlay) radarOverlay.style.display = 'none';
        ensureMapView();
    };

    if (radarCloseBtn) radarCloseBtn.onclick = closeRadar;
    if (radarCloseBtnTop) radarCloseBtnTop.onclick = closeRadar;
    
    if (radarOverlay) {
        radarOverlay.onclick = (e) => {
            if (e.target === radarOverlay) closeRadar();
        };
    }

    const openSearchToolsBtn = document.getElementById('open-search-tools-btn');
    if (openSearchToolsBtn) {
        openSearchToolsBtn.onclick = () => {
            const overlay = document.getElementById('user-tools-overlay');
            if (overlay) {
                overlay.style.display = 'flex';
                // Stop map/sidebar from being hidden if you want to keep them in background
                // but usually we hide them to focus. Let's keep existing behavior of hiding background elements:
                document.getElementById('map-viewport').style.display = 'none';
                document.querySelector('.sidebar').style.display = 'none';
                document.getElementById('status-display').style.display = 'none';
                document.getElementById('stats-container').style.display = 'none';
                
                document.getElementById('user-tools-view').style.display = 'block';
                document.getElementById('user-tools-settings-area').style.display = 'block';
                document.getElementById('user-tools-results-area').style.display = 'none';
            }
        };
    }

    const userToolsCloseBtn = document.getElementById('user-tools-close-btn');
    const userToolsCloseBtnTop = document.getElementById('user-tools-close-btn-top');
    const userToolsOverlay = document.getElementById('user-tools-overlay');

    const closeSettings = () => {
        if (userToolsOverlay) userToolsOverlay.style.display = 'none';
        ensureMapView();
        refreshVisualization();
    };

    if (userToolsCloseBtn) userToolsCloseBtn.onclick = closeSettings;
    if (userToolsCloseBtnTop) userToolsCloseBtnTop.onclick = closeSettings;

    if (userToolsOverlay) {
        userToolsOverlay.onclick = (e) => {
            if (e.target === userToolsOverlay) {
                closeSettings();
            }
        };
        // Prevent closing when clicking inside the view
        const userToolsView = document.getElementById('user-tools-view');
        if (userToolsView) {
            userToolsView.onclick = (e) => e.stopPropagation();
        }
    }

    const detailBackBtn = document.getElementById('detail-back-btn');
    if (detailBackBtn) {
        detailBackBtn.onclick = () => {
            ensureMapView();
            refreshVisualization();
            // Clear selection highlight in sidebar
            document.querySelectorAll('.case-item').forEach(el => el.classList.remove('selected'));
        };
    }

    // ─── 실험실(Lab): 실험적 기능 모음 — 암호 확인 후 사용 ───
    // 통계/리니지/리스크 레이더/타임라인/월간 보고서는 개선 진행 중인 기능이라
    // 실험실 메뉴 하나로 통합. 암호는 세션당 1회만 확인(sessionStorage).
    const labSelect = document.getElementById('lab-select');
    if (labSelect) {
        labSelect.addEventListener('change', () => {
            const val = labSelect.value;
            labSelect.value = ''; // 같은 항목을 다시 선택할 수 있도록 리셋
            if (!val) return;
            if (sessionStorage.getItem('lab-unlocked') !== '1') {
                const pw = prompt("실험실 메뉴는 접근이 제한되어 있습니다. 암호를 입력해주세요.");
                if (pw !== "2848") {
                    if (pw !== null) alert("암호가 일치하지 않습니다.");
                    return;
                }
                sessionStorage.setItem('lab-unlocked', '1');
            }
            switch (val) {
                case 'stats':    document.getElementById('stats-menu-btn')?.click(); break;
                case 'lineage':  window.open('lineage.html', '_blank'); break;
                case 'radar':    document.getElementById('open-radar-btn')?.click(); break;
                case 'timeline': location.href = '/timeline/timeline-aisuit.html'; break;
                case 'report':   document.getElementById('report-menu-btn')?.click(); break;
            }
        });
    }

    const reportMenuBtn = document.getElementById('report-menu-btn');
    const reportModal = document.getElementById('report-modal');
    const generateReportBtn = document.getElementById('generate-report-btn');
    const closeReportBtn = document.getElementById('close-report-btn');

    // 연/월 드롭다운 채우기 (type="month" 미지원 브라우저 대비 크로스브라우저 처리)
    const populateMonthPicker = () => {
        const yearSel = document.getElementById('report-year-input');
        const monthSel = document.getElementById('report-month-num-input');
        if (!yearSel || !monthSel || yearSel.options.length > 0) return; // 한 번만 채움
        const now = new Date();
        const curYear = now.getFullYear();
        // 데이터 범위를 넉넉히 커버: (현재-3) ~ (현재+1)년, 최신 연도가 위로 오도록 내림차순
        for (let y = curYear + 1; y >= curYear - 3; y--) {
            const opt = document.createElement('option');
            opt.value = String(y);
            opt.textContent = `${y}년`;
            yearSel.appendChild(opt);
        }
        for (let m = 1; m <= 12; m++) {
            const mm = String(m).padStart(2, '0');
            const opt = document.createElement('option');
            opt.value = mm;
            opt.textContent = `${mm}월`;
            monthSel.appendChild(opt);
        }
        // 기본값: 현재 연/월
        yearSel.value = String(curYear);
        monthSel.value = String(now.getMonth() + 1).padStart(2, '0');
    };

    if (reportMenuBtn && reportModal) {
        // 암호 확인은 실험실(lab-select) 진입 시 1회 수행하므로 여기서는 생략
        reportMenuBtn.onclick = () => {
            populateMonthPicker();
            reportModal.style.display = 'flex';
            const res = document.getElementById('report-result-container');
            if (res) res.style.display = 'none';
        };
    }

    if (reportModal && closeReportBtn && generateReportBtn) {
        closeReportBtn.onclick = () => reportModal.style.display = 'none';
        
        generateReportBtn.onclick = async () => {
            const typeSelect = document.getElementById('report-type-select');
            const yearInput = document.getElementById('report-year-input');
            const monthNumInput = document.getElementById('report-month-num-input');
            const csvSelect = document.getElementById('csv-select');
            const reportResultContainer = document.getElementById('report-result-container');

            if (!typeSelect || !yearInput || !monthNumInput || !csvSelect) {
                console.error("Required report fields missing");
                return;
            }

            const type = typeSelect.value;
            // 연/월 드롭다운을 'YYYY-MM' 형식으로 조합
            const month = (yearInput.value && monthNumInput.value)
                ? `${yearInput.value}-${monthNumInput.value}`
                : "";
            const fileName = csvSelect.value;

            if (!month) {
                alert("대상 월(연도와 월)을 선택해 주세요.");
                return;
            }
            
            // 경과 시간(초)을 1초마다 버튼에 표시
            const startTime = Date.now();
            const renderBtnLabel = (sec) => `<span class="loader"></span> AI 분석 중... (${sec}초 경과)`;
            generateReportBtn.innerHTML = renderBtnLabel(0);
            generateReportBtn.disabled = true;
            const elapsedTimer = setInterval(() => {
                const sec = Math.floor((Date.now() - startTime) / 1000);
                generateReportBtn.innerHTML = renderBtnLabel(sec);
            }, 1000);

            try {
                const response = await fetch('/api/report/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, month, file_name: fileName })
                });
                
                const result = await response.json();
                
                if (!response.ok) {
                    const errorMsg = result.detail || "보고서 생성 실패";
                    throw new Error(errorMsg);
                }
                
                const reportMd = result.report;
                const reportTitle = `${month}_Litigation_Report`;
                if (reportResultContainer) {
                    // 결과 상단에 PDF 저장 버튼(고정 표시) + 본문
                    reportResultContainer.innerHTML =
                        `<div class="report-toolbar">
                            <button type="button" class="report-pdf-btn">📄 PDF 문서로 저장하기</button>
                         </div>` + marked.parse(reportMd);
                    reportResultContainer.style.display = 'block';
                    const topPdfBtn = reportResultContainer.querySelector('.report-pdf-btn');
                    if (topPdfBtn) topPdfBtn.onclick = () => downloadReportAsPdf(reportMd, reportTitle);
                }
                
            } catch (err) {
                console.error("Report Generation Error:", err);
                // fetch() 자체가 실패하면(TypeError) 서버에 닿지 못했거나 응답이 끊긴 것:
                // 서버 미실행/포트 오류 또는 보고서 생성이 길어져 연결이 타임아웃된 경우.
                // HTTP 오류 응답(예: API Key 미설정 500)은 위에서 throw new Error(detail)로 구분됨.
                const isNetworkError = (err instanceof TypeError);
                const helpHtml = isNetworkError
                    ? `<p>서버에 연결하지 못했거나 응답이 끊겼습니다. 다음을 확인해 주세요:</p>
                       <ul>
                         <li>대시보드 서버가 실행 중인지 (<code>http://localhost:8007</code>)</li>
                         <li>보고서 생성에 시간이 오래 걸려 연결이 끊겼는지 — 잠시 후 다시 시도</li>
                       </ul>`
                    : `<p>도움말: 서버 실행 시 <code>GEMINI_API_KEY</code> 환경변수가 올바르게 설정되었는지 확인해 주세요.</p>`;
                const alertHelp = isNetworkError
                    ? "서버 연결 실패 또는 응답 시간 초과입니다. 서버 실행 상태(http://localhost:8007)를 확인하고 잠시 후 다시 시도해 주세요."
                    : "만약 API Key 관련 오류라면, README.md의 'Gemini AI 설정' 가이드를 참고하여 환경변수(GEMINI_API_KEY)를 등록해 주세요.";
                alert(`⚠️ 오류 발생: ${err.message}\n\n도움말: ${alertHelp}`);
                if (reportResultContainer) {
                    reportResultContainer.innerHTML = `<div class="error-box"><h3>Report Generation Error</h3><p>${err.message}</p>${helpHtml}</div>`;
                    reportResultContainer.style.display = 'block';
                }
            } finally {
                clearInterval(elapsedTimer);
                generateReportBtn.innerHTML = '🚀 보고서 생성 시작';
                generateReportBtn.disabled = false;
            }
        };
    }

    const docSelect = document.getElementById('manual-select');
    if (docSelect) {
        docSelect.onchange = (e) => {
            const val = e.target.value;
            if (val) {
                openDocModal(val);
                // Reset select to placeholder
                e.target.value = "";
            }
        };
    }

    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.onchange = (e) => {
            const themes = ['theme-professional', 'theme-pet', 'theme-illustration', 'theme-fashion', 'theme-ux', 'theme-model', 'theme-blue', 'theme-black', 'theme-orange', 'theme-green', 'theme-purple'];
            themes.forEach(t => document.body.classList.remove(t));
            if (e.target.value !== 'none') {
                document.body.classList.add(`theme-${e.target.value}`);
            }
            localStorage.setItem('dashboard-theme', e.target.value);
        };
        const savedTheme = localStorage.getItem('dashboard-theme') || 'illustration';
        themeSelect.value = savedTheme;
        if (savedTheme !== 'none') document.body.classList.add(`theme-${savedTheme}`);
    }

    // Sidebar Page Size Control
    const sidebarPageSizeSelect = document.getElementById('sidebar-page-size');
    if (sidebarPageSizeSelect) {
        sidebarPageSizeSelect.onchange = (e) => {
            sidebarPageSize = parseInt(e.target.value);
            sidebarCurrentPage = 1;
            renderSidebar(sidebarAllCases);
        };
    }

    const statsMenuBtn = document.getElementById('stats-menu-btn');
    if (statsMenuBtn) {
        statsMenuBtn.onclick = async () => {
            document.getElementById('map-viewport').style.display = 'none';
            document.querySelector('.sidebar').style.display = 'none';
            document.getElementById('status-display').style.display = 'none';
            if (document.querySelector('.world-summary-container')) {
                document.querySelector('.world-summary-container').style.display = 'none';
            }
            document.getElementById('stats-container').style.display = 'block';
            await loadStatistics();
        };
    }
    const statsCloseBtn = document.getElementById('stats-close-btn');
    if (statsCloseBtn) {
        statsCloseBtn.onclick = () => {
            ensureMapView();
            refreshVisualization();
        };
    }

    // Global Modal Overlay Click Handler (Close on outside click)
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.style.display = 'none';
        }
    });

    // Dataset Search Logic
    // Dataset Search Logic
    const datasetSearchBtn = document.getElementById("header-dataset-search-btn") || document.getElementById("dataset-search-btn");
    const datasetSearchModal = document.getElementById("dataset-search-modal");
    const executeDatasetSearchBtn = document.getElementById("execute-dataset-search");
    const datasetQueryInput = document.getElementById("dataset-query-input");
    const datasetSearchResults = document.getElementById("dataset-search-results");
    const datasetSearchPageSizeSelect = document.getElementById("dataset-search-page-size");

    // Pagination State for Dataset Search
    let datasetSearchCurrentData = [];
    let datasetSearchCurrentPage = 1;
    let datasetSearchPageSize = 15;

    function renderDatasetSearchResults() {
        if (!datasetSearchResults) return;
        datasetSearchResults.innerHTML = "";
        const paginationContainer = document.getElementById('dataset-search-pagination');
        if (paginationContainer) paginationContainer.innerHTML = "";
        const lang = localStorage.getItem('dashboard-lang') || 'ko';

        if (datasetSearchCurrentData.length === 0) {
            datasetSearchResults.innerHTML = `<p class="empty-msg">${lang === 'ko' ? '결과가 없습니다.' : 'No results found.'}</p>`;
            return;
        }

        const totalPages = Math.ceil(datasetSearchCurrentData.length / datasetSearchPageSize);
        if (datasetSearchCurrentPage > totalPages) datasetSearchCurrentPage = totalPages;
        if (datasetSearchCurrentPage < 1) datasetSearchCurrentPage = 1;

        const start = (datasetSearchCurrentPage - 1) * datasetSearchPageSize;
        const end = start + datasetSearchPageSize;
        const paginatedCases = datasetSearchCurrentData.slice(start, end);

        const table = document.createElement('table');
        table.className = 'user-tools-table';
        
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>${lang === 'ko' ? '사건명' : 'Case Name'}</th>
                <th>${lang === 'ko' ? '피고' : 'Defendant'}</th>
                <th>${lang === 'ko' ? '대상 데이터' : 'Target Data'}</th>
                <th>${lang === 'ko' ? '제기일' : 'Filed Date'}</th>
                <th>${lang === 'ko' ? '진행상태' : 'Status'}</th>
            </tr>
        `;
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        paginatedCases.forEach(c => {
            const tr = document.createElement('tr');
            tr.onclick = () => {
                datasetSearchModal.style.display = "none";
                showCaseDetail(c);
            };
            const icon = typeof getCaseIcon === 'function' ? getCaseIcon(c) : '📄';
            tr.innerHTML = `
                <td class="col-name">
                    <div class="case-name-wrapper">
                        <span class="case-icon">${icon}</span>
                        <span class="case-title">${c.case_name || 'N/A'}</span>
                    </div>
                </td>
                <td class="col-defendant">${c.defendant || 'N/A'}</td>
                <td class="col-target">${c.target_data || 'N/A'}</td>
                <td class="col-date">${c.file_date || 'N/A'}</td>
                <td class="col-status"><span class="status-badge small">${c.status || 'N/A'}</span></td>
            `;
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        datasetSearchResults.appendChild(table);

        if (totalPages > 1 && paginationContainer) {
            const createBtn = (text, page, isActive = false) => {
                const btn = document.createElement('button');
                btn.className = isActive ? 'btn-primary' : 'btn-secondary';
                btn.textContent = text;
                btn.style.minWidth = '35px';
                btn.onclick = () => {
                    datasetSearchCurrentPage = page;
                    renderDatasetSearchResults();
                    datasetSearchResults.scrollTop = 0;
                };
                return btn;
            };
            if (datasetSearchCurrentPage > 1) paginationContainer.appendChild(createBtn('←', datasetSearchCurrentPage - 1));
            let startPage = Math.max(1, datasetSearchCurrentPage - 2);
            let endPage = Math.min(totalPages, startPage + 4);
            if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);
            for (let i = startPage; i <= endPage; i++) {
                paginationContainer.appendChild(createBtn(i, i, i === datasetSearchCurrentPage));
            }
            if (datasetSearchCurrentPage < totalPages) paginationContainer.appendChild(createBtn('→', datasetSearchCurrentPage + 1));
        }
    }

    if (datasetSearchBtn && datasetSearchModal) {
        datasetSearchBtn.onclick = () => {
            datasetSearchModal.style.display = "flex";
            if (datasetQueryInput) {
                datasetQueryInput.value = "";
                datasetQueryInput.focus();
            }
            datasetSearchCurrentData = [];
            datasetSearchCurrentPage = 1;
            renderDatasetSearchResults();
            if (datasetSearchResults) {
                datasetSearchResults.innerHTML = "<p class='empty-msg'>데이터셋 이름을 입력하고 조회 버튼을 눌러주세요.</p>";
            }
        };
        
        if (datasetSearchPageSizeSelect) {
            datasetSearchPageSizeSelect.onchange = (e) => {
                datasetSearchPageSize = parseInt(e.target.value);
                datasetSearchCurrentPage = 1;
                renderDatasetSearchResults();
            };
        }

        const performSearch = () => {
            const lang = localStorage.getItem('dashboard-lang') || 'ko';
            const query = datasetQueryInput.value.trim().toLowerCase();
            if (!query) {
                datasetSearchResults.innerHTML = `<p class='empty-msg'>${lang === 'ko' ? '데이터셋 이름을 입력해주세요.' : 'Please enter a dataset name.'}</p>`;
                return;
            }
            
            if (!allCases || allCases.length === 0) {
                datasetSearchResults.innerHTML = `<p class='empty-msg'>${lang === 'ko' ? '데이터가 로드되지 않았습니다. 지도를 먼저 갱신해주세요.' : 'Data not loaded. Please refresh map first.'}</p>`;
                return;
            }

            if (executeDatasetSearchBtn) {
                executeDatasetSearchBtn.innerHTML = `<span class="loader"></span> ${lang === 'ko' ? '조회 중...' : 'Searching...'}`;
                executeDatasetSearchBtn.disabled = true;
            }
            
            // Search across multiple relevant fields for a better user experience
            datasetSearchCurrentData = allCases.filter(c => {
                const searchFields = [
                    c.target_data, c['Target Data'], c['데이터셋'],
                    c.case_name, c.case_name_ko, c['Case Name'],
                    c.plaintiff, c['원고'],
                    c.defendant, c['피고']
                ];
                
                return searchFields.some(field => 
                    field && String(field).toLowerCase().includes(query)
                );
            });

            datasetSearchCurrentPage = 1;
            renderDatasetSearchResults();

            if (executeDatasetSearchBtn) {
                executeDatasetSearchBtn.innerHTML = lang === 'ko' ? '조회' : 'View';
                executeDatasetSearchBtn.disabled = false;
            }
        };

        if (executeDatasetSearchBtn) executeDatasetSearchBtn.onclick = performSearch;
        if (datasetQueryInput) datasetQueryInput.onkeypress = (e) => { if (e.key === "Enter") performSearch(); };
    }

    // 2. World Map (External SVG)
    try {
        await loadWorldMap();
        initWorldLabels();
    } catch (err) {
        console.error("World map initialization failed:", err);
    }

    // 3. Data Initialization Sequence
    try {
        // A. Load File List first
        await populateFileList();
        
        // B. Perform Initial Visualization (fetches allCases)
        await handleVisualize();
        
        // C. Initialize App (Listeners, Language, Tickers)
        await initApp();
        
    } catch (err) {
        console.error("Dashboard initialization failed:", err);
    }
    
    // 4. Final UI Adjustments
    setTimeout(() => {
        try {
            initUSLabels();
            // Final refresh to ensure everything is in sync
            refreshVisualization();
        } catch (e) {}
    }, 200);
});

// Helper to trigger visualization refresh without re-fetching data
function refreshVisualization() {
    if (allCases.length > 0) {
        const checkboxes = document.querySelectorAll('#status-dropdown input[type="checkbox"]');
        let selectedStatuses = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
        
        // Default to all statuses if the dropdown is missing or no selection made
        if (selectedStatuses.length === 0) {
            selectedStatuses = ['ready', 'started', 'first', 'second', 'judgment', 'appeal', 'closed'];
        }
        
        updateVisualization(allCases, selectedStatuses);
        updateSuitTicker();
        updateNewsTicker();
    }
}


async function loadWorldMap() {
    try {
        const response = await fetch('/img/world_map.svg');
        const text = await response.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(text, "image/svg+xml");
        const pathsGroup = xmlDoc.querySelector('g');
        const container = document.getElementById('world-paths');
        
        if (container && pathsGroup) {
            // Transfer paths and preserve IDs
            Array.from(pathsGroup.children).forEach(child => {
                const clone = child.cloneNode(true);
                // Standardize class for styling
                if (clone.tagName === 'path') {
                    clone.classList.add('state-path', 'country');
                } else if (clone.tagName === 'g') {
                    clone.classList.add('state-path', 'country');
                    clone.querySelectorAll('path').forEach(p => p.classList.add('state-path', 'country'));
                }
                container.appendChild(clone);
            });
        }
    } catch (err) {
        console.error("Failed to load world map:", err);
    }
}


function initMobileMenu() {
    const toggle = document.getElementById('mobile-menu-toggle');
    const controls = document.querySelector('.controls');
    if (toggle && controls) {
        toggle.onclick = (e) => {
            e.stopPropagation();
            controls.classList.toggle('show');
        };
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!controls.contains(e.target) && !toggle.contains(e.target)) {
                controls.classList.remove('show');
            }
        });
    }
}

async function initApp() {
    initTickers();
    // Initial data load will be triggered by setLanguage() or after initApp() completes

    // Dataset Visualization Trigger
    const visualizeBtn = document.getElementById('visualize-btn');
    if (visualizeBtn) {
        visualizeBtn.onclick = () => {
            handleVisualize();
        };
    }

    // Status Filter Dropdown Toggle
    const statusToggleBtn = document.getElementById('status-toggle-btn');
    const statusDropdown = document.getElementById('status-dropdown');
    if (statusToggleBtn && statusDropdown) {
        statusToggleBtn.onclick = (e) => {
            e.stopPropagation();
            const isVisible = statusDropdown.style.display === 'block';
            statusDropdown.style.display = isVisible ? 'none' : 'block';
            statusToggleBtn.classList.toggle('active', !isVisible);
        };

        document.addEventListener('click', (e) => {
            if (!statusToggleBtn.contains(e.target) && !statusDropdown.contains(e.target)) {
                statusDropdown.style.display = 'none';
                statusToggleBtn.classList.remove('active');
            }
        });

        // Update text when checkboxes change
        statusDropdown.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', () => {
                updateToggleBtnText();
                refreshVisualization();
            });
        });
    }

    
    // Search Functionality
    const searchInput = document.getElementById('case-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            sidebarCurrentPage = 1; // Reset to page 1 on search
            refreshVisualization();
        });
    }

    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    if (applyFiltersBtn) {
        applyFiltersBtn.onclick = () => {
            ensureMapView();
            refreshVisualization();
        };
    }

    // Language Selection Logic
    let currentLang = localStorage.getItem('dashboard-lang') || 'ko';
    const langSelect = document.getElementById('lang-select');

    const setLanguage = (lang) => {
        currentLang = lang;
        localStorage.setItem('dashboard-lang', lang);
        if (langSelect) langSelect.value = lang;

        // Update static elements with data-i18n
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) {
                el.textContent = TRANSLATIONS[lang][key];
            }
        });

        // Update placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) {
                el.placeholder = TRANSLATIONS[lang][key];
            }
        });

        // Refresh UI components that use currentLang
        updateToggleBtnText();
        if (allCases && allCases.length > 0) {
            updateStatusFilters(allCases);
        }
        
        refreshVisualization();
    };

    if (langSelect) {
        langSelect.addEventListener('change', (e) => setLanguage(e.target.value));
    }
    setLanguage(currentLang);
    loadAppVersion();

    
    


    // Initial UI state
    updateToggleBtnText();

    // Report modal handlers already attached in DOMContentLoaded
    
    const helpModal = document.getElementById('help-modal');
    const closeHelpBtn = document.getElementById('close-help-btn');

    if (helpModal && closeHelpBtn) {
        closeHelpBtn.addEventListener('click', () => {
            try {
                const dontShowCheckbox = document.getElementById('dont-show-guide');
                if (dontShowCheckbox) {
                    if (dontShowCheckbox.checked) {
                        localStorage.setItem('hide-user-guide', 'true');
                    } else {
                        localStorage.removeItem('hide-user-guide');
                    }
                }
            } catch (storageErr) {
                console.warn("Could not save guide preference:", storageErr);
            }
            helpModal.style.display = 'none';
        });
    }

    // Auto-show User Guide on first visit
    function initUserGuideAutoShow() {
        const hideGuide = localStorage.getItem('hide-user-guide');
        if (!hideGuide) {
            // Small delay to ensure everything is ready
            setTimeout(() => openDocModal('user'), 1000);
        }
    }
    initUserGuideAutoShow();

    // Consolidated Modal Background Click Handler
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.style.display = 'none';
        }
    });
}



let appVersionData = { version: 'unknown', commit: 'unknown' };

async function loadAppVersion() {
    const logoLink = document.getElementById('logo-link');
    if (!logoLink) return;

    try {
        const response = await fetch('/api/version');
        if (!response.ok) throw new Error("Version fetch failed");
        const data = await response.json();
        appVersionData = data;
        if (logoLink) logoLink.title = `Version: ${data.version}\nCommit: ${data.commit}\nDate: ${data.date}`;
        return data;
    } catch (err) {
        console.warn("Could not load app version:", err);
    }
}

async function openDocModal(type) {
    const helpModal = document.getElementById('help-modal');
    const helpContentPlaceholder = document.getElementById('help-content-placeholder');
    const modalTitle = helpModal ? helpModal.querySelector('h2') : null;
    const dontShowCheckbox = document.getElementById('dont-show-guide');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    if (helpModal) helpModal.style.display = 'flex';
    
    // Ensure version info is loaded before showing the manual
    if (appVersionData.version === 'unknown') {
        await loadAppVersion();
    }
    
    // Sync checkbox with localStorage
    if (dontShowCheckbox) {
        dontShowCheckbox.checked = localStorage.getItem('hide-user-guide') === 'true';
    }

    if (helpContentPlaceholder) {
        helpContentPlaceholder.innerHTML = '<p><span class="loader"></span> Loading documentation...</p>';
        try {
            let filePath = type === 'api' ? 'manual/api_guide.md' : 'manual/user_guide.md';
            if (lang === 'en') {
                filePath = filePath.replace('.md', '_en.md');
            }

            if (modalTitle) {
                if (type === 'api') {
                    modalTitle.innerText = TRANSLATIONS[lang].btn_api_manual;
                } else {
                    modalTitle.innerText = TRANSLATIONS[lang].btn_user_guide;
                }
            }
            
            const response = await fetch(filePath);
            if (!response.ok) throw new Error("Documentation file not found.");
            let markdown = await response.text();
            
            // Replace version placeholders
            markdown = markdown.replace(/{{APP_VERSION}}/g, appVersionData.version)
                               .replace(/{{COMMIT_HASH}}/g, appVersionData.commit)
                               .replace(/{{COMMIT_DATE}}/g, appVersionData.date);
            
            // Add a link to Swagger if it's the API manual
            if (type === 'api') {
                const tipTitle = lang === 'ko' ? '대화형 Swagger UI' : 'Interactive Swagger UI';
                const tipText = lang === 'ko' ? '모든 API를 직접 테스트해 볼 수 있습니다' : 'You can test all APIs directly';
                markdown = `> [!TIP]\n> **${tipTitle}**: ${tipText} [${window.location.origin}/docs](${window.location.origin}/docs)\n\n` + markdown;
            }
            
            helpContentPlaceholder.innerHTML = marked.parse(markdown);
        } catch (err) {
            helpContentPlaceholder.innerHTML = `<p class="error-msg">Failed to load document: ${err.message}</p>`;
        }
    }
}

// 마크다운 보고서를 '렌더링된 모습 그대로' PDF로 저장한다.
// 별도 PDF 라이브러리 없이, 깨끗한 인쇄용 문서를 새 창에 그려 브라우저의
// 인쇄 → 'PDF로 저장'을 띄운다. (원시 마크다운이 아니라 가독성 좋은 렌더 결과가 저장됨)
function downloadReportAsPdf(content, title) {
    try {
        const bodyHtml = (typeof marked !== 'undefined') ? marked.parse(content) : content;
        const win = window.open('', '_blank');
        if (!win) {
            alert("팝업이 차단되었습니다. 브라우저에서 팝업을 허용한 뒤 다시 시도해 주세요.");
            return;
        }
        const printCss = `
            @page { margin: 18mm; }
            * { box-sizing: border-box; }
            body { font-family: 'Malgun Gothic','Apple SD Gothic Neo','Noto Sans KR',sans-serif;
                   color:#1a1a1a; line-height:1.7; font-size:12pt; margin:0; }
            .doc-title { font-size:22pt; font-weight:800; color:#0b3d66; margin:0 0 2px; }
            .doc-meta { color:#666; font-size:10pt; margin-bottom:20px; border-bottom:2px solid #0b3d66; padding-bottom:10px; }
            h1,h2,h3 { color:#0b3d66; margin:1.3em 0 .5em; line-height:1.3; page-break-after:avoid; }
            h1 { font-size:18pt; } h2 { font-size:15pt; border-bottom:1px solid #ccc; padding-bottom:5px; } h3 { font-size:13pt; }
            p { margin:0 0 12px; } ul,ol { padding-left:22px; margin:0 0 12px; }
            li { margin-bottom:6px; }
            strong { color:#0b3d66; }
            table { border-collapse:collapse; width:100%; margin:14px 0; font-size:10.5pt; page-break-inside:avoid; }
            th,td { border:1px solid #999; padding:6px 9px; text-align:left; vertical-align:top; }
            th { background:#eef2f7; color:#0b3d66; }
            code { background:#f3f3f3; padding:1px 5px; border-radius:3px; font-size:0.92em; }
            blockquote { margin:14px 0; padding:10px 16px; background:#f5f8fc; border-left:4px solid #0b3d66; color:#333; }
        `;
        win.document.write(
            `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">` +
            `<title>${title}</title><style>${printCss}</style></head>` +
            `<body><div class="doc-title">AI 소송 월간 동향 보고서</div>` +
            `<div class="doc-meta">${title}</div>` +
            `${bodyHtml}</body></html>`
        );
        win.document.close();
        win.focus();
        // 콘텐츠가 그려진 뒤 인쇄 대화상자(→ PDF로 저장) 표시
        setTimeout(() => win.print(), 350);
    } catch (err) {
        alert("PDF 저장 중 오류가 발생했습니다: " + err.message);
    }
}

async function loadStatistics() {
    const fileName = document.getElementById('csv-select').value;
    const url = fileName ? `/api/statistics?file_name=${fileName}` : '/api/statistics';
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("통계 데이터 로드 실패");
        const stats = await response.json();
        
        renderStatsCard('stats-by-claim', stats.claim);
        renderStatsCard('stats-by-defendant', stats.defendant);
        renderStatsCard('stats-by-country', stats.country);
        renderStatsCard('stats-by-decision', stats.decision);
        renderStatsCard('stats-by-data', stats.target_data);
        
        initStatsDashboard(allCases);
    } catch (err) {
        console.error(err);
    }
}

function initStatsDashboard(cases) {
    if (!cases || cases.length === 0) return;
    
    try {
        // Populate Trend Filters (Country and Period)
        const trendCountrySelect = document.getElementById('trend-country-select');
        const trendStartInput = document.getElementById('trend-start-period');
        const trendEndInput = document.getElementById('trend-end-period');

        if (trendCountrySelect && trendStartInput && trendEndInput) {

        const countries = new Set();
        const periods = [];

        cases.forEach(c => {
            const country = (c.country || "").trim();
            if (country && country.toLowerCase() !== 'unknown') countries.add(country);
            
            const dateStr = (c.file_date || c.filing_date || c.date_filed || '').toString().trim();
            const match = dateStr.match(/^(\d{4})[./-]?(\d{2})/);
            if (match) periods.push(`${match[1]}-${match[2]}`);
        });

            
            const sortedCountries = Array.from(countries).sort();
            periods.sort();
            
            // Populate Country
            const curCountry = trendCountrySelect.value || 'all';
            trendCountrySelect.innerHTML = '<option value="all">전체 (All)</option>';
            sortedCountries.forEach(ctry => {
                const opt = document.createElement('option');
                opt.value = ctry; opt.textContent = ctry;
                trendCountrySelect.appendChild(opt);
            });
            trendCountrySelect.value = curCountry;

            // Set Min/Max and Initial Values for Month Inputs
            if (periods.length > 0) {
                const minPeriod = periods[0];
                const maxPeriod = periods[periods.length - 1];
                
                trendStartInput.min = minPeriod;
                trendStartInput.max = maxPeriod;
                trendEndInput.min = minPeriod;
                trendEndInput.max = maxPeriod;
                
                if (!trendStartInput.value) trendStartInput.value = minPeriod;
                if (!trendEndInput.value) trendEndInput.value = maxPeriod;
            }
            
            const trendViewUnit = document.getElementById('trend-view-unit');
            const trendChartType = document.getElementById('trend-chart-type');
            const trendStackCategory = document.getElementById('trend-stack-category');
            const trendStackGroup = document.getElementById('trend-stack-group');

            const refreshTrend = () => renderTrendStats(allCases);
            trendCountrySelect.onchange = refreshTrend;
            trendStartInput.oninput = refreshTrend; 
            trendStartInput.onchange = refreshTrend;
            trendEndInput.oninput = refreshTrend;
            trendEndInput.onchange = refreshTrend;
            if (trendViewUnit) trendViewUnit.onchange = refreshTrend;

            if (trendChartType) {
                trendChartType.onchange = (e) => {
                    if (trendStackGroup) {
                        trendStackGroup.style.display = e.target.value === 'stacked' ? 'flex' : 'none';
                    }
                    refreshTrend();
                };
            }
            if (trendStackCategory) trendStackCategory.onchange = refreshTrend;

            // Zoom Controls
            const btnZoomIn = document.getElementById('trend-zoom-in');
            const btnZoomOut = document.getElementById('trend-zoom-out');
            const btnZoomReset = document.getElementById('trend-zoom-reset');

            if (btnZoomIn) btnZoomIn.onclick = () => {
                trendZoomLevel = Math.min(trendZoomLevel + 0.25, 3.0);
                if (btnZoomReset) btnZoomReset.textContent = Math.round(trendZoomLevel * 100) + '%';
                refreshTrend();
            };
            if (btnZoomOut) btnZoomOut.onclick = () => {
                trendZoomLevel = Math.max(trendZoomLevel - 0.25, 0.25);
                if (btnZoomReset) btnZoomReset.textContent = Math.round(trendZoomLevel * 100) + '%';
                refreshTrend();
            };
            if (btnZoomReset) btnZoomReset.onclick = () => {
                trendZoomLevel = 1.0;
                btnZoomReset.textContent = '100%';
                refreshTrend();
            };
        }


        // Use the globally available allCases for trend calculation
        renderTrendStats(allCases);
        
    } catch (err) {
        console.error(err);
    }
}


function renderStatsCard(containerId, statsObj) {

    const card = document.getElementById(containerId);
    if (!card) return;
    const container = card.querySelector('.stats-content');
    const header = card.querySelector('h3');
    if (!container || !header) return;
    
    const lang = localStorage.getItem('dashboard-lang') || 'ko';
    
    const data = statsObj.data || {};
    const total = statsObj.total || 0;
    const categoryCount = Object.keys(data).length;

    // Map container ID to internal type
    const typeMap = {
        'stats-by-claim': 'claim',
        'stats-by-defendant': 'defendant',
        'stats-by-country': 'country',
        'stats-by-decision': 'decision',
        'stats-by-data': 'target_data'
    };
    const type = typeMap[containerId];

    // Update Header with counts
    const baseTitle = TRANSLATIONS[lang][`title_${type}`] || containerId;
    header.textContent = `${baseTitle}: ${total}${TRANSLATIONS[lang].count_unit} (${TRANSLATIONS[lang].category_count}: ${categoryCount}${TRANSLATIONS[lang].count_suffix})`;
    
    if (!data || categoryCount === 0) {
        container.innerHTML = `<p class="empty-msg">${TRANSLATIONS[lang].no_results}</p>`;
        return;
    }
    
    const max = Math.max(...Object.values(data));
    let html = `<table class="stats-table"><thead><tr><th>${TRANSLATIONS[lang].item}</th><th>${TRANSLATIONS[lang].count}</th></tr></thead><tbody>`;
    
    for (const [key, val] of Object.entries(data)) {
        const percentage = (val / max) * 100;
        const escapedKey = key.replace(/'/g, "\\'");
        const icon = getCategoryIcon(type, key);
        
        html += `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 0.9rem;">${icon}</span>
                        <div style="font-weight: 500;">${key}</div>
                    </div>
                    <div class="stats-bar-bg"><div class="stats-bar-fill" style="width: ${percentage}%"></div></div>
                </td>
                <td style="font-weight: 700; vertical-align: top; padding-top: 12px; white-space: nowrap;">
                    <a href="javascript:void(0)" class="stats-count-link" onclick="showCategoryCases('${type}', '${escapedKey}')">${val}</a>
                </td>
            </tr>
        `;
    }

    
    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Filter and show cases belonging to a specific statistics category
 */
function showCategoryCases(type, itemName) {
    if (!allCases || allCases.length === 0) {
        alert("No data loaded. Please refresh the map first.");
        return;
    }

    let filtered = [];

    // Local categorization logic matching backend/main.py
    filtered = allCases.filter(c => {
        if (type === 'claim') {
            const val = (c.reason || "").toLowerCase();
            if (itemName === '기타') {
                const isMatched = Object.values(CATEGORY_KEYWORDS.claim).some(keywords => 
                    keywords.some(kw => val.includes(kw.toLowerCase()))
                );
                return !isMatched && val !== "";
            }
            const keywords = CATEGORY_KEYWORDS.claim[itemName];
            return keywords && keywords.some(kw => val.includes(kw.toLowerCase()));
        } 
        
        if (type === 'target_data') {
            const val = (c.target_data || "").toLowerCase();
            if (itemName === 'Other') {
                const isMatched = Object.values(CATEGORY_KEYWORDS.target_data).some(keywords => 
                    keywords.some(kw => val.includes(kw.toLowerCase()))
                );
                return !isMatched && val !== "";
            }
            const keywords = CATEGORY_KEYWORDS.target_data[itemName];
            return keywords && keywords.some(kw => val.includes(kw.toLowerCase()));
        }

        if (type === 'defendant') {
            const val = (c.defendant || "").toLowerCase();
            if (itemName === '기타') return false; 
            return val.includes(itemName.toLowerCase());
        }

        if (type === 'country') {
            const val = (c.country || "").toLowerCase();
            return val === itemName.toLowerCase() || (itemName === '미국' && val === 'us') || (itemName === '한국' && val === 'kr');
        }

        if (type === 'decision') {
            const val = (c.status || "").toLowerCase();
            return val === itemName.toLowerCase();
        }

        return false;
    });

    if (filtered.length === 0) {
        alert("Could not find matching cases for " + itemName);
        return;
    }

    showCasesPopup(itemName, filtered);
}

function updateToggleBtnText() {
    const checkboxes = document.querySelectorAll('#status-dropdown input[type="checkbox"]');
    const selected = Array.from(checkboxes).filter(cb => cb.checked).map(cb => {
        const span = cb.nextElementSibling;
        const text = span ? span.textContent : "";
        return text.split('(')[0].trim();
    });

    const btn = document.getElementById('status-toggle-btn');
    const modalBtn = document.getElementById('status-toggle-btn-modal');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';
    
    let textContent = "";
    if (selected.length === 0) {
        textContent = TRANSLATIONS[lang].status_none_selected;
    } else if (selected.length === checkboxes.length) {
        textContent = TRANSLATIONS[lang].status_all;
    } else {
        textContent = TRANSLATIONS[lang].status_selected_label.replace('{count}', selected.length).replace('{first}', selected[0]);
    }

    if (btn) btn.textContent = textContent;
    if (modalBtn) modalBtn.textContent = textContent;
}

async function populateFileList() {
    try {
        const response = await fetch('/api/files');
        if (!response.ok) throw new Error("Failed to fetch files");
        const files = await response.json();
        const select = document.getElementById('csv-select');
        
        if (files.length > 0) {
            // Sort files descending just in case the API didn't
            files.sort((a, b) => b.localeCompare(a));

            select.innerHTML = ""; 
            files.forEach((file, index) => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                if (index === 0) option.selected = true; 
                select.appendChild(option);
            });
            // Force the select value to the first file
            select.value = files[0];
            console.log("Default dataset selected:", files[0]);
        } else {
            console.warn("No CSV files found in /api/files");
        }

    } catch (err) {
        console.error("Failed to load file list:", err);
    }
}

async function handleVisualize() {
    const lang = localStorage.getItem('dashboard-lang') || 'ko';
    const fileNameElement = document.getElementById('csv-select');
    if (!fileNameElement) return;
    const fileName = fileNameElement.value;
    
    const checkboxes = document.querySelectorAll('#status-dropdown input[type="checkbox"]');
    let selectedStatuses = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
    
    // Default to all statuses if no checkboxes found (UI removed)
    if (checkboxes.length === 0) {
        selectedStatuses = ['ready', 'started', 'first', 'second', 'judgment', 'appeal', 'closed'];
    } else if (selectedStatuses.length === 0) {
        alert(TRANSLATIONS[lang].alert_select_status);
        return;
    }

    const url = fileName ? `/api/cases?file_name=${fileName}` : '/api/cases';
    
    const btn = document.getElementById('visualize-btn');
    let originalText = "";
    if (btn) {
        originalText = btn.textContent;
        btn.innerHTML = `<span class="loader"></span> ${TRANSLATIONS[lang].updating}`;
        btn.disabled = true;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errBody = await response.json();
            throw new Error(errBody.detail || "Server error");
        }
        
        const result = await response.json();
        allCases = result.data || [];
        
        updateVisualization(allCases, selectedStatuses);
        updateSuitTicker();
        updateNewsTicker();

        // Close the modal if it was opened from the Load Dataset popup
        const datasetLoadModal = document.getElementById('dataset-load-modal');
        if (datasetLoadModal) datasetLoadModal.style.display = 'none';
    } catch (err) {
        console.error("Error fetching case data:", err);
        alert(TRANSLATIONS[lang].error_fetch_data + ": " + err.message);
    } finally {
        if (btn) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

function updateVisualization(cases, selectedStatuses) {
    if (!cases || !Array.isArray(cases)) {
        console.error("Invalid cases data", cases);
        return;
    }

    // Automatically switch back to map view if we are in Statistics or Detail view
    ensureMapView();
    
    // Reset sidebar pagination on each global refresh
    sidebarCurrentPage = 1;

    const countryType = document.getElementById('country-select').value;
    
    // Update the dropdown counts based on the current region view
    updateStatusFilterCounts(cases, countryType);

    const filtered = cases.filter(c => {
        if (!c.status) return false;
        const key = getStatusKey(c.status);
        
        // Status Filter
        const statusMatch = selectedStatuses.includes(key);
        if (!statusMatch) return false;

        return true;
    });


    // Store globally for search filtering
    currentFilteredCases = filtered;

    const stats = {};

    let maxCount = 0;

    // Calculate global metrics for metrics display
    const worldTotal = filtered.length;
    const usaCases = filtered.filter(c => {
        const country = (c.country || "").trim().toLowerCase();
        return country === 'us' || country === '미국' || country === 'usa';
    });
    const usaCount = usaCases.length;

    // 2. Further filter/group for visualization based on view (USA/World)
    let displaySet = (countryType === 'US') ? usaCases : filtered;

    // Apply Search Query filtering to the map view as well
    const searchInput = document.getElementById('case-search');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    if (query) {
        displaySet = displaySet.filter(c => {
            const q = query.toLowerCase();
            const searchFields = [
                c.case_name, c['Case Name'], c.case_name_ko,
                c.case_no, c['Case No'], c.case_number, c['소송번호'],
                c.defendant, c.Defendant, c['피고'],
                c.plaintiff, c.Plaintiff, c['원고'],
                c.court, c.Court, c['법원'],
                c.target_data, c['Target Data'], c['데이터셋'],
                c.system_id, c.id
            ];
            
            return searchFields.some(field => 
                field && String(field).toLowerCase().includes(q)
            );
        });
    }

    displaySet.forEach(c => {

        const id = extractLocation(c, countryType);
        if (id) {
            stats[id] = stats[id] || [];
            stats[id].push(c);
            maxCount = Math.max(maxCount, stats[id].length);
        }
    });

    // 3. Render all components
    currentVisibleCases = displaySet;
    renderStats(displaySet.length, selectedStatuses, countryType, worldTotal, usaCount, displaySet);
    toggleMapDisplay(countryType);
    renderMap(stats, countryType);
    renderSidebar(displaySet);
    renderSummaryTable(stats, displaySet.length, countryType);
}

function renderSidebar(cases, customTitle) {
    const list = document.getElementById('litigation-list');
    const title = document.getElementById('list-title');
    const searchInput = document.getElementById('case-search');
    const paginationContainer = document.getElementById('sidebar-pagination');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';
    
    if (!list) return;
    
    // Always sync with the global variable
    sidebarAllCases = cases || [];
    
    // 1. Apply Search Filter
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    let filteredCases = sidebarAllCases;
    if (query) {
        const q = query.toLowerCase();
        filteredCases = sidebarAllCases.filter(c => {
            const searchFields = [
                c.case_name, c['Case Name'], c.case_name_ko,
                c.case_no, c['Case No'], c.case_number, c['소송번호'],
                c.defendant, c.Defendant, c['피고'],
                c.plaintiff, c.Plaintiff, c['원고'],
                c.court, c.Court, c['법원'],
                c.target_data, c['Target Data'], c['데이터셋'],
                c.system_id, c.id
            ];
            return searchFields.some(field => 
                field && String(field).toLowerCase().includes(q)
            );
        });
    }

    list.innerHTML = "";

    // 2. Update Header Title
    if (title) {
        if (customTitle) {
            title.innerHTML = customTitle;
        } else {
            const baseTitle = TRANSLATIONS[lang].case_details_title || 'Case Details';
            title.innerHTML = `${baseTitle} <span style="font-size: 0.85em; opacity: 0.8; font-weight: 700;">(${filteredCases.length})</span>`;

        }
    }

    // 3. Handle Empty State
    if (filteredCases.length === 0) {
        let msg = query 
            ? (TRANSLATIONS[lang].empty_msg_no_query || 'No cases found for "{query}".').replace('{query}', query)
            : (TRANSLATIONS[lang].empty_msg_no_search || 'No cases match the selected filters.');
        list.innerHTML = `<p class="empty-msg">${msg}</p>`;
        if (paginationContainer) paginationContainer.innerHTML = "";
        return;
    }

    // 4. Pagination Slicing
    // Ensure sidebarPageSize is valid
    const pageSize = parseInt(sidebarPageSize) || 15;
    const totalPages = Math.ceil(filteredCases.length / pageSize);
    
    if (sidebarCurrentPage > totalPages) sidebarCurrentPage = totalPages;
    if (sidebarCurrentPage < 1) sidebarCurrentPage = 1;

    const start = (sidebarCurrentPage - 1) * pageSize;
    const end = start + pageSize;
    const paginatedCases = filteredCases.slice(start, end);

    // 5. Render Page Items
    paginatedCases.forEach((c, index) => {
        const item = document.createElement('div');
        item.className = 'case-item';
        item.style.animationDelay = `${index * 0.03}s`;
        
        const icon = getCaseIcon(c);
        
        item.innerHTML = `
            <div class="case-title">${icon} ${c.case_name || 'Untitled Case'}</div>
            <div class="case-meta">
                <span class="meta-icon">📍</span> ${c.court || TRANSLATIONS[lang].unknown_court}
                <span class="meta-sep">|</span>
                <span class="meta-status">${c.status || TRANSLATIONS[lang].status_na}</span>
            </div>
        `;
        item.onclick = () => showCaseDetail(c);
        list.appendChild(item);
    });

    // 6. Render Pagination Controls
    renderSidebarPagination(filteredCases.length);
}

function renderSidebarPagination(totalItems) {
    const container = document.getElementById('sidebar-pagination');
    if (!container) return;
    
    container.innerHTML = "";
    const pageSize = parseInt(sidebarPageSize) || 15;
    const totalPages = Math.ceil(totalItems / pageSize);
    if (totalPages <= 1) return;

    // Page Info (e.g., "1 - 15 of 27")
    const start = (sidebarCurrentPage - 1) * pageSize + 1;
    const end = Math.min(sidebarCurrentPage * pageSize, totalItems);
    const info = document.createElement('div');
    info.style.width = '100%';
    info.style.textAlign = 'center';
    info.style.fontSize = '0.7rem';
    info.style.color = 'var(--text-muted)';
    info.style.marginBottom = '10px';
    info.textContent = `${start} - ${end} of ${totalItems}`;
    container.appendChild(info);

    const btnWrapper = document.createElement('div');
    btnWrapper.style.display = 'flex';
    btnWrapper.style.justifyContent = 'center';
    btnWrapper.style.gap = '5px';
    btnWrapper.style.width = '100%';

    const createBtn = (text, page, isActive = false, isDisabled = false) => {
        const btn = document.createElement('button');
        btn.className = `pagination-btn ${isActive ? 'active' : ''}`;
        btn.textContent = text;
        btn.disabled = isDisabled;
        if (!isDisabled && !isActive) {
            btn.onclick = () => {
                sidebarCurrentPage = page;
                renderSidebar(sidebarAllCases);
                const list = document.getElementById('litigation-list');
                if (list) list.scrollTop = 0;
            };
        }
        return btn;
    };

    // Prev Button
    btnWrapper.appendChild(createBtn('«', sidebarCurrentPage - 1, false, sidebarCurrentPage === 1));

    // Page Numbers
    let startPage = Math.max(1, sidebarCurrentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    if (endPage === totalPages) startPage = Math.max(1, endPage - 4);

    for (let i = startPage; i <= endPage; i++) {
        btnWrapper.appendChild(createBtn(i, i, i === sidebarCurrentPage));
    }

    // Next Button
    btnWrapper.appendChild(createBtn('»', sidebarCurrentPage + 1, false, sidebarCurrentPage === totalPages));
    
    container.appendChild(btnWrapper);
}

function extractCountry(countryText) {
    if (!countryText) return null;
    return COUNTRY_MAP[countryText] || null;
}

function extractState(courtText) {
    if (!courtText) return null;
    const upper = courtText.toUpperCase();
    
    // 1. Try common court patterns first (e.g. N.D. Cal.)
    // We already have these in STATE_ABBR as 'CAL.', 'N.Y.', etc.
    
    // Priority: Long names first to avoid 'MA' matching 'MAINE' early
    const sortedStates = Object.entries(STATE_ABBR).sort((a, b) => b[0].length - a[0].length);
    
    for (const [fullName, abbr] of sortedStates) {
        // If it's a short 2-letter abbreviation, use word boundaries or specific delimiters
        if (fullName.length <= 3) {
             // Match " CA ", ", CA", "(CA)", " CA," or "CA."
             const regex = new RegExp(`(^|[^A-Z])${fullName.replace('.', '\\.')}([^A-Z]|$)`, 'i');
             if (regex.test(upper)) return abbr;
        } else {
             // For long names, simple include check is usually fine
             if (upper.includes(fullName)) return abbr;
        }
    }

    // Fallback: check if the text itself IS the abbreviation
    if (upper.length === 2 && Object.values(STATE_ABBR).includes(upper)) {
        return upper;
    }

    return null;
}

function renderStats(total, selectedStatuses, selectedCountry, worldTotal, usaCount, currentCases) {
    const badgeContainer = document.getElementById('status-count-badges');
    const shareContainer = document.getElementById('share-info');
    const totalValEl = document.getElementById('total-count-val');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    if (totalValEl) totalValEl.textContent = total;
    
    if (shareContainer) {
        if (selectedCountry === 'US' && worldTotal > 0) {
            const share = Math.round((usaCount / worldTotal) * 100);
            shareContainer.textContent = `${TRANSLATIONS[lang].share_info_label} = ${usaCount}/${worldTotal} (${share}%)`;
            shareContainer.style.display = 'block';
            shareContainer.style.color = '#ff4d4d'; // Set to bright red
            shareContainer.style.fontWeight = '800';
        } else {
            shareContainer.style.display = 'none';
        }
    }
    
    // Render Status-wise Badges in Sidebar
    if (badgeContainer && currentCases) {
        badgeContainer.innerHTML = '';
        const lang = localStorage.getItem('dashboard-lang') || 'ko';
        
        // Count specific statuses found in the data
        const counts = {};
        currentCases.forEach(c => {
            const s = c.status || 'Unknown';
            let group = '기타';
            if (s.includes('준비')) group = 'st_ready';
            else if (s.includes('항소')) group = 'st_appeal';
            else if (s.includes('제기') || s.includes('시작')) group = 'st_started';
            else if (s.includes('1심')) group = 'st_first';
            else if (s.includes('2심')) group = 'st_second';
            else if (s.includes('판결')) group = 'st_judgment';
            else if (s.includes('종')) group = 'st_closed';
            
            counts[group] = (counts[group] || 0) + 1;
        });

        const labelToKey = {
            'st_ready': 'ready',
            'st_started': 'started',
            'st_first': 'first',
            'st_second': 'second',
            'st_judgment': 'judgment',
            'st_appeal': 'appeal',
            'st_closed': 'closed'
        };

        const displayOrder = ['준비 중', '소 제기됨', '1심 진행중', '2심 진행중', '판결 선고', '항소 제기됨', '사건 종결'];

        displayOrder.forEach(label => {
            const count = counts[label] || 0;
            const badge = document.createElement('div');
            badge.className = `status-badge-item ${count > 0 ? 'active' : ''}`;
            badge.innerHTML = `
                <span class="label">${label}</span>
                <span class="count">${count}</span>
            `;
            badge.onclick = () => {
                if (count > 0) showStatusCasesModal(label, labelToKey[label]);
            };
            badgeContainer.appendChild(badge);
        });
    }

    const chipsContainer = document.getElementById('active-status-chips');
    if (chipsContainer) {
        chipsContainer.innerHTML = "";
        
        // Define the standard mapping for map-top chips
        const chipMapping = [
            { key: 'ready', label: '준비중' },
            { key: 'started', label: '소 제기됨' },
            { key: 'first', label: '1심 진행중' },
            { key: 'second', label: '2심 진행중' },
            { key: 'judgment', label: '판결 선고' },
            { key: 'appeal', label: '항소 제기됨' },
            { key: 'closed', label: '사건 종결' }
        ];

        // Recalculate counts based on CURRENTly displayed cases (currentCases)
        // to show accurate counts for the current region
        const regionCounts = {};
        currentCases.forEach(c => {
            const key = getStatusKey(c.status);
            regionCounts[key] = (regionCounts[key] || 0) + 1;
        });


        chipMapping.forEach(item => {
            const count = regionCounts[item.key] || 0;
            const chip = document.createElement('span');
            chip.className = 'status-chip';
            // Highlight if this status is currently active in the filter
            if (selectedStatuses.includes(item.key)) {
                chip.classList.add('active');
            }
            chip.textContent = `${item.label}(${count})`;
            
            if (count > 0) {
                chip.style.cursor = 'pointer';
                chip.onclick = () => showStatusCasesModal(item.label, item.key);
            }
            
            chipsContainer.appendChild(chip);
        });
    }
}

function initLabels() {
    // This function is now just a fallback or convenience
    initUSLabels();
    initWorldLabels();
}


function initUSLabels() {
    const usMap = document.getElementById('us-map');
    if (!usMap) return;
    
    const labelGroup = document.getElementById('state-labels');
    if (!labelGroup) return;
    
    // Force temporary display to get correct BBox coordinates if map is hidden
    const wasHidden = usMap.style.display === 'none';
    if (wasHidden) usMap.style.display = 'block';
    
    labelGroup.innerHTML = '';
    
    const adjustments = {
        'FL': { dx: 3, dy: 1 }, 'MI': { dx: 1, dy: 2 }, 'LA': { dx: -1, dy: 0 },
        'CA': { dx: -1, dy: 0 }, 'AK': { dx: 0, dy: -2 }, 'HI': { dx: 0, dy: -2 },
        'NJ': { dx: 1, dy: 0 }, 'MD': { dx: 1, dy: 0 }, 'MA': { dx: 1, dy: -1 },
        'VT': { dx: 0, dy: -1 }, 'NH': { dx: 1, dy: 1 }, 'ME': { dx: 2, dy: 0 }
    };

    document.querySelectorAll('#us-map .state-path').forEach(path => {
        const id = path.id;
        if (!id || id.length !== 2) return;

        const bbox = path.getBBox();
        if (bbox.width === 0) return; // Skip if still zero

        let x = bbox.x + bbox.width / 2;
        let y = bbox.y + bbox.height / 2;

        if (id === 'DC') {
            x = 148.5; y = 62.5;
        }

        if (adjustments[id]) {
            x += adjustments[id].dx;
            y += adjustments[id].dy;
        }

        createLabel(labelGroup, x, y, id, 'state-label us-label', '');
    });

    if (wasHidden) usMap.style.display = 'none';
}

function initWorldLabels() {
    const worldMap = document.getElementById('world-map');
    if (!worldMap) return;

    const labelGroup = document.getElementById('world-labels');
    if (!labelGroup) return;

    const wasHidden = worldMap.style.display === 'none';
    if (wasHidden) worldMap.style.display = 'block';

    labelGroup.innerHTML = '';

    const countryPaths = new Map();
    
    // Systemic offsets for world map coordinates (x, y)
    const WORLD_OFFSETS = {
        'us': { dx: 15, dy: 10 },
        'ca': { dx: 0, dy: 15 },
        'fr': { dx: 0, dy: -5 },
        'uk': { dx: -5, dy: -5 },
        'de': { dx: 0, dy: -5 },
        'it': { dx: 0, dy: 2 },
        'ru': { dx: 0, dy: 10 },
        'cn': { dx: 0, dy: 10 },
        'au': { dx: 0, dy: 5 },
        'br': { dx: 0, dy: 5 }
    };

    document.querySelectorAll('#world-paths .state-path').forEach(el => {
        const id = el.id || (el.parentElement && el.parentElement.id);
        if (!id || id.length > 3) return;

        let targetEl = el;
        if (el.tagName === 'g') {
            const mainland = el.querySelector('.mainland');
            if (mainland) {
                targetEl = mainland;
            } else {
                let maxArea = -1;
                el.querySelectorAll('path').forEach(p => {
                    const b = p.getBBox();
                    const a = b.width * b.height;
                    if (a > maxArea) {
                        maxArea = a;
                        targetEl = p;
                    }
                });
            }
        }

        let bbox;
        try {
            bbox = targetEl.getBBox();
        } catch(e) {
            return;
        }
        
        if (bbox.width === 0) return;

        const area = bbox.width * bbox.height;
        if (!countryPaths.has(id) || area > countryPaths.get(id).area) {
            countryPaths.set(id, { bbox, area });
        }
    });

    countryPaths.forEach((data, id) => {
        const { bbox } = data;
        let x = bbox.x + bbox.width / 2;
        let y = bbox.y + bbox.height / 2;

        const offset = WORLD_OFFSETS[id.toLowerCase()];
        if (offset) {
            x += offset.dx;
            y += offset.dy;
        }

        createLabel(labelGroup, x, y, id, 'state-label world-label', '');
    });

    if (wasHidden) worldMap.style.display = 'none';
}

function createLabel(group, x, y, id, className, textContent) {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', x);
    text.setAttribute('y', y);
    text.setAttribute('class', className);
    text.setAttribute('data-loc', id);
    text.setAttribute('dominant-baseline', 'middle');
    text.textContent = textContent;
    group.appendChild(text);
    return text;
}


function renderMap(stats, countryType) {
    const selector = countryType === 'US' ? '#us-map .state-path' : '#world-paths .state-path';
    const paths = document.querySelectorAll(selector);
    
    const counts = Object.values(stats).map(c => c.length);
    const maxCount = counts.length > 0 ? Math.max(...counts) : 1;

    // Reset all paths first
    paths.forEach(el => {
        el.classList.remove('has-cases', 'selected-location');
        el.removeAttribute('data-count');
        el.style.removeProperty('--intensity');
        el.onclick = null; // Clear old handlers
    });

    paths.forEach(el => {
        const id = el.id || (el.parentElement && el.parentElement.id);
        if (!id || id === 'world-paths' || id === 'us-map' || id === 'map-svg-wrapper') return;

        const cases = stats[id] || [];
        const baseDisplayCode = (COUNTRY_LABEL_OVERRIDE[id] || id).toUpperCase();
        const fullName = FULL_NAMES[id];
        const displayInfo = fullName ? `${baseDisplayCode} (${fullName})` : baseDisplayCode;
        
        // Target labels specifically within the active map container to avoid conflicts
        const labelSelector = countryType === 'US' 
            ? `#us-map .state-label[data-loc="${id}"]` 
            : `#world-map .state-label[data-loc="${id}"]`;
        const labelElem = document.querySelector(labelSelector);

        // Tooltip logic
        el.onmouseenter = (e) => showTooltip(e, `${displayInfo}: ${cases.length} litigation(s)`);
        el.onmousemove = (e) => {
            const tt = document.getElementById('tooltip');
            if (tt) {
                tt.style.left = e.pageX + 'px';
                tt.style.top = e.pageY + 'px';
            }
        };
        el.onmouseleave = hideTooltip;

        // Label update
        if (labelElem) {
            if (cases.length > 0) {
                labelElem.textContent = `${baseDisplayCode} (${cases.length})`;
                labelElem.classList.add('active-label');
                labelElem.setAttribute('visibility', 'visible');
            } else {
                labelElem.textContent = '';
                labelElem.classList.remove('active-label');
                labelElem.setAttribute('visibility', 'hidden');
            }
        }

        if (cases.length > 0) {
            el.classList.add('has-cases');
            el.setAttribute('data-count', cases.length);
            const intensity = 0.3 + (0.7 * (Math.log(cases.length + 1) / Math.log(maxCount + 1)));
            el.style.setProperty('--intensity', intensity);
        }

        // Unified click handler with bubble support
        el.onclick = (e) => {
            e.stopPropagation();
            document.querySelectorAll('.state-path').forEach(p => p.classList.remove('selected-location'));
            
            // Highlight the entire group or path
            if (el.tagName === 'g') {
                el.classList.add('selected-location');
            } else if (el.parentElement && el.parentElement.tagName === 'g' && el.parentElement.id === id) {
                el.parentElement.classList.add('selected-location');
            } else {
                el.classList.add('selected-location');
            }
            
            filterSidebarByLocation(displayInfo, cases);
        };
    });

    // Add background click listener to reset
    const container = countryType === 'US' ? document.getElementById('us-map') : document.getElementById('world-paths');
    if (container) {
        container.onclick = (e) => {
            if (e.target === container || e.target.id === 'world-map') {
                resetSidebar();
            }
        };
    }
}

function filterSidebarByLocation(locationName, cases) {
    const customTitle = `Case Details in ${locationName} <button class="btn-reset-sidebar" onclick="resetSidebar()">✕</button>`;
    renderSidebar(cases, customTitle);
}

function resetSidebar() {
    const title = document.getElementById('list-title');
    if (title) title.textContent = `Case Details (${currentFilteredCases.length})`;
    
    document.querySelectorAll('.state-path').forEach(p => p.classList.remove('selected-location'));
    renderSidebar(currentFilteredCases);
}

function extractLocation(c, type) {
    if (type === 'US') {
        return extractState(c.court);
    } else {
        return extractCountry(c.country);
    }
}

function ensureMapView() {
    const statsContainer = document.getElementById('stats-container');
    const mapViewport = document.getElementById('map-viewport');
    const sidebar = document.querySelector('.sidebar');
    const statusDisplay = document.getElementById('status-display');
    const caseDetailView = document.getElementById('case-detail-view');
    const summaryContainer = document.getElementById('map-summary-container');

    const userToolsView = document.getElementById('user-tools-view');

    if (statsContainer) statsContainer.style.display = 'none';
    if (userToolsView) userToolsView.style.display = 'none';
    const radarOverlay = document.getElementById('radar-overlay');
    if (radarOverlay) radarOverlay.style.display = 'none';
    
    if (mapViewport) mapViewport.style.display = 'block';
    if (sidebar) sidebar.style.display = 'flex';
    if (statusDisplay) statusDisplay.style.display = 'block';
    if (caseDetailView) caseDetailView.style.display = 'none';
    if (summaryContainer && summaryContainer.getAttribute('data-visible') === 'true') {
        summaryContainer.style.display = 'block';
    }
}

function toggleMapDisplay(country) {
    const usMap = document.getElementById('us-map');
    const worldMap = document.getElementById('world-map');
    const summaryBtn = document.getElementById('open-summary-modal-btn');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    if (country === 'US') {
        if (usMap) usMap.style.display = 'block';
        if (worldMap) worldMap.style.display = 'none';
        if (summaryBtn) summaryBtn.textContent = TRANSLATIONS[lang].btn_regional_summary;
        initUSLabels();
        resetTransform(); 
    } else {
        if (usMap) usMap.style.display = 'none';
        if (worldMap) worldMap.style.display = 'block';
        if (summaryBtn) summaryBtn.textContent = TRANSLATIONS[lang].btn_regional_summary_world;
        initWorldLabels();
        resetTransform();
    }
}

function getCaseIcon(c) {
    const target = (c.target_data || '').toLowerCase();
    const reason = (c.reason || '').toLowerCase();
    const fullText = `${target} ${reason}`;

    let matchedCategory = "Other";
    
    // Find matching category based on keywords
    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS.target_data)) {
        if (keywords.some(kw => fullText.includes(kw.toLowerCase()))) {
            matchedCategory = category;
            break;
        }
    }

    const icon = (CATEGORY_ICONS.target_data && CATEGORY_ICONS.target_data[matchedCategory]) || "📦";
    
    // Return icon wrapped in a styled span for a badge-like look
    return `<span class="case-category-icon" title="${matchedCategory}">${icon}</span>`;
}

function getStatusKey(status) {
    if (!status) return 'unknown';
    const s = status.toLowerCase();
    
    // Order matters to avoid keyword collisions (e.g., '항소 제기' contains both)
    if (s.includes('준비')) return 'ready';
    if (s.includes('항소')) return 'appeal';
    if (s.includes('2심')) return 'second';
    if (s.includes('1심')) return 'first';
    if (s.includes('판결')) return 'judgment';
    if (s.includes('제기') || s.includes('시작')) return 'started';
    if (s.includes('종') || s.includes('결')) return 'closed';
    
    return 'other';
}



function cleanText(text) {
    if (!text) return '';
    return text.split('\n').filter(line => {
        // Filter out log-style lines (e.g., Name/Team/Status/Date)
        const isLogLine = line.includes('/') && line.match(/\d{4}-\d{2}-\d{2}/);
        return !isLogLine;
    }).join('\n').trim();
}

function parseUpdateStatus(remarks) {
    if (!remarks || !remarks.includes('##')) return '';

    // Split by '##' but keep the header part for parsing
    const updates = remarks.split(/(?=##)/);
    
    let html = '<div class="update-timeline">';
    
    updates.forEach(update => {
        const lines = update.trim().split('\n');
        if (lines.length < 1) return;

        // Parse Header: ## (Status), YYYY-MM-DD, Title
        const headerLine = lines[0].replace('##', '').trim();
        const headerParts = headerLine.split(',').map(p => p.trim());
        
        const statusMatch = headerParts[0] ? headerParts[0].match(/\((.*?)\)/) : null;
        const status = statusMatch ? statusMatch[1] : 'Updated';
        const date = headerParts[1] || '';
        const title = headerParts.slice(2).join(', ') || 'Update';

        // Parse remaining lines for link and description
        let link = '';
        let contentLines = [];
        
        lines.slice(1).forEach(line => {
            const trimmed = line.trim();
            if (!trimmed) return;
            if (trimmed.startsWith('http')) {
                link = trimmed;
            } else {
                contentLines.push(trimmed);
            }
        });

        const statusClass = status.toLowerCase() === 'started' ? 'tag-started' : 'tag-updated';
        let content = cleanText(contentLines.join('\n'));
        
        // Use marked if available for content formatting
        if (typeof marked !== 'undefined') {
            content = marked.parse(content);
        } else {
            content = `<p>${content.replace(/\n/g, '<br>')}</p>`;
        }

        html += `
            <div class="update-item">
                <div class="update-header">
                    <div class="update-badges">
                        <span class="update-tag ${statusClass}">${status}</span>
                    </div>
                    <span class="update-date">${date}</span>
                </div>
                <div class="update-title">${title}</div>
                ${link ? `<a href="${link}" target="_blank" class="update-link">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    관련 기사 보기
                </a>` : ''}
                <div class="update-content">${content}</div>
            </div>
        `;
    });

    html += '</div>';
    return html;
}

function parseProceedingsResult(result) {
    if (!result || result === "N/A" || result === "Unknown") return '';
    
    const lines = result.split('\n').filter(l => l.trim());
    if (lines.length === 0) return '';

    let html = '<div class="result-list">';
    
    lines.forEach((line, index) => {
        // Pattern: (Status), Date, Title
        const parts = line.split(',').map(p => p.trim());
        if (parts.length >= 2) {
            const statusMatch = parts[0].match(/\((.*?)\)/);
            const status = statusMatch ? statusMatch[1] : 'Updated';
            const date = parts[1];
            const content = parts.slice(2).join(', ');
            
            const statusClass = status.toLowerCase() === 'started' ? 'tag-started' : 'tag-updated';
            
            html += `
                <div class="result-card" style="animation-delay: ${index * 0.05}s">
                    <div class="result-card-header">
                        <span class="update-tag ${statusClass}">${status}</span>
                        <span class="result-date">${date}</span>
                    </div>
                    <div class="result-card-content">${content}</div>
                </div>
            `;
        } else {
            // Fallback for simple lines
            html += `
                <div class="result-card simple" style="animation-delay: ${index * 0.05}s">
                    ${line}
                </div>
            `;
        }
    });

    html += '</div>';
    return html;
}

function parseHistoryCards(text) {
    if (!text) return '';
    
    // Clean log lines first
    const cleaned = cleanText(text);
    const lines = cleaned.split('\n').filter(l => l.trim());
    
    let html = '';
    let currentParagraphs = [];
    
    lines.forEach((line, index) => {
        const parts = line.split(',').map(p => p.trim());
        // Check if line matches "(Status), Date, ..."
        if (parts.length >= 2 && parts[0].includes('(') && parts[0].includes(')')) {
            // If we had accumulated paragraphs, flush them
            if (currentParagraphs.length > 0) {
                html += `<div class="history-summary-box">${currentParagraphs.map(p => `<p>${p}</p>`).join('')}</div>`;
                currentParagraphs = [];
            }
            
            const statusMatch = parts[0].match(/\((.*?)\)/);
            const status = statusMatch ? statusMatch[1] : 'Updated';
            const date = parts[1];
            const content = parts.slice(2).join(', ');
            const statusClass = status.toLowerCase() === 'started' ? 'tag-started' : 'tag-updated';
            
            html += `
                <div class="result-card" style="margin-bottom: 12px;">
                    <div class="result-card-header">
                        <span class="update-tag ${statusClass}">${status}</span>
                        <span class="result-date">${date}</span>
                    </div>
                    <div class="result-card-content">${content}</div>
                </div>
            `;
        } else {
            currentParagraphs.push(line);
        }
    });
    
    if (currentParagraphs.length > 0) {
        html += `<div class="history-summary-box">${currentParagraphs.map(p => `<p>${p}</p>`).join('')}</div>`;
    }
    
    return html;
}


function formatCaseSummary(text) {
    if (!text) return "<p>No detailed summary available.</p>";

    const lines = text.split('\n').map(l => l.trim()).filter(l => l !== '');
    let html = '<div class="summary-container-v5">';
    
    let currentBoxContent = "";

    const formatLine = (line) => {
        return line.replace(/^([^:]+:)/, '<strong style="color: black;">$1</strong>');
    };

    lines.forEach((line, index) => {
        const isNewSection = line.startsWith('*') || line.startsWith('##');
        
        if (isNewSection) {
            // If we have previous content, close that box first
            if (currentBoxContent) {
                html += `
                    <div class="summary-grey-card">
                        <div class="card-body">${currentBoxContent}</div>
                    </div>
                `;
                currentBoxContent = "";
            }
            // Start new content for this section (remove symbols)
            let cleanedLine = line.replace(/^[\*#\s]+/, '').trim();
            currentBoxContent = formatLine(cleanedLine);
        } else {
            // Append to current box content as a new paragraph without extra spacing
            if (currentBoxContent) {
                currentBoxContent += `<br>${formatLine(line)}`;
            } else {
                // If no box started yet, start one with this line
                currentBoxContent = formatLine(line);
            }
        }

        // If it's the last line, close the box
        if (index === lines.length - 1 && currentBoxContent) {
            html += `
                <div class="summary-grey-card">
                    <div class="card-body">${currentBoxContent}</div>
                </div>
            `;
        }
    });

    html += '</div>';
    return html;
}

function showStatusCasesModal(statusLabel, statusKey) {

    const cases = (currentVisibleCases || []).filter(c => getStatusKey(c.status) === statusKey);
    
    const list = document.getElementById('litigation-list');
    const title = document.getElementById('list-title');
    
    if (title) title.innerHTML = `Case Details: ${statusLabel} <button class="btn-reset-sidebar" onclick="resetSidebar()">✕</button>`;
    
    renderSidebar(cases);
}


function showCaseDetail(c) {
    const caseDetailView = document.getElementById('case-detail-view');
    const mainDetailContent = document.getElementById('main-detail-content');
    const mapViewport = document.getElementById('map-viewport');
    const statusDisplay = document.getElementById('status-display');
    const summaryContainer = document.getElementById('map-summary-container');

    if (!caseDetailView || !mainDetailContent) return;

    // Highlight selected item in sidebar
    document.querySelectorAll('.case-item').forEach(el => el.classList.remove('selected'));
    const items = document.querySelectorAll('.case-item');
    for (let item of items) {
        if (item.querySelector('.case-title').textContent.includes(c.case_name)) {
            item.classList.add('selected');
            break;
        }
    }

    const firstUrl = c.url ? c.url.split(' ')[0] : '#';
    const isPreparing = c.status && c.status.includes("준비");
    const reasonText = c.reason || "N/A";
    const updateStatusHtml = parseUpdateStatus(c.remarks);
    const icon = getCaseIcon(c);

    // Store visibility of summary container
    if (summaryContainer) {
        summaryContainer.setAttribute('data-visible', summaryContainer.style.display !== 'none');
        summaryContainer.style.display = 'none';
    }

    mainDetailContent.innerHTML = `
        <div class="detail-header">
            <div class="header-main">
                <h3 class="detail-main-title">${icon} ${c.case_name}</h3>
                <div class="case-number-badge detail-case-no">Case No: ${c.case_no || 'Unknown'}</div>
            </div>
            <span class="status-badge large detail-status-badge">${c.status}</span>
        </div>

        <div class="detail-grid full-grid detail-main-grid">
            <div class="field"><span>System ID</span><strong>${c.system_id || 'N/A'}</strong></div>
            <div class="field"><span>Filed Date</span><strong>${c.file_date}</strong></div>
            <div class="field"><span>Court</span><strong>${c.court}</strong></div>
            <div class="field"><span>Country</span><strong>${c.country || 'US'}</strong></div>
            <div class="field"><span>Plaintiff</span><strong>${c.plaintiff}</strong></div>
            <div class="field"><span>Defendant</span><strong>${c.defendant}</strong></div>
            <div class="field"><span>Plaintiff Lawyer</span><strong>${c.plaintiff_lawyer || 'N/A'}</strong></div>
            <div class="field"><span>Defendant Lawyer</span><strong>${c.defendant_lawyer || 'N/A'}</strong></div>
        </div>

        <div class="detail-grid detail-sub-grid">
            <div class="field"><span>Target Data (대상 데이터)</span><strong>${c.target_data || 'N/A'}</strong></div>
            <div class="field"><span>Target Product (대상 제품)</span><strong>${c.target_product || 'N/A'}</strong></div>
        </div>

        <div class="detail-section highlight detail-reason-section">
            <h4>Litigation Reason (소송 이유)</h4>
            <p class="detail-reason-text">${reasonText}</p>
        </div>

        <div class="detail-section foldable-section active detail-summary-section" onclick="this.classList.toggle('active')">
            <div class="fold-icon">▼</div>
            <h4>Full Case Summary</h4>
            <div class="foldable-content">
                <div class="summary-text">
                    ${formatCaseSummary(c.summary)}
                </div>
            </div>
        </div>

        ${updateStatusHtml ? `
        <div class="detail-section detail-updates-section">
            <h4>Update Status (업데이트 현황)</h4>
            ${updateStatusHtml}
            <div class="last-update-tag">Last Update: ${c.last_update || 'N/A'}</div>
        </div>
        ` : `
        <div class="detail-section">
            <div class="last-update-tag">Last Update: ${c.last_update || 'N/A'}</div>
        </div>
        `}

        <div class="detail-actions main-detail-actions">
            ${isPreparing ? `
                <div class="warning-box animate-in">
                    <span class="warning-icon">⚠️</span>
                    <span>Legal documents have not yet been publicly uploaded to CourtListener for this case.</span>
                </div>
            ` : `
                <a href="${firstUrl}" target="_blank" class="btn-primary detail-primary-btn">View Full Docket on CourtListener</a>
            `}
        </div>
    `;

    caseDetailView.style.display = 'block';
    mapViewport.style.display = 'none';
    statusDisplay.style.display = 'none';
    
    // Smooth scroll to top
    caseDetailView.scrollTop = 0;
}

// Modals are now handled by a consolidated event listener in the initialization section

function showTooltip(e, text) {
    const tt = document.getElementById('tooltip');
    if (!tt) return;
    tt.textContent = text;
    tt.style.display = 'block';
    // Position exactly at cursor; CSS transform (-50%, -100%) handles centering above
    tt.style.left = e.pageX + 'px';
    tt.style.top = e.pageY + 'px';
}


function hideTooltip() {
    const tt = document.getElementById('tooltip');
    if (tt) tt.style.display = 'none';
}

// Map Zoom and Pan Logic
let currentScale = 1;
let translateX = 0;
let translateY = 0;
let isDragging = false;
let isSelecting = false;
let startX, startY;
let selectStartX, selectStartY;

function initMapControls() {
    const viewport = document.getElementById('map-viewport');
    const zoomIn = document.getElementById('zoom-in');
    const zoomOut = document.getElementById('zoom-out');
    const zoomReset = document.getElementById('zoom-reset');
    const continentSelect = document.getElementById('continent-select');
    const box = document.getElementById('selection-box');

    if (!viewport || !zoomIn || !zoomOut || !zoomReset) return;

    if (continentSelect) {
        continentSelect.onchange = (e) => {
            const continent = e.target.value;
            if (continent) {
                zoomToContinent(continent);
            }
        };
    }

    // Zoom Buttons
    zoomIn.onclick = (e) => { e.stopPropagation(); updateTransform(0.2); };
    zoomOut.onclick = (e) => { e.stopPropagation(); updateTransform(-0.2); };
    zoomReset.onclick = (e) => { e.stopPropagation(); resetTransform(); };

    // Mouse Wheel - Unified Pivot Zoom
    viewport.onwheel = (e) => {
        // [FIX] Require Ctrl/Cmd key to zoom. This prevents accidental map zoom while scrolling the sidebar or page.
        if (!e.ctrlKey && !e.metaKey) return; 

        e.preventDefault();
        e.stopPropagation();

        // [FIX] More consistent zoom factor across different devices/browsers
        const delta = -e.deltaY;
        const factor = Math.pow(1.1, Math.sign(delta) * 0.5); 
        
        const oldScale = currentScale;
        currentScale = Math.min(Math.max(currentScale * factor, 0.5), 100);

        if (currentScale !== oldScale) {
            const vRect = viewport.getBoundingClientRect();
            
            // [FIX] Pivot point relative to viewport. 
            // We clamp these to the viewport bounds to prevent the map from "flying away" 
            // if the mouse is outside the viewport (e.g., in the sidebar).
            let mouseX = e.clientX - vRect.left;
            let mouseY = e.clientY - vRect.top;
            
            mouseX = Math.max(0, Math.min(vRect.width, mouseX));
            mouseY = Math.max(0, Math.min(vRect.height, mouseY));

            const actualFactor = currentScale / oldScale;

            translateX = mouseX - (mouseX - translateX) * actualFactor;
            translateY = mouseY - (mouseY - translateY) * actualFactor;
            
            applyTransform();
        }
    };

    // Modes: Shift+Drag for Box, Drag for Pan
    viewport.onmousedown = (e) => {
        if (e.button !== 0) return;

        if (e.shiftKey) {
            e.preventDefault();
            isSelecting = true;
            selectStartX = e.clientX;
            selectStartY = e.clientY;
            
            document.body.style.userSelect = 'none';
            viewport.style.cursor = 'crosshair';

            if (box) {
                const vRect = viewport.getBoundingClientRect();
                box.style.display = 'block';
                box.style.left = `${e.clientX - vRect.left}px`;
                box.style.top = `${e.clientY - vRect.top}px`;
                box.style.width = '0px';
                box.style.height = '0px';
            }
        } else {
            isDragging = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
            viewport.style.cursor = 'grabbing';
            isSelecting = false; // Guard
        }
    };

    window.onmousemove = (e) => {
        if (isDragging) {
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            applyTransform();
        } else if (isSelecting && box) {
            const vRect = viewport.getBoundingClientRect();
            const x = Math.min(selectStartX, e.clientX);
            const y = Math.min(selectStartY, e.clientY);
            const w = Math.abs(e.clientX - selectStartX);
            const h = Math.abs(e.clientY - selectStartY);

            box.style.left = `${x - vRect.left}px`;
            box.style.top = `${y - vRect.top}px`;
            box.style.width = `${w}px`;
            box.style.height = `${h}px`;
        }
    };

    window.onmouseup = () => {
        if (isSelecting) {
            isSelecting = false;
            document.body.style.userSelect = '';
            viewport.style.cursor = 'grab';
            
            if (box) {
                const boxRect = box.getBoundingClientRect();
                box.style.display = 'none';
                if (boxRect.width > 20 && boxRect.height > 20) {
                    zoomToBox(boxRect);
                }
            }
        }
        isDragging = false;
        if (viewport && viewport.style.cursor === 'grabbing') {
            viewport.style.cursor = 'grab';
        }
    };
}

function zoomToContinent(continent) {
    const countries = CONTINENTS[continent];
    if (!countries) return;

    // Reset transform first to ensure bounding box calculations are based on scale 1
    resetTransform();

    // Switch to World Map if not already there
    const countrySelect = document.getElementById('country-select');
    if (countrySelect && countrySelect.value !== 'WORLD') {
        countrySelect.value = 'WORLD';
        toggleMapDisplay('WORLD');
    }
    
    // Always trigger a refresh to ensure the map labels and data are correctly rendered
    refreshVisualization();

    // Wait for the map and labels to be fully rendered before performing the zoom
    setTimeout(() => performContinentalZoom(countries, continent), 300);
}

function performContinentalZoom(countries, continent) {
    const worldMap = document.getElementById('world-map');
    if (!worldMap) return;

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    let found = false;

    countries.forEach(id => {
        // Try both lowercase and uppercase IDs
        const el = document.getElementById(id) || document.getElementById(id.toUpperCase());
        if (el && el.getBBox) {
            const bbox = el.getBoundingClientRect();
            if (bbox.width > 0 && bbox.height > 0) {
                minX = Math.min(minX, bbox.left);
                minY = Math.min(minY, bbox.top);
                maxX = Math.max(maxX, bbox.right);
                maxY = Math.max(maxY, bbox.bottom);
                found = true;
            }
        }
    });

    if (found) {
        const boxRect = {
            left: minX,
            top: minY,
            right: maxX,
            bottom: maxY,
            width: maxX - minX,
            height: maxY - minY
        };
        
        // Special case: Americas is very tall, so we might want to zoom in a bit more
        let padding = 0.9;
        if (continent === 'AMERICAS') padding = 1.4; // Focused zoom for Americas
        if (continent === 'EUROPE') padding = 1.1;   // Slightly tighter for Europe
        if (continent === 'ASIA PACIFIC') padding = 1.3; // Focused zoom for Asia Pacific to exclude Europe
        if (continent === 'MIDDLE EAST') padding = 1.5; // Very focused for Middle East
        if (continent === 'AFRICA') padding = 1.1;      // Tighter for Africa
        
        zoomToBox(boxRect, padding);
    }
}

function zoomToBox(boxRect, customPadding) {
    const viewport = document.getElementById('map-viewport');
    if (!viewport) return;

    const vRect = viewport.getBoundingClientRect();
    const screenCX = (boxRect.left + boxRect.right) / 2 - vRect.left;
    const screenCY = (boxRect.top + boxRect.bottom) / 2 - vRect.top;

    const padding = customPadding || 0.9;
    const factor = Math.min(vRect.width / boxRect.width, vRect.height / boxRect.height) * padding;
    
    const oldScale = currentScale;
    currentScale = Math.min(Math.max(currentScale * factor, 0.5), 100);

    const actualChange = currentScale / oldScale;
    
    translateX = (vRect.width / 2) - (screenCX - translateX) * actualChange;
    translateY = (vRect.height / 2) - (screenCY - translateY) * actualChange;

    applyTransform();
}

function updateTransform(delta) {
    const oldScale = currentScale;
    const factor = delta > 0 ? 1.25 : 0.8;
    currentScale = Math.min(Math.max(currentScale * factor, 0.5), 100);
    
    if (currentScale !== oldScale) {
        const viewport = document.getElementById('map-viewport');
        if (viewport) {
            const vRect = viewport.getBoundingClientRect();
            const cx = vRect.width / 2;
            const cy = vRect.height / 2;
            const actualFactor = currentScale / oldScale;
            translateX = cx - (cx - translateX) * actualFactor;
            translateY = cy - (cy - translateY) * actualFactor;
        }
        applyTransform();
    }
}



function resetTransform() {
    currentScale = 1;
    translateX = 0;
    translateY = 0;
    const continentSelect = document.getElementById('continent-select');
    if (continentSelect) continentSelect.value = "";
    applyTransform();
}



function applyTransform() {
    const wrapper = document.getElementById('map-svg-wrapper');
    if (wrapper) {
        wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${currentScale})`;
        wrapper.style.setProperty('--map-scale', currentScale);
    }
}

// RESTORED SUMMARY TABLE AND CSV EXPORT Logic
function renderSummaryTable(stats, total, type) {
    const container = document.getElementById('map-summary-container');
    const wrapper = document.getElementById('stats-table-wrapper');
    const titleEl = document.getElementById('summary-title');
    const textSummary = document.getElementById('text-summary');
    const exportBtn = document.getElementById('export-csv-btn');
    const openBtn = document.getElementById('open-summary-modal-btn');
    const modal = document.getElementById('map-summary-modal');

    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    if (!container || total === 0) {
        if (openBtn) openBtn.style.display = 'none';
        return;
    }

    if (openBtn) {
        openBtn.style.display = 'inline-block';
        openBtn.onclick = () => {
            if (modal) modal.style.display = 'flex';
        };
    }
    if (titleEl) {
        titleEl.textContent = type === 'WORLD' ? TRANSLATIONS[lang].summary_title_world : TRANSLATIONS[lang].summary_title_us;
    }

    // Sort stats
    const sorted = Object.entries(stats)
        .map(([loc, cases]) => ({
            loc,
            count: cases.length,
            share: ((cases.length / total) * 100).toFixed(1)
        }))
        .sort((a, b) => b.count - a.count);

    let html = `
        <table class="stats-table summary-stats-table">
            <thead>
                <tr>
                    <th>${type === 'WORLD' ? TRANSLATIONS[lang].col_loc_world : TRANSLATIONS[lang].col_loc_us}</th>
                    <th>${TRANSLATIONS[lang].col_count}</th>
                    <th>${TRANSLATIONS[lang].col_share}</th>
                </tr>
            </thead>
            <tbody>
    `;

    sorted.forEach(item => {
        const displayCode = item.loc.toUpperCase();
        const fullName = FULL_NAMES[item.loc] || FULL_NAMES[item.loc.toLowerCase()] || "";
        const locDisplayName = fullName ? `${displayCode} (${fullName})` : displayCode;
        
        html += `
            <tr>
                <td>${locDisplayName}</td>
                <td class="count-col"><b>${item.count}</b></td>
                <td class="share-col">
                    <div class="share-bar-container">
                        <div class="share-bar-bg">
                            <div class="share-bar" style="width: ${item.share}%"></div>
                        </div>
                        <span class="share-val">${item.share}%</span>
                    </div>
                </td>
            </tr>
        `;
    });

    html += `
            <tr class="total-row">
                <td>TOTAL</td>
                <td>${total}</td>
                <td>100%</td>
            </tr>
        </tbody>
    </table>`;

    if (wrapper) wrapper.innerHTML = html;

    // Generate textual summary
    let summaryText = "";
    if (type === 'WORLD') {
        const top3 = sorted.slice(0, 3).map(x => `${x.loc.toUpperCase()}(${x.count}${lang === 'ko' ? '건' : ''})`).join(", ");
        summaryText = TRANSLATIONS[lang].summary_text_world.replace('{total}', total).replace('{top3}', top3);
    } else {
        const top3 = sorted.slice(0, 3).map(x => `${x.loc}(${x.count}${lang === 'ko' ? '건' : ''})`).join(", ");
        summaryText = TRANSLATIONS[lang].summary_text_us.replace('{total}', total).replace('{top3}', top3);
    }
    
    if (textSummary) textSummary.innerHTML = summaryText;

    // Hook up export button
    if (exportBtn) {
        exportBtn.onclick = () => exportToCSV(sorted, total, type);
    }
}

function exportToCSV(data, total, type) {
    let csv = "\uFEFF"; // UTF-8 BOM for Excel
    csv += (type === 'WORLD' ? "Country" : "State") + ",Count,Share (%)\n";
    
    data.forEach(item => {
        const displayCode = item.loc.toUpperCase();
        const fullName = FULL_NAMES[item.loc] || FULL_NAMES[item.loc.toLowerCase()] || "";
        const locDisplayName = fullName ? `${displayCode} (${fullName})` : displayCode;
        csv += `"${locDisplayName}",${item.count},${item.share}\n`;
    });
    
    csv += `TOTAL,${total},100\n`;
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    const dateStr = new Date().toISOString().slice(0, 10);
    
    link.setAttribute("href", url);
    link.setAttribute("download", `litigation_report_${type.toLowerCase()}_${dateStr}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Updates the status filter dropdown labels with real-time counts based on the current region.
 * @param {Array} cases - All cases in the current dataset.
 * @param {string} countryType - 'US' or 'WORLD'.
 */
function updateStatusFilterCounts(cases, countryType) {
    const regionCases = cases.filter(c => {
        if (countryType === 'WORLD') return true;
        const country = (c.country || "").trim().toLowerCase();
        return country === 'us' || country === '미국' || country === 'usa';
    });

    const counts = {};
    regionCases.forEach(c => {
        const key = getStatusKey(c.status);
        counts[key] = (counts[key] || 0) + 1;
    });

    const dropdown = document.getElementById('status-dropdown');
    if (!dropdown) return;

    const items = [
        { key: 'ready', label: '준비 중', meta: 'Ready' },
        { key: 'started', label: '소 제기됨', meta: 'Started' },
        { key: 'first', label: '1심 진행중', meta: '1st Instance' },
        { key: 'second', label: '2심 진행중', meta: '2nd Instance' },
        { key: 'judgment', label: '판결 선고', meta: 'Decision' },
        { key: 'appeal', label: '항소 제기됨', meta: 'Appeal' },
        { key: 'closed', label: '사건 종결', meta: 'Closed' }
    ];

    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    items.forEach(item => {
        const checkbox = dropdown.querySelector(`input[value="${item.key}"]`);
        if (checkbox) {
            const span = checkbox.nextElementSibling;
            if (span) {
                const count = counts[item.key] || 0;
                const localizedLabel = TRANSLATIONS[lang][`st_${item.key}`] || item.label;
                span.textContent = `${localizedLabel} (${count})`;
            }
        }
    });

    // Update User Tools Status Chips
    const statusChipsContainer = document.getElementById('user-tools-status-chips');
    if (statusChipsContainer) {
        statusChipsContainer.innerHTML = "";
        
        // Add "All" chip
        const allChip = document.createElement('div');
        allChip.className = 'status-chip active';
        allChip.setAttribute('data-value', 'all');
        allChip.textContent = `${TRANSLATIONS[lang].status_all || '전체'}`;
        allChip.onclick = () => {
            statusChipsContainer.querySelectorAll('.status-chip').forEach(c => c.classList.remove('active'));
            allChip.classList.add('active');
        };
        statusChipsContainer.appendChild(allChip);

        items.forEach(item => {
            const count = counts[item.key] || 0;
            const localizedLabel = TRANSLATIONS[lang][`st_${item.key}`] || item.label;
            const chip = document.createElement('div');
            chip.className = 'status-chip';
            chip.setAttribute('data-value', item.key);
            chip.textContent = `${localizedLabel} (${count})`;
            chip.onclick = () => {
                allChip.classList.remove('active');
                chip.classList.toggle('active');
                // If no chips active, select All
                if (statusChipsContainer.querySelectorAll('.status-chip.active').length === 0) {
                    allChip.classList.add('active');
                }
            };
            statusChipsContainer.appendChild(chip);
        });
    }
}


/**
 * Populates Defendant and Target Data filter dropdowns based on current dataset.
 */

/**
 * Renders chronological litigation trend in statistics view.
 */

function renderTrendStats(cases) {
    const card = document.getElementById('stats-by-trend');
    const countryFilter = document.getElementById('trend-country-select');
    const startFilter = document.getElementById('trend-start-period');
    const endFilter = document.getElementById('trend-end-period');
    const viewUnit = document.getElementById('trend-view-unit')?.value || 'month';
    const chartType = document.getElementById('trend-chart-type')?.value || 'single';
    const stackCategory = document.getElementById('trend-stack-category')?.value || 'reason';

    if (!card) return;
    const container = card.querySelector('.stats-content');
    if (!container) return;

    const isExpanded = card.classList.contains('expanded');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';
    
    let filteredCases = cases;
    if (countryFilter && countryFilter.value !== 'all') {
        filteredCases = filteredCases.filter(c => (c.country || '').trim() === countryFilter.value);
    }
    
    // 1. Identify valid categories (Top N) to match the statistical cards
    const groupCounts = {};
    filteredCases.forEach(c => {
        let rawVal = 'N/A';
        if (stackCategory === 'claim') {
            const v = (c.reason || "").toLowerCase();
            for (const [catName, keywords] of Object.entries(CATEGORY_KEYWORDS.claim)) {
                if (keywords.some(kw => v.includes(kw.toLowerCase()))) { rawVal = catName; break; }
            }
        } else if (stackCategory === 'target_data') {
            const v = (c.target_data || "").toLowerCase();
            for (const [catName, keywords] of Object.entries(CATEGORY_KEYWORDS.target_data)) {
                if (keywords.some(kw => v.includes(kw.toLowerCase()))) { rawVal = catName; break; }
            }
        } else if (stackCategory === 'defendant') {
            rawVal = (c.defendant || 'N/A').split(/[;,]/)[0].trim();
        } else if (stackCategory === 'country') {
            rawVal = (c.country || 'N/A');
        } else if (stackCategory === 'decision') {
            rawVal = (c.status || 'N/A');
        }
        if (rawVal && rawVal !== 'N/A') groupCounts[rawVal] = (groupCounts[rawVal] || 0) + 1;
    });

    const limits = { claim: 7, defendant: 15, country: 12, decision: 7, target_data: 9 };
    const limit = limits[stackCategory] || 15;
    
    const topGroups = Object.entries(groupCounts)
        .sort((a,b) => b[1] - a[1])
        .slice(0, limit)
        .map(([name]) => name);
    const validGroups = new Set(topGroups);

    const trend = {};
    const trendCases = {}; 

    const startKey = startFilter ? startFilter.value : '';
    const endKey = endFilter ? endFilter.value : '9999-99';

    filteredCases.forEach(c => {
        const dateStr = (c.file_date || c.filing_date || c.date_filed || '').toString().trim();
        const match = dateStr.match(/^(\d{4})[./-]?(\d{2})/);
        if (match) {
            const y = match[1];
            const m = match[2];
            const key = viewUnit === 'year' ? y : (y + '-' + m);
            
            let isInRange = false;
            if (viewUnit === 'year') {
                isInRange = key >= startKey.substring(0,4) && key <= endKey.substring(0,4);
            } else {
                isInRange = key >= startKey && key <= endKey;
            }

            if (isInRange) {
                trend[key] = (trend[key] || 0) + 1;
                if (!trendCases[key]) trendCases[key] = [];
                trendCases[key].push(c);
            }
        }
    });
    
    const fullTimeline = [];
    if (startKey && endKey) {
        if (viewUnit === 'year') {
            let startY = parseInt(startKey.substring(0,4));
            let endY = parseInt(endKey.substring(0,4));
            for (let y = startY; y <= endY; y++) {
                fullTimeline.push(y.toString());
            }
        } else {
            let cur = new Date(startKey + '-01');
            const last = new Date(endKey + '-01');
            let safety = 0;
            while (cur <= last && safety < 120) {
                const y = cur.getFullYear();
                const m = (cur.getMonth() + 1).toString().padStart(2, '0');
                fullTimeline.push(`${y}-${m}`);
                cur.setMonth(cur.getMonth() + 1);
                safety++;
            }
        }
    }
    
    const sortedKeys = fullTimeline.length > 0 ? fullTimeline : Object.keys(trend).sort();
    if (sortedKeys.length === 0) {
        container.innerHTML = `<p class="empty-msg">${(lang === 'en') ? 'No valid date data found.' : '데이터가 부족하여 추이를 표시할 수 없습니다.'}</p>`;
        return;
    }
    
    let runningTotal = 0;
    const runningTrend = {};
    sortedKeys.forEach(key => {
        runningTotal += (trend[key] || 0);
        runningTrend[key] = runningTotal;
    });

    // Optimize Y-axis Max to ensure clean grid steps and adequate headroom (approx 40% buffer)
    const rawMax = chartType === 'stacked' ? runningTotal : Math.max(...Object.values(trend));
    const maxVal = rawMax || 1;
    let yAxisMaxFinal;
    
    // Provide enough headroom so labels above bars aren't clipped
    const suggestedMax = maxVal * 1.4;
    
    if (suggestedMax <= 10) yAxisMaxFinal = 15;
    else if (suggestedMax <= 25) yAxisMaxFinal = 30;
    else if (suggestedMax <= 50) yAxisMaxFinal = 60;
    else if (suggestedMax <= 100) yAxisMaxFinal = 120;
    else if (suggestedMax <= 200) yAxisMaxFinal = 250;
    else yAxisMaxFinal = Math.ceil(suggestedMax / 50) * 50;
    
    const chartHeight = isExpanded ? 550 : 260;
    const paddingBottom = isExpanded ? 60 : 45;
    const barAreaHeight = chartHeight - paddingBottom;

    // Build Grid Lines (5 levels)
    let gridLinesHtml = '';
    const stepCount = 5;
    for (let i = 0; i <= stepCount; i++) {
        const labelVal = Math.round((yAxisMaxFinal / stepCount) * (stepCount - i));
        const topPos = (i / stepCount) * 100;
        gridLinesHtml += `
            <div style="position: absolute; width: 100%; top: ${topPos}%; border-top: 1px dashed rgba(255,255,255,${i === stepCount ? '0.2' : '0.08'}); z-index: 1;">
                <span style="position: absolute; left: -55px; top: 0; transform: translateY(-50%); font-size: ${(isExpanded ? 1.0 : 0.8)}rem; font-weight: 800; color: var(--primary-bright); width: 45px; text-align: right; text-shadow: 0 1px 3px rgba(0,0,0,0.5);">${labelVal}</span>
            </div>`;
    }

    let html = `
        <div class="excel-chart-container" style="position: relative; height: ${chartHeight}px; margin-top: 40px; border-left: 2px solid var(--border); border-bottom: 2px solid var(--border); padding-left: 10px;">
            <div class="axis-label-y" style="left: -80px; font-weight: 900; color: var(--text-muted);">${TRANSLATIONS[lang].axis_y_cases || '소송 건수'}</div>
            <div class="axis-label-x" style="bottom: -50px;">${TRANSLATIONS[lang].axis_x_time || '시기'}</div>
            <div class="grid-lines-container" style="position: absolute; width: 100%; height: ${barAreaHeight}px; bottom: ${paddingBottom}px; left: 0; pointer-events: none;">
                ${gridLinesHtml}
            </div>
            
            <div class="trend-chart-scroll" id="trend-chart-scroll" style="display: flex; align-items: flex-end; gap: ${(isExpanded ? 12 : 8) * trendZoomLevel}px; height: ${chartHeight}px; overflow-x: auto; position: relative; z-index: 2; scrollbar-width: thin; padding-left: 10px; box-sizing: border-box;">
    `;

    const PALETTE = [
        '#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', 
        '#8b5cf6', '#f43f5e', '#06b6d4', '#84cc16', '#fb923c'
    ];

    let sortedCats = [];
    let catColorMap = {};
    if (chartType === 'stacked') {
        const allCats = new Set();
        filteredCases.forEach(c => allCats.add(getTrendGroupValue(c, stackCategory, lang, validGroups, topGroups)));
        sortedCats = Array.from(allCats).sort((a, b) => {
            // Sort 'Other'/'기타' to the end, then sort by total counts globally so larger items get consistent top colors
            if (a === '기타' || a === 'Other') return 1;
            if (b === '기타' || b === 'Other') return -1;
            const countA = groupCounts[a] || 0;
            const countB = groupCounts[b] || 0;
            if (countB !== countA) return countB - countA;
            return a.localeCompare(b);
        });
        sortedCats.forEach((cat, idx) => {
            catColorMap[cat] = PALETTE[idx % PALETTE.length];
        });
    }

    const barWidth = (isExpanded ? 60 : 36) * trendZoomLevel;

    sortedKeys.forEach((key, idx) => {
        const monthlyTotal = trend[key] || 0;
        const displayTotal = chartType === 'stacked' ? (runningTrend[key] || 0) : monthlyTotal;
        const heightPct = (displayTotal / yAxisMaxFinal) * 100;
        const periodCases = trendCases[key] || [];

        let labelTop = '';
        let labelBottom = '';
        if (viewUnit === 'year') {
            labelTop = key; // Year
            labelBottom = '';
        } else {
            const parts = key.split('-');
            labelTop = parts[1] || '';
            labelBottom = parts[0] || '';
        }
        
        let barInnerHtml = '';
        if (chartType === 'stacked') {
            const subGroups = {};
            const allCasesSoFar = [];
            for(let i=0; i<=idx; i++) {
                const k = sortedKeys[i];
                if (trendCases[k]) allCasesSoFar.push(...trendCases[k]);
            }
            allCasesSoFar.forEach(c => {
                let val = getTrendGroupValue(c, stackCategory, lang, validGroups, topGroups);
                subGroups[val] = (subGroups[val] || 0) + 1;
            });
            const sortedSubs = Object.entries(subGroups).sort((a, b) => b[1] - a[1]);
            sortedSubs.forEach(([name, count], sIdx) => {
                const sHeightPct = (count / displayTotal) * 100;
                const color = catColorMap[name] || PALETTE[0];
                barInnerHtml += `<div class="bar-segment" style="height: ${sHeightPct}%; width: 100%; background: ${color}; border-top: 1px solid rgba(255,255,255,0.15); transition: all 0.3s; box-sizing: border-box;" title="${name}: ${count}건 (누적)"></div>`;
            });
        } else {
            barInnerHtml = `<div class="excel-bar" style="height: 100%; width: 100%; background: linear-gradient(180deg, var(--primary-bright) 0%, var(--primary) 100%); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px 6px 0 0; position: relative; transition: all 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.2);"></div>`;
        }

        let caseIds = (chartType === 'stacked') 
            ? Array.from({length: idx + 1}, (_, i) => trendCases[sortedKeys[i]] || []).flat().map(c => String(c.system_id || c.id)).join(',')
            : periodCases.map(c => String(c.system_id || c.id)).join(',');
        
        html += `
            <div class="excel-bar-item" 
                 style="flex: 0 0 ${barWidth}px; display: flex; flex-direction: column; align-items: center; height: ${chartHeight}px; justify-content: flex-end; cursor: pointer; position: relative;" 
                 data-period="${key}" data-ids="${caseIds}" data-count="${displayTotal}"
                 onclick="event.stopPropagation(); handleTrendClick(this)">
                <div style="width: 100%; height: ${barAreaHeight}px; position: absolute; bottom: ${paddingBottom}px; left: 0; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; pointer-events: none;">
                    <div class="bar-value-label" style="position: absolute; bottom: calc(${heightPct}% + 5px); left: 50%; transform: translateX(-50%); font-size: ${(isExpanded ? 0.95 : 0.75) * Math.max(0.7, trendZoomLevel)}rem; font-weight: 900; color: var(--primary-bright); white-space: nowrap; z-index: 10; text-shadow: 0 0 8px rgba(0,0,0,0.4);">${displayTotal}</div>
                    <div class="bar-wrapper" style="width: 70%; height: ${heightPct}%; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; position: relative; pointer-events: auto; border-radius: 6px 6px 0 0; overflow: hidden; box-sizing: border-box;">
                        ${barInnerHtml}
                    </div>
                </div>
                <div class="label-wrapper" style="position: absolute; bottom: 8px; text-align: center; width: ${barWidth}px; pointer-events: none;">
                    <div style="font-size: ${(isExpanded ? 0.8 : 0.6) * Math.max(0.7, trendZoomLevel)}rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">${labelTop}</div>
                    <div style="font-size: ${(isExpanded ? 0.7 : 0.55) * Math.max(0.6, trendZoomLevel)}rem; color: var(--text-muted); opacity: 0.7; font-weight: 500; margin-top: 2px;">${labelBottom}</div>
                </div>
            </div>`;
    });

    html += `</div></div><div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px;"><div id="trend-legend" style="display: ${chartType === 'stacked' ? 'flex' : 'none'}; flex-wrap: wrap; gap: 15px; max-width: 80%;"></div><p style="text-align: right; font-size: 0.65rem; color: var(--text-muted); margin: 0;">* ${lang === 'ko' ? '소송제기일(Filing Date) 기준 월별 합계' : 'Monthly totals based on Filing Date'}</p></div>`;
    container.innerHTML = html;
    
    const scrollArea = container.querySelector('#trend-chart-scroll');
    if (scrollArea) {
        requestAnimationFrame(() => {
            scrollArea.scrollLeft = scrollArea.scrollWidth;
        });
    }

    if (chartType === 'stacked') {
        const legendContainer = document.getElementById('trend-legend');
        legendContainer.innerHTML = sortedCats.map((cat) => `
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 12px; height: 12px; border-radius: 3px; background: ${catColorMap[cat]};"></div>
                <span style="font-size: ${isExpanded ? '0.8rem' : '0.65rem'}; color: var(--text-muted);">${cat}</span>
            </div>`).join('');
    }
}




function getTrendGroupValue(c, type, lang, validGroups, topGroups) {
    let rawStr = '';
    if (type === 'claim') {
        rawStr = (c.reason || "").toLowerCase();
        for (const [catName, keywords] of Object.entries(CATEGORY_KEYWORDS.claim)) {
            if (keywords.some(kw => rawStr.includes(kw.toLowerCase()))) return catName;
        }
    } else if (type === 'target_data') {
        rawStr = (c.target_data || "").toLowerCase();
        for (const [catName, keywords] of Object.entries(CATEGORY_KEYWORDS.target_data)) {
            if (keywords.some(kw => rawStr.includes(kw.toLowerCase()))) return catName;
        }
    } else if (type === 'defendant') {
        rawStr = (c.defendant || "").toLowerCase();
    } else if (type === 'country') {
        rawStr = (c.country || "").toLowerCase();
    } else if (type === 'decision') {
        rawStr = (c.status || "").toLowerCase();
    }

    // Prioritize topGroups if they appear in the string
    if (topGroups && topGroups.length > 0) {
        for (const tg of topGroups) {
            if (rawStr.includes(tg.toLowerCase())) return tg;
        }
    }

    // Fallback to first item
    let fallback = 'N/A';
    if (type === 'defendant') fallback = (c.defendant || 'N/A').split(/[;,]/)[0].trim();
    else if (type === 'country') fallback = (c.country || 'N/A');
    else if (type === 'decision') fallback = (c.status || 'N/A');

    if (validGroups && !validGroups.has(fallback)) {
        return (lang === 'en') ? 'Other' : '기타';
    }
    if (fallback === 'N/A') return (lang === 'en') ? 'Other' : '기타';
    return fallback;
}



function handleTrendClick(el) {

    const period = el.getAttribute('data-period');
    const ids = el.getAttribute('data-ids');
    const count = el.getAttribute('data-count');
    showTrendCasesPopup(period, ids, count);
}

function showTrendCasesPopup(period, ids, count) {
    if (!ids) return;
    const idList = ids.split(',');
    const filtered = allCases.filter(c => idList.includes(String(c.system_id || c.id)));
    const title = period + ' 소송 현황 (' + (count || filtered.length) + '건)';
    showCasesPopup(title, filtered);
}


let modalListCurrentPage = 1;
let modalListFilteredCases = [];
let modalListTitle = "";

function renderModalList() {
    const modal = document.getElementById('case-list-modal');
    const title = document.getElementById('modal-list-title');
    const content = document.getElementById('modal-list-content');
    const paginationContainer = document.getElementById('case-list-pagination');
    const pageSizeSelect = document.getElementById('case-list-page-size');
    
    if (!modal || !title || !content) return;

    const itemsPerPage = pageSizeSelect ? parseInt(pageSizeSelect.value) : 15;
    const totalItems = modalListFilteredCases.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;

    if (modalListCurrentPage > totalPages) modalListCurrentPage = totalPages;

    title.textContent = `${modalListTitle} (${totalItems}건)`;
    content.innerHTML = '';

    if (totalItems === 0) {
        content.innerHTML = '<p style="padding: 20px; color: var(--text-muted);">해당 조건의 소송 데이터가 없습니다.</p>';
        if (paginationContainer) paginationContainer.innerHTML = '';
    } else {
        const startIdx = (modalListCurrentPage - 1) * itemsPerPage;
        const endIdx = startIdx + itemsPerPage;
        const currentItems = modalListFilteredCases.slice(startIdx, endIdx);

        currentItems.forEach(c => {
            const item = document.createElement('div');
            item.className = 'modal-case-item';
            item.innerHTML = '<h4>' + (c.case_name || 'Untitled Case') + '</h4><div class="modal-case-meta"><span>📅 ' + (c.file_date || 'Unknown') + '</span><span>📍 ' + (c.country || c.court || 'Unknown') + '</span><span class="badge ' + getStatusKey(c.status) + '">' + (c.status || 'Unknown') + '</span></div>';
            item.onclick = () => {
                if (typeof closeAllModals === 'function') closeAllModals();
                else modal.style.display = 'none';
                showCaseDetail(c);
            };
            content.appendChild(item);
        });

        if (paginationContainer) {
            paginationContainer.innerHTML = '';
            if (totalPages > 1) {
                const createBtn = (text, targetPage, isActive = false) => {
                    const btn = document.createElement('button');
                    btn.textContent = text;
                    btn.className = `pagination-btn ${isActive ? 'active' : ''}`;
                    btn.onclick = () => {
                        modalListCurrentPage = targetPage;
                        renderModalList();
                    };
                    return btn;
                };

                if (modalListCurrentPage > 1) paginationContainer.appendChild(createBtn('←', modalListCurrentPage - 1));
                
                let startPage = Math.max(1, modalListCurrentPage - 2);
                let endPage = Math.min(totalPages, startPage + 4);
                if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

                for (let i = startPage; i <= endPage; i++) {
                    paginationContainer.appendChild(createBtn(i, i, i === modalListCurrentPage));
                }

                if (modalListCurrentPage < totalPages) paginationContainer.appendChild(createBtn('→', modalListCurrentPage + 1));
            }
        }
    }
    modal.style.display = 'flex';
}

function showCasesPopup(titleText, filteredCases) {
    modalListTitle = titleText.replace(/\s*\(\d+건\)$/, '');
    modalListFilteredCases = filteredCases;
    modalListCurrentPage = 1;
    
    const pageSizeSelect = document.getElementById('case-list-page-size');
    if (pageSizeSelect && !pageSizeSelect.hasAttribute('data-bound')) {
        pageSizeSelect.setAttribute('data-bound', 'true');
        pageSizeSelect.addEventListener('change', () => {
            modalListCurrentPage = 1;
            renderModalList();
        });
    }

    renderModalList();
}
function renderUserToolsResults(cases, title) {
    const resultsArea = document.getElementById('user-tools-results-area');
    const settingsArea = document.getElementById('user-tools-settings-area');
    const listContainer = document.getElementById('user-tools-results-list');
    const titleEl = document.getElementById('user-tools-results-title');
    const paginationContainer = document.getElementById('user-tools-pagination');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    if (!resultsArea || !settingsArea || !listContainer) return;

    // Save state for pagination
    userToolsCurrentData = cases;
    userToolsCurrentTitle = title;

    const resultsLabel = TRANSLATIONS[lang].results_title || "Results";
    titleEl.textContent = `${title} - ${resultsLabel} (${cases.length})`;
    listContainer.innerHTML = "";
    if (paginationContainer) paginationContainer.innerHTML = "";
    
    settingsArea.style.display = 'none';
    resultsArea.style.display = 'block';

    if (cases.length === 0) {
        const noRes = TRANSLATIONS[lang].no_results || "No results found.";
        listContainer.innerHTML = `<p class="empty-msg">${noRes}</p>`;
        return;
    }

    // Pagination Logic
    const totalPages = Math.ceil(cases.length / userToolsPageSize);
    if (userToolsCurrentPage > totalPages) userToolsCurrentPage = totalPages;
    if (userToolsCurrentPage < 1) userToolsCurrentPage = 1;

    const start = (userToolsCurrentPage - 1) * userToolsPageSize;
    const end = start + userToolsPageSize;
    const paginatedCases = cases.slice(start, end);

    const table = document.createElement('table');
    table.className = 'user-tools-table';
    
    // Header
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>${lang === 'ko' ? '사건명' : 'Case Name'}</th>
            <th>${lang === 'ko' ? '피고' : 'Defendant'}</th>
            <th>${lang === 'ko' ? '대상 데이터' : 'Target Data'}</th>
            <th>${lang === 'ko' ? '제기일' : 'Filed Date'}</th>
            <th>${lang === 'ko' ? '진행상태' : 'Status'}</th>
        </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    paginatedCases.forEach(c => {
        const tr = document.createElement('tr');
        tr.onclick = () => showCaseDetail(c);
        
        const icon = typeof getCaseIcon === 'function' ? getCaseIcon(c) : '📄';
        
        tr.innerHTML = `
            <td class="col-name">
                <div class="case-name-wrapper">
                    <span class="case-icon">${icon}</span>
                    <span class="case-title">${c.case_name || 'N/A'}</span>
                </div>
            </td>
            <td class="col-defendant">${c.defendant || 'N/A'}</td>
            <td class="col-target">${c.target_data || 'N/A'}</td>
            <td class="col-date">${c.file_date || 'N/A'}</td>
            <td class="col-status"><span class="status-badge small">${c.status || 'N/A'}</span></td>
        `;
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    listContainer.appendChild(table);

    // Render Pagination Controls
    if (totalPages > 1 && paginationContainer) {
        const createBtn = (text, page, isActive = false) => {
            const btn = document.createElement('button');
            btn.className = isActive ? 'btn-primary' : 'btn-secondary';
            btn.textContent = text;
            btn.style.minWidth = '40px';
            btn.onclick = () => {
                userToolsCurrentPage = page;
                renderUserToolsResults(cases, title);
                resultsArea.scrollIntoView({ behavior: 'smooth' });
            };
            return btn;
        };

        // Prev
        if (userToolsCurrentPage > 1) {
            paginationContainer.appendChild(createBtn('←', userToolsCurrentPage - 1));
        }

        // Page Numbers (Show max 5)
        let startPage = Math.max(1, userToolsCurrentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

        for (let i = startPage; i <= endPage; i++) {
            paginationContainer.appendChild(createBtn(i, i, i === userToolsCurrentPage));
        }

        // Next
        if (userToolsCurrentPage < totalPages) {
            paginationContainer.appendChild(createBtn('→', userToolsCurrentPage + 1));
        }
    }
}

// --- Live Ticker Functions ---

function initTickers() {
    const suitBox = document.getElementById('suit-ticker-box');
    const newsBox = document.getElementById('news-ticker-box');
    
    // Check localStorage for "Don't show again" settings
    if (localStorage.getItem('hide-suit-ticker') === 'true') {
        if (suitBox) suitBox.style.display = 'none';
    }
    if (localStorage.getItem('hide-news-ticker') === 'true') {
        if (newsBox) newsBox.style.display = 'none';
    }

    const suitCountSelect = document.getElementById('suit-ticker-count');
    const newsCountSelect = document.getElementById('news-ticker-count');
    const suitCloseBtn = document.getElementById('suit-ticker-close');
    const newsCloseBtn = document.getElementById('news-ticker-close');
    const suitHideForever = document.getElementById('suit-ticker-hide-forever');
    const newsHideForever = document.getElementById('news-ticker-hide-forever');
    const restoreTickersBtn = document.getElementById('restore-tickers-btn');

    if (suitCountSelect) {
        suitCountSelect.onchange = (e) => {
            suitTickerCount = parseInt(e.target.value);
            updateSuitTicker();
        };
    }
    if (newsCountSelect) {
        newsCountSelect.onchange = (e) => {
            newsTickerCount = parseInt(e.target.value);
            updateNewsTicker();
        };
    }

    // Close button logic with "Don't show again" support
    const handleClose = (type) => {
        const box = type === 'suit' ? suitBox : newsBox;
        const cb = type === 'suit' ? suitHideForever : newsHideForever;
        if (cb && cb.checked) {
            localStorage.setItem(`hide-${type}-ticker`, 'true');
        }
        if (box) box.style.display = 'none';
    };

    if (suitCloseBtn) suitCloseBtn.onclick = () => handleClose('suit');
    if (newsCloseBtn) newsCloseBtn.onclick = () => handleClose('news');

    // Also close immediately if "Don't show again" is checked
    if (suitHideForever) {
        suitHideForever.onchange = () => {
            if (suitHideForever.checked) handleClose('suit');
        };
    }
    if (newsHideForever) {
        newsHideForever.onchange = () => {
            if (newsHideForever.checked) handleClose('news');
        };
    }

    // Restore Tickers Logic
    if (restoreTickersBtn) {
        restoreTickersBtn.onclick = () => {
            localStorage.removeItem('hide-suit-ticker');
            localStorage.removeItem('hide-news-ticker');
            
            if (suitBox) suitBox.style.display = 'block';
            if (newsBox) newsBox.style.display = 'block';
            
            if (suitHideForever) suitHideForever.checked = false;
            if (newsHideForever) newsHideForever.checked = false;
            
            // Refresh content
            updateSuitTicker();
            updateNewsTicker();
            
            const msg = (localStorage.getItem('dashboard-lang') || 'ko') === 'ko' ? 
                "티커 표시 설정이 초기화되었습니다." : "Ticker display settings have been restored.";
            alert(msg);
        };
    }
}

function updateSuitTicker() {
    const list = document.getElementById('suit-ticker-list');
    if (!list || !allCases || allCases.length === 0) return;

    // Sort by file_date (latest first)
    const sorted = [...allCases].sort((a, b) => {
        const dateA = new Date(a.file_date || '1970-01-01');
        const dateB = new Date(b.file_date || '1970-01-01');
        return dateB - dateA;
    });

    const items = sorted.slice(0, suitTickerCount);
    list.innerHTML = items.map(c => `
        <li class="ticker-item" data-id="${c.system_id || c.id}">
            <span class="item-icon">${getCaseIcon(c)}</span>
            <span class="item-text">${c.case_name}</span>
            <span class="item-date">${c.file_date || ''}</span>
        </li>
    `).join('');

    // Attach click events
    list.querySelectorAll('.ticker-item').forEach(el => {
        el.onclick = () => showCaseDetailById(el.getAttribute('data-id'));
    });

    startTickerAnimation('suit-ticker-list');
}

function updateNewsTicker() {
    const list = document.getElementById('news-ticker-list');
    if (!list || !allCases || allCases.length === 0) return;

    const latestNewsPerCase = [];
    allCases.forEach(c => {
        if (!c.remarks || !c.remarks.includes('##')) return;
        const updates = c.remarks.split(/(?=##)/);
        let latestUpdate = null;
        
        updates.forEach(update => {
            // Check for 'Updated' or 'updated' in the status part
            if (update.toLowerCase().includes('updated')) {
                const lines = update.trim().split('\n');
                if (lines.length < 1) return;
                const headerLine = lines[0].replace('##', '').trim();
                const parts = headerLine.split(',').map(p => p.trim());
                const date = parts[1] || '';
                const title = parts.slice(2).join(', ') || 'Update';
                
                if (date && (!latestUpdate || new Date(date) > new Date(latestUpdate.date))) {
                    latestUpdate = {
                        case_id: c.system_id || c.id,
                        case_name: c.case_name,
                        date: date,
                        title: title,
                        icon: getCaseIcon(c)
                    };
                }
            }
        });
        
        if (latestUpdate) {
            latestNewsPerCase.push(latestUpdate);
        }
    });

    // Sort cases by their latest news date (latest first)
    latestNewsPerCase.sort((a, b) => {
        const dateA = new Date(a.date || '1970-01-01');
        const dateB = new Date(b.date || '1970-01-01');
        return dateB - dateA;
    });

    const items = latestNewsPerCase.slice(0, newsTickerCount);
    list.innerHTML = items.map(n => `
        <li class="ticker-item" data-id="${n.case_id}">
            <span class="item-icon">${n.icon}</span>
            <span class="item-text"><b>[${n.date}]</b> ${n.title} - ${n.case_name}</span>
        </li>
    `).join('');

    // Attach click events
    list.querySelectorAll('.ticker-item').forEach(el => {
        el.onclick = () => showCaseDetailById(el.getAttribute('data-id'));
    });

    startTickerAnimation('news-ticker-list');
}

function startTickerAnimation(listId) {
    const list = document.getElementById(listId);
    if (!list) return;

    // Clear existing interval
    if (listId === 'suit-ticker-list') {
        if (suitTickerInterval) clearInterval(suitTickerInterval);
    } else {
        if (newsTickerInterval) clearInterval(newsTickerInterval);
    }

    const items = list.querySelectorAll('.ticker-item');
    if (items.length <= 3) {
        list.style.transform = 'translateY(0)';
        return;
    }

    let currentIndex = 0;
    const itemHeight = 40;
    const scrollCount = items.length;

    const animate = () => {
        currentIndex++;
        if (currentIndex > scrollCount - 3) {
            // Smoothly wrap around
            list.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            list.style.transform = `translateY(-${currentIndex * itemHeight}px)`;
            
            setTimeout(() => {
                list.style.transition = 'none';
                list.style.transform = 'translateY(0)';
                currentIndex = 0;
            }, 500);
        } else {
            list.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            list.style.transform = `translateY(-${currentIndex * itemHeight}px)`;
        }
    };

    const interval = setInterval(animate, 3500);
    if (listId === 'suit-ticker-list') suitTickerInterval = interval;
    else newsTickerInterval = interval;
}

function showCaseDetailById(id) {
    const c = allCases.find(x => (x.system_id || x.id) == id);
    if (c) showCaseDetail(c);
}

// --- Statistics Expansion Logic ---

/**
 * Toggles a statistics card between grid view and fullscreen expanded view.
 * @param {string} cardId - The ID of the card to expand.
 */
function toggleExpand(cardId) {
    const card = document.getElementById(cardId);
    const backdrop = document.getElementById('stats-expand-backdrop');
    if (!card || !backdrop) return;

    const isExpanded = card.classList.contains('expanded');
    
    // Close any other expanded cards first just in case
    document.querySelectorAll('.stats-card.expanded').forEach(c => {
        if (c !== card) c.classList.remove('expanded');
    });
    
    if (!isExpanded) {
        card.classList.add('expanded');
        document.body.classList.add('stats-card-expanded');
        backdrop.style.display = 'block';
        // Add close button to expanded view
        if (!card.querySelector('.close-expand-btn')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'btn-secondary close-expand-btn';
            closeBtn.style.position = 'absolute';
            closeBtn.style.top = '15px';
            closeBtn.style.right = '40px';
            closeBtn.style.zIndex = '100000';
            closeBtn.innerHTML = '✕ 축소 (Minimize)';
            closeBtn.onclick = (e) => {
                e.stopPropagation();
                closeAllExpanded();
            };
            card.appendChild(closeBtn);
        }
        // Disable body scroll when expanded
        document.body.style.overflow = 'hidden';
    } else {
        card.classList.remove('expanded');
        document.body.classList.remove('stats-card-expanded');
        backdrop.style.display = 'none';
        const closeBtn = card.querySelector('.close-expand-btn');
        if (closeBtn) closeBtn.remove();
        document.body.style.overflow = '';
    }
}

/**
 * Closes all expanded statistics cards.
 */
function closeAllExpanded() {
    const backdrop = document.getElementById('stats-expand-backdrop');
    if (backdrop) backdrop.style.display = 'none';
    
    document.querySelectorAll('.stats-card.expanded').forEach(card => {
        card.classList.remove('expanded');
        const closeBtn = card.querySelector('.close-expand-btn');
        if (closeBtn) closeBtn.remove();
    });
    document.body.classList.remove('stats-card-expanded');
    document.body.style.overflow = '';
}

/**
 * Initialize AI Risk Radar Content
 * Tailored for Samsung Electronics Business Divisions
 */
function initRadarContent(region = 'ALL') {
    const riskList = document.getElementById('radar-risk-list');
    const checklistContent = document.getElementById('radar-checklist-content');
    const lang = localStorage.getItem('dashboard-lang') || 'ko';

    if (!riskList || !checklistContent) return;

    // 1. Potential Risks Data with Geo-tags
    const allRisks = [
        {
            title: lang === 'ko' ? '생성형 AI 학습 데이터 저작권 (Training Data)' : 'Generative AI Training Data Copyright',
            desc: lang === 'ko' ? 'NYT vs OpenAI 소송과 유사하게, 삼성 자체 LLM(Gauss 등) 학습 시 뉴스, 도서 등 저작물 무단 사용에 따른 저작권 침해 리스크' : 'Risk of copyright infringement for unauthorized use of news/books for internal LLM (Gauss, etc.) training, similar to NYT vs OpenAI.',
            level: 'high',
            tags: ['Gauss', 'Copyright', 'LLM', 'Legal'],
            regions: ['ALL', 'US', 'EU', 'KR'],
            relatedCases: lang === 'ko' ? 'New York Times v. OpenAI, Getty Images v. Stability AI' : 'New York Times v. OpenAI, Getty Images v. Stability AI'
        },
        {
            title: lang === 'ko' ? '생체 정보(Biometrics) 프라이버시 리스크' : 'Biometric Privacy (BIPA) Risks',
            desc: lang === 'ko' ? '갤럭시 AI의 실시간 번역, 온디바이스 얼굴/음성 인식 기능이 미국 일리노이주 BIPA법 등 글로벌 생체정보 보호법 위반 소지' : 'Galaxy AI features like Live Translate, face/voice recognition may violate global biometric privacy laws like Illinois BIPA.',
            level: 'high',
            tags: ['Galaxy AI', 'Privacy', 'BIPA', 'Compliance'],
            regions: ['ALL', 'US'],
            relatedCases: lang === 'ko' ? 'Texas v. Meta (Face Recognition), Class Actions on Voice Data' : 'Texas v. Meta (Face Recognition), Class Actions on Voice Data'
        },
        {
            title: lang === 'ko' ? 'AI 할루시네이션(환각) 및 제조물 책임' : 'AI Hallucination & Product Liability',
            desc: lang === 'ko' ? '빅스비나 스마트싱스 AI가 사용자에게 잘못된 의학적/기술적 조언을 제공하여 발생할 수 있는 사고 및 제조물 책임(PL) 리스크' : 'Product Liability (PL) risk if Bixby or SmartThings AI provides incorrect medical/technical advice leading to user accidents.',
            level: 'medium',
            tags: ['Bixby', 'SmartThings', 'Liability'],
            regions: ['ALL', 'US', 'EU', 'KR'],
            relatedCases: lang === 'ko' ? 'Walters v. OpenAI (명예훼손), Air Canada Chatbot Case' : 'Walters v. OpenAI (Defamation), Air Canada Chatbot Case'
        },
        {
            title: lang === 'ko' ? 'AI 생성 콘텐츠의 저작권 및 워터마크 의무' : 'AI Content Copyright & Watermarking',
            desc: lang === 'ko' ? '갤럭시 S 시리즈의 생성형 편집 기능을 통해 수정된 이미지에 대한 투명성 공지 및 워터마크 강제화 미준수 시 법적 분쟁 가능성' : 'Potential legal disputes if transparency notices or watermarking for images modified by Galaxy S-series Generative Edit are not strictly followed.',
            level: 'medium',
            tags: ['Generative Edit', 'Transparency', 'IP'],
            regions: ['ALL', 'EU', 'US'],
            relatedCases: lang === 'ko' ? 'Thaler v. Perlmutter (AI 저작물 불인정 판결)' : 'Thaler v. Perlmutter (AI Authorship Denial)'
        },
        {
            title: lang === 'ko' ? 'EU AI Act 준수 및 고위험 AI 분류' : 'EU AI Act Compliance & High-Risk AI',
            desc: lang === 'ko' ? '유럽 시장 출시 예정인 AI 기반 의료 기기나 보안 솔루션이 고위험 AI로 분류될 경우의 엄격한 기술 문서 및 사후 모니터링 의무' : 'Strict technical documentation and post-market monitoring duties if AI-based medical or security solutions for EU market are classified as High-Risk AI.',
            level: 'high',
            tags: ['EU AI Act', 'Medical AI', 'Security'],
            regions: ['ALL', 'EU'],
            relatedCases: lang === 'ko' ? 'EU 규제 당국 조사 사례 (Clearview AI 과징금 등)' : 'EU Regulatory Investigations (e.g. Clearview AI fines)'
        },
        {
            title: lang === 'ko' ? '영업비밀 및 임직원 데이터 유출' : 'Trade Secret & Internal Data Leak',
            desc: lang === 'ko' ? '임직원이 외부 퍼블릭 AI 사용 중 회사의 소스코드나 영업비밀을 입력하여 발생하는 정보 유출 및 지식재산권 상실 리스크' : 'Risk of data breach and loss of IP if employees input source code or trade secrets into public AI models.',
            level: 'medium',
            tags: ['Security', 'Trade Secret', 'HR'],
            regions: ['ALL', 'US', 'EU', 'KR'],
            relatedCases: lang === 'ko' ? 'Samsung 자체 데이터 유출 사례 (과거 ChatGPT 도입 초기)' : 'Internal Data Leak Incidents (e.g. early ChatGPT adoption)'
        }
    ];

    const risks = region === 'ALL' ? allRisks : allRisks.filter(r => r.regions.includes(region) || r.regions.includes('ALL'));

    // 2. Checklist Data
    const checklists = [
        {
            dept: lang === 'ko' ? 'MX (Mobile eXperience) 사업부' : 'MX (Mobile eXperience) Division',
            icon: '📱',
            items: lang === 'ko' ? 
                ['갤럭시 AI 기능별 데이터 수집/처리 동의 프로세스 점검', '생성형 편집 기능 사용 시 메타데이터 및 워터마크 자동 삽입 검증', '온디바이스 AI 처리 비중 확대를 통한 프라이버시 강화'] : 
                ['Review data consent process for each Galaxy AI feature', 'Verify auto-insertion of watermarks in Generative Edit', 'Enhance privacy by increasing on-device AI processing share']
        },
        {
            dept: lang === 'ko' ? 'VD (Visual Display) / 가전 사업부' : 'VD (Visual Display) & Digital Appliances',
            icon: '📺',
            items: lang === 'ko' ? 
                ['스마트 TV/냉장고 AI 카메라/마이크 사용 알림 및 프라이버시 셔터 확인', 'AI 추천 시스템의 알고리즘 투명성 및 설명 가능성 확보', '가전용 AI 서비스의 오작동 대비 안전 가드레일 설계'] : 
                ['Check camera/mic usage notifications and privacy shutters', 'Ensure algorithm transparency and explainability for AI recommendations', 'Design safety guardrails against AI service malfunctions']
        },
        {
            dept: lang === 'ko' ? 'DS (Device Solutions) 사업부' : 'DS (Device Solutions) Division',
            icon: '💾',
            items: lang === 'ko' ? 
                ['반도체 설계 보조 AI 사용 시 보안망 분리 및 데이터 휘발성 보장', 'AI 반도체 칩셋 내 보안 구역(Secure Element) 통한 생체정보 보호', '공정 최적화 AI 모델의 영업비밀 보호 및 접근 제어'] : 
                ['Ensure network isolation and data volatility when using AI for chip design', 'Protect biometric data via Secure Element in AI chipsets', 'Enforce access control for trade secrets in manufacturing AI models']
        },
        {
            dept: lang === 'ko' ? '법무 및 컴플라이언스 팀' : 'Legal & Compliance Team',
            icon: '⚖️',
            items: lang === 'ko' ? 
                ['글로벌 AI 규제(EU AI Act, 미국 행정명령) 상시 모니터링', 'AI 서비스 약관 내 면책 조항 및 책임 소재 명확화', '학습 데이터 구매 시 저작권 보증 및 구상권 조항 검토'] : 
                ['Monitor global AI regulations (EU AI Act, US Exec Order)', 'Clarify liability and disclaimers in AI service terms', 'Review copyright warranties and indemnity in data purchase contracts']
        }
    ];

    // Render Risks
    riskList.innerHTML = risks.map(r => `
        <div class="radar-card">
            <div class="radar-card-header">
                <span class="radar-card-title">${r.title}</span>
                <span class="risk-level risk-${r.level}">${r.level.toUpperCase()}</span>
            </div>
            <div class="radar-card-desc">
                ${r.desc}
                <br>
                <span style="color: var(--primary-bright); font-size: 0.85em; display: inline-block; margin-top: 5px;">
                    (*관련 소송사건: ${r.relatedCases})
                </span>
            </div>
            <div class="radar-card-tags">
                ${r.tags.map(t => `<span class="radar-tag">#${t}</span>`).join('')}
            </div>
        </div>
    `).join('');

    // Render Checklist with Interactive Radio Buttons
    let globalItemIndex = 0;
    checklistContent.innerHTML = checklists.map((c, deptIndex) => `
        <div class="radar-section-item">
            <div class="radar-card-header" style="margin-bottom: 10px;">
                <span class="radar-card-title" style="color: var(--primary-bright); display: flex; align-items: center; gap: 8px;">
                    <span>${c.icon}</span> ${c.dept}
                </span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                ${c.items.map(item => {
                    const idx = globalItemIndex++;
                    return `
                    <div class="checklist-item" id="checklist-item-${idx}">
                        <div class="checklist-header">
                            <div class="checklist-icon">🔹</div>
                            <div class="checklist-info">
                                <p>${item}</p>
                            </div>
                        </div>
                        <div class="checklist-controls">
                            <label><input type="radio" name="chk-${idx}" value="pass" onchange="updateChecklistProgress(this, ${idx})"> <span>✅ ${lang === 'ko' ? '적합' : 'Pass'}</span></label>
                            <label><input type="radio" name="chk-${idx}" value="fail" onchange="updateChecklistProgress(this, ${idx})"> <span>❌ ${lang === 'ko' ? '부적합' : 'Fail'}</span></label>
                            <label><input type="radio" name="chk-${idx}" value="na" onchange="updateChecklistProgress(this, ${idx})"> <span>➖ ${lang === 'ko' ? '해당없음' : 'N/A'}</span></label>
                        </div>
                    </div>
                `;
                }).join('')}
            </div>
        </div>
    `).join('<div style="height: 20px;"></div>');
    
    // Bind Region Selector Event once
    const countrySelect = document.getElementById('radar-country-select');
    if (countrySelect && !countrySelect.hasAttribute('data-bound')) {
        countrySelect.setAttribute('data-bound', 'true');
        countrySelect.onchange = (e) => {
            initRadarContent(e.target.value);
        };
    }
    
    // Reset Progress
    updateGlobalProgress();
}

/**
 * Updates the visual state of a checklist item when a radio button is selected
 */
window.updateChecklistProgress = function(radioElem, idx) {
    const itemDiv = document.getElementById(`checklist-item-${idx}`);
    if (itemDiv) {
        itemDiv.classList.remove('status-pass', 'status-fail', 'status-na');
        if (radioElem.value === 'pass') itemDiv.classList.add('status-pass');
        else if (radioElem.value === 'fail') itemDiv.classList.add('status-fail');
        else if (radioElem.value === 'na') itemDiv.classList.add('status-na');
    }
    updateGlobalProgress();
};

/**
 * Calculates the total readiness score and updates the progress bar
 */
function updateGlobalProgress() {
    const allRadios = document.querySelectorAll('.checklist-controls input[type="radio"]:checked');
    const totalItems = document.querySelectorAll('.checklist-item').length;
    
    if (totalItems === 0) return;

    let passed = 0;
    let failed = 0;
    
    allRadios.forEach(r => {
        if (r.value === 'pass' || r.value === 'na') passed++;
        if (r.value === 'fail') failed++;
    });

    const progressPercent = Math.round((passed / totalItems) * 100);
    
    const fill = document.getElementById('radar-progress-fill');
    const text = document.getElementById('radar-progress-text');
    
    if (fill && text) {
        fill.style.width = `${progressPercent}%`;
        text.textContent = `${progressPercent}%`;
        
        if (progressPercent === 100 && failed === 0) {
            fill.style.background = 'var(--success)';
            text.style.color = 'var(--success)';
            text.textContent = '100% (출시 가능)';
        } else if (failed > 0) {
            fill.style.background = 'var(--error)';
            text.style.color = 'var(--error)';
        } else {
            fill.style.background = 'var(--primary-bright)';
            text.style.color = 'var(--primary-bright)';
        }
    }
}
