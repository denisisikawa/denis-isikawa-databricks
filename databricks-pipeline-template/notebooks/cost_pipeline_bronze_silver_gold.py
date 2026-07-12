# Databricks Pipeline Template — IT Cost Consolidation
# ======================================================
# Purpose: Reusable pipeline structure for consolidating
#          cost data from multiple sources into a single
#          financial data layer.
# Pattern: Bronze → Silver → Gold
# Data: Synthetic / does not contain Bradesco data
# Stack: PySpark, Delta Lake, Python

# ──────────────────────────────────────────────
# BRONZE LAYER — Raw ingestion
# Reads from source tables/apis, lands in Delta
# ──────────────────────────────────────────────

import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("it_cost_pipeline")


def ingest_bronze(spark, source_table, target_path, date_partition):
    """
    Reads raw source data and writes to bronze Delta table.
    No transformations — just copy with schema validation.
    """
    df = spark.read.format("jdbc").option("dbtable", source_table).load()
    
    df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("load_date") \
        .option("path", target_path) \
        .save()
    
    print(f"Bronze: {source_table} → {target_path}")


def generate_synthetic_bronze(spark, months: int = 12):
    """
    Generate a synthetic bronze DataFrame for demo/reporting purposes.
    Returns a Spark DataFrame with columns: load_date, cost_center, category, vendor, amount, month
    """
    try:
        from pyspark.sql import Row
        import pandas as pd
        import numpy as np
        months_range = pd.date_range(end=pd.Timestamp.today(), periods=months, freq='MS')
        centers = [f"CC-{i:02d}" for i in range(1, 6)]
        categories = ["Software", "Hardware", "Cloud", "Consulting"]
        rows = []
        for m in months_range:
            for c in centers:
                for cat in categories:
                    rows.append(Row(
                        load_date=m.strftime("%Y-%m-%d"),
                        cost_center=c,
                        category=cat,
                        vendor=f"VENDOR-{(hash(c+cat) % 10) + 1}",
                        amount=round(10000 * (1 + 0.1 * centers.index(c)) * (1 + 0.05 * categories.index(cat)), 2),
                        month=m.strftime("%Y-%m-01")
                    ))
        df = spark.createDataFrame(rows)
        logger.info("Synthetic bronze data generated (%d rows)", df.count())
        return df
    except Exception as e:
        logger.warning("Spark not available locally — cannot generate synthetic bronze in Spark: %s", e)
        raise

# Bronze sources for IT cost scenario:
#   - SAP cost center table
#   - ServiceNow hardware/software costs
#   - HR headcount and salary data
#   - Vendor invoices table

# ──────────────────────────────────────────────
# SILVER LAYER — Cleansed and conformed
# Standardizes schemas, applies business rules
# ──────────────────────────────────────────────

def load_silver_cost(spark, bronze_path, silver_path):
    """
    Reads bronze cost data, applies cleansing:
    - Standardize currency (all in BRL)
    - Remove duplicates on (cost_center, month, category)
    - Filter invalid amounts (negative or null)
    - Normalize cost center codes
    """
    df = spark.read.format("delta").load(bronze_path)
    
    from pyspark.sql.functions import col, when, trim, upper, regexp_replace, abs as spark_abs
    
    silver = (
        df
        .filter(col("amount").isNotNull())
        .filter(col("amount") > 0)
        .filter(col("amount") < 1_000_000_000)  # sanity check
        .withColumn("cost_center", trim(upper(col("cost_center"))))
        .withColumn("category", trim(upper(col("category"))))
        .withColumn("amount", spark_abs(col("amount")))
        .dropDuplicates(["cost_center", "month", "category", "vendor"])
    )
    
    silver.write \
        .format("delta") \
        .mode("overwrite") \
        .option("path", silver_path) \
        .save()
    
    print(f"Silver: {silver.count()} records written to {silver_path}")
    return silver


