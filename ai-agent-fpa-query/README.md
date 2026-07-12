# AI Agent FP&A Query

A portfolio demonstration of how AI agents can enable self-service analytics for finance teams.

## Problem

FP&A analysts often spend time waiting for data teams to answer cost and spend questions. This slows decision-making and increases ad hoc reporting workload.

## Value delivered

- shows how a natural-language query workflow can speed FP&A access to insights
- defines safe prompt engineering and answer validation patterns
- includes a synthetic fallback mode for local demos without Databricks credentials
- provides an audit logging pattern to track and review AI query responses

## What it includes

- example Genie API wrapper for submitting natural-language questions
- synthetic response fallback when Databricks credentials are not available
- prompt engineering guidance for safe financial responses
- logging and auditing pattern for query handling
- sample synthetic report generation for demo purposes

## Stack

- Python
- requests
- Databricks Genie API patterns
- SQL analytics patterns

## How to explore

Open the notebook:

- `ai-agent-fpa-query/notebooks/genie_query_handler.ipynb`

Run the script locally to see the demo flow and synthetic answer behavior:

```bash
python ai-agent-fpa-query/notebooks/genie_query_handler.py
```

## Data confidentiality

This example is intentionally synthetic. **No real Bradesco data or sensitive analytics are stored or shared.** It demonstrates architecture and interaction patterns only.

> The local demo uses synthetic answers and does not require Databricks credentials.
