# Databricks Pipeline Template

A reusable Bronze/Silver/Gold pipeline template for financial cost data consolidation and reporting.

## Problem

Cost data from multiple sources must be ingested, cleansed, and transformed into a trusted analytics layer before FP&A can reliably report on it.

## Value delivered

- illustrates a structured Delta Lake pipeline approach for finance data
- demonstrates schema conformance, duplicate handling, and business-ready aggregates
- includes example management reporting outputs for cost analysis

## What it includes

- Bronze ingestion pattern for raw source data
- Silver transformation and standardization
- Gold layer aggregates suitable for FP&A reporting
- synthetic data generation examples for local development
- management report export examples

## Stack

- Databricks
- PySpark
- Delta Lake
- Python

## Run locally

This code is designed as a notebook-style template and can be explored in Databricks or by reading the Python script.

Open the notebook:

- `databricks-pipeline-template/notebooks/cost_pipeline_bronze_silver_gold.ipynb`

## Notes

- The notebook presents reusable pipeline architecture without proprietary data.
- Use `pyspark` only if you want to run the pipeline template locally outside Databricks.

## Data confidentiality

This project is intentionally synthetic. **No real Bradesco data is included or published.** The code focuses on patterns and architecture rather than proprietary data.
