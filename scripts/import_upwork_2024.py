"""Create an attributed, redacted derived sample from the permitted Kaggle export.

The script deliberately does not commit or redistribute the Kaggle CSV.  Download the
archive yourself, pass its CSV path, and it writes a small derived sample used for
offline analysis.  Portfolio/client/review data in this project remains synthetic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REF = "asaniczka/upwork-job-postings-dataset-2024-50k-records"
SOURCE_URL = f"https://www.kaggle.com/datasets/{SOURCE_REF}"
TECH_TERMS = ("python", "react", "fastapi", "data analyst", "data engineer", "machine learning", "api", "typescript", "javascript", "sql", "rag", "artificial intelligence")
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)")
SPACE = re.compile(r"\s+")


def clean(value: str, limit: int) -> str:
    value = html.unescape(value or "")
    value = EMAIL.sub("[redacted-email]", value)
    value = PHONE.sub("[redacted-phone]", value)
    return SPACE.sub(" ", value).strip()[:limit]


def extract_skills(description: str) -> list[str]:
    match = re.search(r"Skills:\s*(.*?)(?:Country:|click to apply|$)", description, re.IGNORECASE)
    if not match:
        return []
    items = re.split(r"[,;]", match.group(1))
    return [clean(item, 48) for item in items if clean(item, 48)][:12]


def row_to_record(row: dict[str, str]) -> dict[str, object]:
    raw_description = row.get("description", "")
    url = row.get("link", "")
    stable_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return {
        "id": f"upwork-2024-{stable_id}",
        "title": clean(row.get("title", ""), 180),
        "description": clean(raw_description, 1400),
        "skills": extract_skills(raw_description),
        "budget": float(row["budget"]) if row.get("budget") else None,
        "is_hourly": row.get("is_hourly", "").lower() == "true",
        "hourly_low": float(row["hourly_low"]) if row.get("hourly_low") else None,
        "hourly_high": float(row["hourly_high"]) if row.get("hourly_high") else None,
        "country": clean(row.get("country", ""), 80) or None,
        "published_date": row.get("published_date"),
        "provenance": {
            "source_type": "real_public_dataset",
            "dataset": SOURCE_REF,
            "dataset_url": SOURCE_URL,
            "license": "ODC Attribution License (ODC-By)",
            "original_job_url": url,
            "import_method": "redacted derived sample; no client history, reviews, proposals, or conversations inferred",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/upwork_jobs_2024_sample.json")
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    with args.csv_path.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            text = f"{row.get('title', '')} {row.get('description', '')}".lower()
            if any(term in text for term in TECH_TERMS):
                rows.append(row_to_record(row))
            if len(rows) >= args.limit:
                break
    payload = {
        "metadata": {
            "record_count": len(rows),
            "source_type": "real_public_dataset",
            "dataset": SOURCE_REF,
            "dataset_url": SOURCE_URL,
            "license": "ODC Attribution License (ODC-By)",
            "limitations": "This is a deterministic, redacted technical-job sample. It is not a live marketplace feed and does not establish client trust, outcomes, or freelancer performance.",
        },
        "records": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(rows)} attributed records to {args.output}")


if __name__ == "__main__":
    main()
