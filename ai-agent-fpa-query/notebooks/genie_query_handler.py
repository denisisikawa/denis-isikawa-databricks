# AI Agent for FP&A — Query Handler Example
# ===========================================
# Purpose: Shows the approach for deploying AI agents
#          (Databricks Genie, Copilot) as natural-language
#          interfaces to financial data.
# NOTE: This is pseudocode/structure — actual Genie setup
#       is done in the Databricks UI and API, not notebook code.
# Data: Synthetic / does not contain Bradesco data
# Stack: Python, SQL (Databricks Genie API)

# ──────────────────────────────────────────────
# CONTEXT — How this fits in the workflow
# ──────────────────────────────────────────────

"""
The goal: an FP&A analyst asks a question in plain English
and gets an answer from the data — without opening a ticket.

Before AI Agent:
  Analyst → Slack to Data Team → Wait 2-3 days → Get Excel → Done

After AI Agent:
  Analyst → Ask Genie → Get answer in seconds

My setup:
  - Gold layer tables are registered as Genie spaces
  - Each space covers a domain (IT Cost, Headcount, Vendor Spend)
  - Analysts get read-only access to Genie
  - Genie answers from Delta Lake gold tables
"""

# ──────────────────────────────────────────────
# EXAMPLE — Python script that wraps Genie API calls
# This is how I'd build a custom interface on top of Genie
# ──────────────────────────────────────────────

import requests
import os
import logging
from typing import Dict, Any, Optional
import pandas as pd

# Databricks workspace configuration (optional when running locally)
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")  # created in Databricks UI

HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}" if DATABRICKS_TOKEN else "",
    "Content-Type": "application/json"
}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("genie_query_handler")


def ask_genie(question: str, space_id: str) -> dict:
    """
    Sends a question to Databricks Genie space and returns the answer.
    Genie reads the gold layer tables and generates a SQL query
    internally, then returns a natural-language answer.
    """
    url = f"{DATABRICKS_HOST}/api/2.0/genie/spaces/{space_id}/messages"
    
    payload = {
        "question": question,
        "generation_config": {
            "max_tokens": 500,
            "temperature": 0.1  # low temp = factual, not creative
        }
    }
    
    if not DATABRICKS_HOST or not DATABRICKS_TOKEN:
        # Running locally without Databricks — return a synthetic response
        logger.info("Databricks credentials not found — returning synthetic response")
        synthetic = {
            "question": question,
            "answer": "Synthetic answer: total IT cost for May 2025 was BRL 1,234,567.89",
            "sql_query": "SELECT SUM(amount) FROM gold.monthly_total WHERE month = '2025-05-01'",
            "sources": ["gold.monthly_total"]
        }
        return synthetic

    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()

    result = response.json()
    return {
        "question": question,
        "answer": result.get("answer"),
        "sql_query": result.get("generated_sql"),  # useful for validation
        "sources": result.get("used_data_sources")
    }


# ──────────────────────────────────────────────
# EXAMPLE — Typical FP&A questions we route to Genie
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # These would be real calls to Databricks API
    # Using example responses to show the pattern
    
    example_questions = [
        "What was the total IT cost for May 2025?",
        "Show me month-over-month variance for cost center CC-03",
        "Which vendors had the highest spend in Q1 2025?",
        "Compare headcount costs vs software licensing costs in 2024",
    ]
    
    for q in example_questions:
        print(f"Q: {q}")
        print(f"→ Genie generates SQL → queries gold layer → returns answer\n")


# ──────────────────────────────────────────────
# PROMPT ENGINEERING — How I tune Genie responses
# ──────────────────────────────────────────────

GENIE_SYSTEM_PROMPT = """
You are a financial data assistant for the IT Cost Analytics team.
You ONLY answer questions about IT costs, headcount, and vendor spend.
You ONLY read from the approved Delta Lake tables in the gold layer.

Rules:
- Always include the SQL query you used in your response
- If the question is ambiguous, ask for clarification before answering
- If data is not available, say so — do not make up numbers
- Use BRL currency format in answers
- Limit responses to 200 words unless asked for detail
""".strip()

"""
How I apply this in Databricks:
1. Create Genie space in UI
2. Attach gold layer tables as data sources
3. Set the system prompt above in the space settings
4. Give FP&A analysts viewer access to the space
5. Optionally build a simple Slack bot or web app on top via API
"""


# ──────────────────────────────────────────────
# LOGGING — Track questions for team review
# ──────────────────────────────────────────────

def log_query(question: str, answer: str, sql: str, analyst: str):
    """
    Logs every Genie query to a Delta table for audit and improvement.
    The data team reviews this weekly to:
    - Catch incorrect answers
    - Identify data quality issues
    - Prioritize new gold layer tables
    """
    log_entry = {
        "timestamp": pd.Timestamp.now(),
        "question": question,
        "answer": answer,
        "sql_generated": sql,
        "analyst": analyst,
        "validated": False  # team marks true after review
    }

    # For local runs we append to a CSV audit log for easy review
    audit_path = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "genie_query_audit.csv")
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    df = pd.DataFrame([log_entry])
    if not os.path.exists(audit_path):
        df.to_csv(audit_path, index=False)
    else:
        df.to_csv(audit_path, mode="a", header=False, index=False)

    logger.info("Query logged for review: %s", question)


def generate_sample_report() -> pd.DataFrame:
    """
    Generates a small synthetic report summarizing IT cost by category and month.
    Returns a pandas DataFrame intended for demo/visualization purposes.
    """
    months = pd.date_range(start="2024-06-01", periods=12, freq='MS')
    categories = ["SOFTWARE", "HARDWARE", "CLOUD", "CONSULTING"]
    rows = []
    for m in months:
        for c in categories:
            rows.append({
                "month": m.strftime("%Y-%m-%d"),
                "category": c,
                "amount_brl": round(100000 * (1 + 0.1 * (categories.index(c))) * (1 + 0.02 * (months.get_loc(m))), 2)
            })
    df = pd.DataFrame(rows)
    report_path = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "genie_sample_report.csv")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df.to_csv(report_path, index=False)
    logger.info("Synthetic Genie report written to %s", report_path)
    return df


if __name__ == "__main__":
    # Demo flow when running the script directly
    q = "What was the total IT cost for May 2025?"
    res = ask_genie(q, GENIE_SPACE_ID or "demo_space")
    print("Answer:", res.get("answer"))
    log_query(res.get("question"), res.get("answer"), res.get("sql_query"), analyst="local_user")
    generate_sample_report()