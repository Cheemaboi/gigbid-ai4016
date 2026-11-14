# Data card

## Purpose

GigBid uses a local, demonstrable corpus so the application can be reviewed without an Upwork account or scraped data. The checked-in demo corpus is deliberately small and is suitable only for functional testing and reproducible course evaluations.

## Sources and attribution

The project includes an attributed derived sample from **Upwork Job Postings Dataset 2024 (50K Records)** by `asaniczka` on Kaggle: <https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records>. At import time (2026-11-15), Kaggle declared the **ODC Attribution License (ODC-By)**. `scripts/import_upwork_2024.py` selects technical postings deterministically, normalises text, redacts obvious email/phone patterns, preserves per-record source links and writes `data/processed/upwork_jobs_2024_sample.json`. The original 50K CSV is not committed or redistributed.

The remaining user-supplied datasets (All Jobs on Upwork, Upwork Freelance Jobs 60K, Freelance Contracts, Freelancer Success/Earnings/Churn, and Trial 1) are documented candidates, but are not used in the checked-in result. Their licences, terms, fields, and permitted use must be checked before a future import.

## Included data

`data/processed/upwork_jobs_2024_sample.json` contains 250 **real public job-posting records**, derived from the cited Kaggle dataset and carrying source/licence metadata. It is only used as an attributed offline corpus; it is not represented as a current Upwork feed.

`data/processed/demo_jobs.json` and `data/processed/demo_portfolio.json` are **synthetic** records written for this course project. They do not describe real clients, contracts, reviews, earnings, proposals, or conversations. The benign jobs exercise fit and pricing; the second job is a planted scam and prompt-injection test case.

## Preprocessing

Importers normalise whitespace, mask email/phone patterns, preserve source attribution, assign a stable document id, and store provenance metadata. The demo evaluator uses deterministic matching rather than a hosted model so results can be reproduced offline.

## Limitations

The 250-record derived sample is not representative enough to estimate real marketplace performance; it has no reliable outcomes, client spend, hire events, or proposal decisions. Synthetic client histories do not represent platform dynamics, and lexical retrieval cannot establish factual truth by itself. Production ingestion must obtain user consent, honour dataset/platform terms, and keep tenant data isolated.

