# Data card

## Purpose

GigBid uses a local, demonstrable corpus so the application can be reviewed without an Upwork account or scraped data. The checked-in demo corpus is deliberately small and is suitable only for functional testing and reproducible course evaluations.

## Sources and attribution

The project design supports public job-posting datasets, including the user-supplied Kaggle sources: Upwork Job Postings Dataset 2024 (asaniczka), All Jobs on Upwork (asaniczka), Upwork Freelance Jobs 60K (ahmedmyalo), Freelance Contracts Dataset (asaniczka), Freelancer Success Earnings and Churn Prediction (sarveshchhetri), and Trial 1 (adityammantri). They are not redistributed in this repository. Before importing any source, its Kaggle license, terms, fields, and permitted use must be checked and recorded in an import manifest.

## Included data

`data/processed/demo_jobs.json` and `data/processed/demo_portfolio.json` are synthetic records written for this course project. They do not describe real clients, contracts, reviews, earnings, or job postings. The two benign jobs exercise fit and pricing; the second job is a planted scam and prompt-injection test case.

## Preprocessing

Importers normalise whitespace, mask email/phone patterns in logs, preserve source attribution, assign a stable document id, and store provenance metadata. The demo evaluator uses deterministic matching rather than a hosted model so results can be reproduced offline.

## Limitations

The corpus is too small to estimate real marketplace performance, synthetic client histories do not represent platform dynamics, and lexical retrieval cannot establish factual truth by itself. Production ingestion must obtain user consent, honour dataset/platform terms, and keep tenant data isolated.

