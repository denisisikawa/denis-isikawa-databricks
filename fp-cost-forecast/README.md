# FP Cost Forecast

A synthetic IT cost forecasting demo designed to show how FP&A planning teams can model IT spend and validate forecast accuracy.

## Problem

FP&A teams need a transparent, repeatable way to forecast IT costs and compare predicted spend against actuals for budgeting and cost control.

## Value delivered

- demonstrates a complete forecast workflow from synthetic cost generation to validation
- provides business-friendly CSV output for forecasting and error review
- helps showcase how a finance team can move from raw cost data to actionable planning insight

## What it includes

- synthetic monthly IT cost data for multiple cost centers
- monthly aggregation and feature preparation
- linear regression forecast with the last 12 months of history
- validation calculations and error percentage reporting
- local CSV output for forecast and validation results

## Stack

- Python
- pandas
- numpy
- scikit-learn

## Run locally

```bash
python fp-cost-forecast/notebooks/it_cost_forecast.py
```

Open the notebook version for a more interactive walkthrough:

- `fp-cost-forecast/notebooks/it_cost_forecast.ipynb`

## Output

- `reports/forecast_result.csv`
- `reports/forecast_validation.csv`

> The `reports/` folder is ignored by Git and is used only for local demo outputs.

## Data confidentiality

All data in this project is synthetic and fictional. **No real Bradesco data is used or shared.**
