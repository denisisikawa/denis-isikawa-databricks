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

# Databricks workspace configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")  # created in Databricks UI

HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}


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
        "timestamp": "CURRENT_TIMESTAMP",  # use current_timestamp() in real code
        "question": question,
        "answer": answer,
        "sql_generated": sql,
        "analyst": analyst,
        "validated": False  # team marks true after review
    }
    
    # Append to Delta table
    # spark.createDataFrame([log_entry]).write \
    #     .format("delta") \
    #     .mode("append") \
    #     .option("path", "/mnt/audit/genie_queries") \
    #     .save()
    
    print("Query logged for review.")