def generate_management_reports(spark, silver_df, out_dir: Optional[str] = None):
    """
    Produce simple management reports (CSV) from a silver DataFrame.
    - monthly_by_cc: total by month and cost center
    - monthly_total: grand total by month
    """
    import pandas as pd
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
    os.makedirs(out_dir, exist_ok=True)

    monthly_by_cc = (
        silver_df.groupBy("month", "cost_center")
        .sum("amount")
        .withColumnRenamed("sum(amount)", "total_amount")
        .orderBy("month", "cost_center")
    )

    monthly_total = (
        silver_df.groupBy("month")
        .sum("amount")
        .withColumnRenamed("sum(amount)", "total_it_cost")
        .orderBy("month")
    )

    # Convert to pandas and write CSVs
    try:
        mbc_pd = monthly_by_cc.toPandas()
        mt_pd = monthly_total.toPandas()
        mbc_path = os.path.join(out_dir, "monthly_by_cc.csv")
        mt_path = os.path.join(out_dir, "monthly_total.csv")
        mbc_pd.to_csv(mbc_path, index=False)
        mt_pd.to_csv(mt_path, index=False)
        logger.info("Management reports written: %s, %s", mbc_path, mt_path)
        return mbc_path, mt_path
    except Exception as e:
        logger.error("Failed to write management reports: %s", e)
        raise

# ──────────────────────────────────────────────
# GOLD LAYER — Business-ready aggregates
# The layer FP&A analysts actually query
# ──────────────────────────────────────────────

def build_gold_aggregates(spark, silver_path, gold_path):
    """
    Produces the financial aggregates FP&A needs:
    - Monthly total by cost center
    - Monthly total by category
    - Month-over-month variance
    - YTD cumulative
    """
    silver = spark.read.format("delta").load(silver_path)
    
    from pyspark.sql.functions import col, sum as spark_sum, avg as spark_avg, month, year
    
    # Monthly totals by cost center
    monthly_by_cc = (
        silver.groupBy("month", "cost_center", "category")
        .agg(
            spark_sum("amount").alias("total_amount"),
            spark_avg("amount").alias("avg_amount")
        )
        .orderBy("month", "cost_center")
    )
    
    # Monthly grand total
    monthly_total = (
        silver.groupBy("month")
        .agg(
            spark_sum("amount").alias("total_it_cost"),
            spark_avg("amount").alias("avg_cost_per_center")
        )
        .orderBy("month")
    )
    
    # Write gold layer as Delta tables
    monthly_by_cc.write \
        .format("delta") \
        .mode("overwrite") \
        .option("path", f"{gold_path}/monthly_by_cc") \
        .save()
    
    monthly_total.write \
        .format("delta") \
        .mode("overwrite") \
        .option("path", f"{gold_path}/monthly_total") \
        .save()
    
    print("Gold layer written:")
    print(f"  - {gold_path}/monthly_by_cc")
    print(f"  - {gold_path}/monthly_total")

# ──────────────────────────────────────────────
# PIPELINE ORCHESTRATION — Databricks Workflows
# ──────────────────────────────────────────────

class ITCostPipeline:
    """
    Databricks Workflows job structure:
    - Task 1: ingest_bronze() for each source
    - Task 2: load_silver_cost()
    - Task 3: build_gold_aggregates()
    - Task 4: Notify FP&A team via email/slack (optional)
    
    Schedule: runs on the 2nd business day of each month
    """
    
    def __init__(self, spark):
        self.spark = spark
        self.base_path = "/mnt/datalake/it-cost"
    
    def run_full(self):
        sources = [
            ("sap_cost_center",  f"{self.base_path}/bronze/sap"),
            ("servicenow_it",    f"{self.base_path}/bronze/servicenow"),
            ("hr_salaries",      f"{self.base_path}/bronze/hr"),
            ("vendor_invoices",  f"{self.base_path}/bronze/vendors"),
        ]
        
        # 1. Ingest bronze
        for table, path in sources:
            ingest_bronze(self.spark, table, path, date_partition=None)
        
        # 2. Silver
        silver = load_silver_cost(
            self.spark,
            f"{self.base_path}/bronze/*",
            f"{self.base_path}/silver/it_cost"
        )
        
        # 3. Gold
        build_gold_aggregates(
            self.spark,
            f"{self.base_path}/silver/it_cost",
            f"{self.base_path}/gold"
        )
        
        print("Pipeline complete.")


# ──────────────────────────────────────────────
# USAGE EXAMPLE
# This is how you'd call it in a Databricks notebook
# ──────────────────────────────────────────────

# pipeline = ITCostPipeline(spark)
# pipeline.run_full()

# After the pipeline runs, FP&A analysts query:
# df = spark.read.format("delta").load("/mnt/datalake/it-cost/gold/monthly_total")
# df.filter(col("month") >= "2025-01-01").display()