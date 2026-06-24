
AI_COMPANIES = ["OpenAI", "Google", "Meta", "Anthropic", "Microsoft", "Stability AI"]

def detect_company(text):
    for c in AI_COMPANIES:
        if c.lower() in text.lower():
            return c
    return "Unknown"

def process(raw):
    result = []
    for r in raw:
        case_name = r.get("caseName", "Unknown")
        result.append({
            "case_name": case_name,
            "file_date": r.get("dateFiled", "Unknown"),
            "case_no": r.get("docket_number", "Unknown"),
            "plaintiff": "Unknown",  # CourtListener dockets list often needs separate calls for parties
            "defendant": detect_company(case_name),
            "country": "USA",
            "court": r.get("court", "Unknown"),
            "status": "Unknown",
            "reason": "AI Litigation",
            "url": "https://www.courtlistener.com" + r.get("absolute_url", ""),
            "summary": ""
        })
    return result
