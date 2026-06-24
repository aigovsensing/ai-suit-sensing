from collector.courtlistener import fetch_cases
from collector.processor import process
from collector.storage import insert_cases

def run():
    raw = fetch_cases()
    cleaned = process(raw)
    insert_cases(cleaned)

if __name__ == "__main__":
    run()
