from __future__ import annotations
import requests

def post_to_slack(webhook_url: str, text: str) -> None:
    r = requests.post(webhook_url, json={"text": text}, timeout=20)
    r.raise_for_status()
