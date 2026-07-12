# Denis Isikawa — Data Engineering & FP&A Analytics Portfolio

**Senior Data Engineering & FP&A Analytics Lead**

Banco Bradesco | 17+ years in data | technical leadership of an 8-person analytics team

---

## Executive overview

- Portfolio built to showcase finance analytics and data engineering patterns with synthetic data.
- Focuses on forecasting, pipeline best practices, and AI self-service for FP&A teams.
- Designed for easy evaluation by recruiters and technical reviewers without exposing confidential data.

---

## Portfolio snapshot

This repository presents three portfolio demonstrations built with synthetic data and reusable finance analytics patterns.

- Predictive IT cost forecasting for FP&A planning
- Bronze/Silver/Gold cost data pipeline architecture
- AI-assisted self-service financial query workflow

> **Important:** all examples use synthetic or fictional data. No real Bradesco data, pipelines, or proprietary business logic are published here.

---

## Why this portfolio stands out

- Shows end-to-end FP&A delivery thinking: data ingestion, transformation, forecasting, validation, and analytics.
- Highlights real engineering patterns used in banking analytics while preserving confidentiality.
- Demonstrates practical AI query handling, model validation, and reporting automation.
- Makes it easy to explore with local Python demos and clear project documentation.

---

## Featured projects

### `fp-cost-forecast`
Problem addressed: FP&A teams need reliable IT cost forecasting and validation for budget planning.

What this demo shows:
- synthetic monthly IT cost generation for multiple cost centers
- linear regression forecast with recent history and error analysis
- CSV output for forecast results and validation reporting

Stack: `Python · pandas · scikit-learn`

Project docs: [`fp-cost-forecast/README.md`](fp-cost-forecast/README.md)

### `databricks-pipeline-template`
Problem addressed: cost data must be ingested, cleansed, and consolidated into a trusted analytics layer.

What this demo shows:
- Bronze/Silver/Gold Delta Lake pipeline structure
- schema conformance, duplicate handling, and business-ready aggregates
- example management reporting exports for FP&A review

Stack: `Databricks · PySpark · Delta Lake · Python`

Project docs: [`databricks-pipeline-template/README.md`](databricks-pipeline-template/README.md)

### `ai-agent-fpa-query`
Problem addressed: analysts want fast, safe answers without manual ticketing or ad hoc SQL work.

What this demo shows:
- Databricks Genie query workflow and prompt engineering
- synthetic fallback mode for local demos without Databricks credentials
- audit logging pattern for query review and answer validation

Stack: `Python · requests · SQL · API design`

Project docs: [`ai-agent-fpa-query/README.md`](ai-agent-fpa-query/README.md)

---

## Why this portfolio works

- Emphasizes design patterns over raw production data
- Shows how I structure analytics solutions for banking
- Keeps confidentiality intact with synthetic examples and clear disclaimers
- Demonstrates end-to-end thinking: data ingestion, transformation, forecasting, and AI self-service

---

## Repository structure

- `ai-agent-fpa-query/` — AI agent query handler and prompt engineering demo
- `databricks-pipeline-template/` — pipeline structure and transformation examples
- `fp-cost-forecast/` — synthetic forecast model and CSV reporting
- `reports/` — local output directory for generated demo reports (ignored by Git)

---

## Run the demos locally

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the forecast demo:

```powershell
.\run_portfolio.ps1
```

3. Explore notebooks in VS Code or Databricks:

- `fp-cost-forecast/notebooks/it_cost_forecast.ipynb`
- `databricks-pipeline-template/notebooks/cost_pipeline_bronze_silver_gold.ipynb`
- `ai-agent-fpa-query/notebooks/genie_query_handler.ipynb`

> If you are on macOS/Linux, use `./run_portfolio.sh`.

---

## Contact

LinkedIn: [linkedin.com/in/denisisikawa](https://www.linkedin.com/in/denisisikawa)

### ai-agent-fpa-query
An AI agent integration example for FP&A query handling.

- Illustrates Databricks Genie API call patterns
- Includes prompt engineering guidance and synthetic fallback behavior
- Focuses on answer validation and safe analytics workflows

Stack: `Python · Databricks Genie · API design · SQL`

Project docs: [`ai-agent-fpa-query/README.md`](ai-agent-fpa-query/README.md)

---

## Why this portfolio works

- Emphasizes design patterns over raw production data
- Shows how I structure analytics solutions for banking
- Keeps confidentiality intact with synthetic examples and clear disclaimers
- Demonstrates end-to-end thinking: data ingestion, transformation, forecasting, and AI self-service

---

## Repository structure

- `ai-agent-fpa-query/` — AI agent query handler and prompt engineering demo
- `databricks-pipeline-template/` — pipeline structure and transformation examples
- `fp-cost-forecast/` — synthetic forecast model and CSV reporting
- `reports/` — local output directory for generated demo reports (ignored by Git)

---

## Run the demos locally

Each project contains a notebook/script to execute locally. No real data or Databricks credentials are required to explore the synthetic workflow.

---

## Contact

LinkedIn: [linkedin.com/in/denisisikawa](https://www.linkedin.com/in/denisisikawa)