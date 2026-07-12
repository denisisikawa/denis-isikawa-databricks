# Databricks Notebook: IT Cost Forecasting Model
# ===============================================
# Purpose: Demonstrate IT cost forecasting approach
# Data: Synthetic — does not contain Bradesco data
# Stack: PySpark, Pandas, scikit-learn (simplified)

# ──────────────────────────────────────────────
# STEP 1 — Generate synthetic cost data
# In production, this reads from Delta Lake tables
# ──────────────────────────────────────────────

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, months_add, regexp_replace, to_date, split, expr
)
from pyspark.sql.types import DoubleType, IntegerType
import random
import pandas as pd
import numpy as np

spark = SparkSession.builder.getOrCreate()

# Generate 24 months of synthetic IT cost data
# 5 cost centers, monthly totals, with seasonal pattern + trend
random.seed(42)
np.random.seed(42)

data = []
for month_offset in range(-24, 1):
    base_cost = 100000
    for center_id in range(1, 6):
        seasonal = 1 + 0.08 * np.sin(2 * np.pi * month_offset / 12)
        trend = 1 + 0.005 * abs(month_offset)
        noise = 1 + np.random.normal(0, 0.03)
        cost = base_cost * center_id * seasonal * trend * noise
        data.append({
            'month': f'2024-{13 + month_offset:02d}' if month_offset < 0 else f'2025-{month_offset + 1:02d}',
            'cost_center': f'CC-{center_id:02d}',
            'amount': round(cost, 2)
        })

df = spark.createDataFrame(data)
df = df.withColumn('month', to_date(col('month'), 'yyyy-MM'))
df = df.withColumn('amount', col('amount').cast(DoubleType()))
df = df.orderBy('month', 'cost_center')

display(df)
print(f"Records: {df.count()}")

# ──────────────────────────────────────────────
# STEP 2 — Data quality checks (bronze layer)
# ──────────────────────────────────────────────

from pyspark.sql.functions import count, when, min, max, avg, stddev

quality = df.select(
    count('*').alias('total_rows'),
    count(when(col('amount').isNull(), 1)).alias('null_amounts'),
    min('amount').alias('min_amount'),
    max('amount').alias('max_amount'),
    avg('amount').alias('avg_amount')
)
display(quality)

# ──────────────────────────────────────────────
# STEP 3 — Aggregate to monthly total (silver layer)
# ──────────────────────────────────────────────

monthly = df.groupBy('month').agg(
    sum('amount').alias('total_cost'),
    count('cost_center').alias('num_centers')
).orderBy('month')

display(monthly)

# ──────────────────────────────────────────────
# STEP 4 — Simple trend-based forecast
# Using last 6 months to project next 3
# ──────────────────────────────────────────────

# Convert to Pandas for the modeling step
monthly_pd = monthly.toPandas()
monthly_pd['month_num'] = range(len(monthly_pd))

# Fit linear regression on last 12 months
recent = monthly_pd.tail(12).copy()
x = recent['month_num'].values.reshape(-1, 1)
y = recent['total_cost'].values

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(x, y)

# Project next 3 months
future_months = monthly_pd.tail(3)['month_num'].max() + np.arange(1, 4)
forecast = pd.DataFrame({
    'month': pd.date_range(
        start=monthly_pd['month'].max(),
        periods=4,
        freq='MS'
    )[1:],
    'forecast_cost': model.predict(future_months.reshape(-1, 1))
})

# Combine historical + forecast
historical = monthly_pd[['month', 'total_cost']].copy()
historical.columns = ['month', 'cost']
historical['type'] = 'actual'

forecast_out = forecast.copy()
forecast_out.columns = ['month', 'cost']
forecast_out['type'] = 'forecast'

result = pd.concat([historical, forecast_out]).sort_values('month')
print(result.to_string(index=False))

# ──────────────────────────────────────────────
# STEP 5 — Variance analysis
# Compare actuals vs forecast for known months (validation)
# ──────────────────────────────────────────────

validation = monthly_pd.tail(6).copy()
validation['predicted'] = model.predict(validation['month_num'].values.reshape(-1, 1))
validation['error_pct'] = ((validation['total_cost'] - validation['predicted']) / validation['total_cost'] * 100).round(2)

print("\nValidation — last 6 months:")
print(validation[['month', 'total_cost', 'predicted', 'error_pct']].to_string(index=False))

mean_error = validation['error_pct'].abs().mean()
print(f"\nMean absolute error: {mean_error:.1f}%")
print(f"R² on recent data: {model.score(x, y):.4f}")