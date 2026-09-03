"""Persistent, de-duplicated catalog of datasets implicated in lawsuits."""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

FIELDS = ("dataset_name", "official_url", "case_count", "evidence_count",
          "related_cases", "evidence", "source_urls", "first_seen", "last_seen")
DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "risky-open-datasets.csv"


def _loads(value: str) -> list:
    try:
        result = json.loads(value or "[]")
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _unique(items: list, key) -> list:
    result, seen = [], set()
    for item in items:
        marker = key(item)
        if marker not in seen:
            seen.add(marker)
            result.append(item)
    return result


def _merge_named_details(old_items: list[dict], new_items: list[dict]) -> list[dict]:
    """Merge case details by name, enriching a previously missing URL in place."""
    merged: dict[str, dict] = {}
    for item in old_items + new_items:
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        key = name.casefold()
        previous = merged.get(key, {})
        merged[key] = {
            "name": previous.get("name") or name,
            "url": previous.get("url") or str(item.get("url") or ""),
        }
    return list(merged.values())


def _merge_evidence(old_items: list[dict], new_items: list[dict]) -> list[dict]:
    """Keep unique evidence while filling source metadata learned on later runs."""
    merged: dict[tuple[str, str], dict] = {}
    for item in old_items + new_items:
        excerpt = str(item.get("excerpt") or "").strip()
        if not excerpt:
            continue
        key = (str(item.get("case") or "").casefold(), excerpt.casefold())
        previous = merged.get(key, {})
        merged[key] = {
            "case": previous.get("case") or str(item.get("case") or ""),
            "source": previous.get("source") or str(item.get("source") or ""),
            "excerpt": previous.get("excerpt") or excerpt,
            "url": previous.get("url") or str(item.get("url") or ""),
        }
    return list(merged.values())


def upsert_dataset_catalog(aggregate: Mapping[str, dict], path=DEFAULT_PATH, *, now: str | None = None) -> list[dict]:
    """Merge observations into CSV, retaining one case-insensitive dataset row."""
    target = Path(path)
    existing: dict[str, dict] = {}
    if target.exists():
        with target.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                name = (row.get("dataset_name") or "").strip()
                if name:
                    existing[name.casefold()] = row
    timestamp = now or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for incoming in aggregate.values():
        name = str(incoming.get("name") or "").strip()
        if not name:
            continue
        key, old = name.casefold(), existing.get(name.casefold(), {})
        new_cases = [{"name": str(x[0]), "url": str(x[1] or "")} for x in incoming.get("cases", []) if x and x[0]]
        cases = _merge_named_details(_loads(old.get("related_cases", "")), new_cases)
        new_evidence = [{"case": str(x[0]), "source": str(x[1]), "excerpt": str(x[2]), "url": str(x[3] or "")}
                        for x in incoming.get("evidence", []) if len(x) >= 4 and x[2]]
        evidence = _merge_evidence(_loads(old.get("evidence", "")), new_evidence)
        urls = _unique(_loads(old.get("source_urls", "")) + [x["url"] for x in new_evidence if x["url"]], lambda x: x)
        changed = (
            cases != _loads(old.get("related_cases", ""))
            or evidence != _loads(old.get("evidence", ""))
            or urls != _loads(old.get("source_urls", ""))
            or (not old.get("official_url") and bool(incoming.get("official_url")))
        )
        existing[key] = {
            "dataset_name": old.get("dataset_name") or name,
            "official_url": old.get("official_url") or str(incoming.get("official_url") or ""),
            "case_count": str(len(cases)), "evidence_count": str(len(evidence)),
            "related_cases": json.dumps(cases, ensure_ascii=False, separators=(",", ":")),
            "evidence": json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
            "source_urls": json.dumps(urls, ensure_ascii=False, separators=(",", ":")),
            "first_seen": old.get("first_seen") or timestamp,
            "last_seen": timestamp if changed or not old else old.get("last_seen") or timestamp,
        }
    rows = sorted(existing.values(), key=lambda x: (-int(x["case_count"]), x["dataset_name"].casefold()))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(rows)
    return rows


def catalog_as_json(path=DEFAULT_PATH) -> list[dict]:
    """Load CSV and decode JSON list columns for the web dashboard."""
    target = Path(path)
    if not target.exists():
        return []
    with target.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["case_count"] = int(row.get("case_count") or 0)
        row["evidence_count"] = int(row.get("evidence_count") or 0)
        for field in ("related_cases", "evidence", "source_urls"):
            row[field] = _loads(row.get(field, ""))
    return rows
