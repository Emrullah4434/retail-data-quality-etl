# Retail Data Quality & ETL (Python + SQLite)

Small, reproducible data engineering example supporting a Data Analyst portfolio. The source dataset is **synthetic**, with no company or confidential data.

## Workflow
CSV source → schema and range validation → derived net sales → transactional SQLite load → indexed fact table → SQL checks. Re-running is idempotent (refreshes the target table). Bad records cause an explicit error rather than being silently discarded.

## Run
```bash
python src/pipeline.py
python src/quality_checks.py
```
No third-party dependencies. Python 3.10+ recommended.

## Concepts demonstrated
Data quality controls, primary keys, type validation, repeatable ETL, SQLite indexes, reconciliations, SQL window calculations. This is a local demo, **not** a production cloud pipeline or deployed Airflow/dbt project.
