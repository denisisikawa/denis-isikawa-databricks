# Databricks Notebook: IT Cost Forecasting Model
# ===============================================
# Purpose: Demonstrate IT cost forecasting approach
# Data: Synthetic — does not contain Bradesco data
# Stack: Pandas, scikit-learn (simplified)

import argparse
import logging
import os
import sys

import numpy as np
import pandas as pd

SPARK_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("it_cost_forecast")

report_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
os.makedirs(report_dir, exist_ok=True)


def generate_synthetic_data(history_months: int = 25) -> pd.DataFrame:
    """Create synthetic monthly IT cost records for the forecast demo.

    Parameters
    ----------
    history_months : int
        Number of historical months to generate for the synthetic series.
    """
    np.random.seed(42)

    months = pd.date_range(end="2025-01-01", periods=history_months, freq="MS")
    data = []

    for month_index, month in enumerate(months):
        base_cost = 100000
        for center_id in range(1, 6):
            seasonal = 1 + 0.08 * np.sin(2 * np.pi * month_index / 12)
            trend = 1 + 0.005 * month_index
            noise = 1 + np.random.normal(0, 0.03)
            cost = base_cost * center_id * seasonal * trend * noise
            data.append({
                "month": month,
                "cost_center": f"CC-{center_id:02d}",
                "amount": round(cost, 2),
            })

    return pd.DataFrame(data)


def build_monthly_summary_pandas(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa dados por mês e calcula total de custo e número de cost centers."""
    monthly = (
        df.groupby("month", as_index=False)
        .agg(total_cost=("amount", "sum"), num_centers=("cost_center", "nunique"))
        .sort_values("month")
    )
    return monthly


def run_forecast(output_dir: str = None, history_months: int = 25, forecast_horizon: int = 3) -> dict:
    """Executa o fluxo de forecast e escreve os relatórios em CSV."""
    if output_dir is None:
        output_dir = report_dir

    logger.info("Running forecast in pandas-only mode.")
    pdf = generate_synthetic_data(history_months)
    monthly_pd = build_monthly_summary_pandas(pdf)

    monthly_pd["month_num"] = range(len(monthly_pd))

    recent = monthly_pd.tail(12).copy()
    x = recent["month_num"].values.reshape(-1, 1)
    y = recent["total_cost"].values

    from sklearn.linear_model import LinearRegression

    model = LinearRegression()
    model.fit(x, y)

    last_month = monthly_pd["month"].max()
    forecast_months = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=forecast_horizon,
        freq="MS",
    )
    future_index = np.arange(
        monthly_pd["month_num"].max() + 1,
        monthly_pd["month_num"].max() + 1 + forecast_horizon,
    ).reshape(-1, 1)

    forecast = pd.DataFrame({
        "month": forecast_months,
        "forecast_cost": model.predict(future_index),
    })

    historical = monthly_pd[["month", "total_cost"]].copy()
    historical.columns = ["month", "cost"]
    historical["type"] = "actual"

    forecast_out = forecast.copy()
    forecast_out.columns = ["month", "cost"]
    forecast_out["type"] = "forecast"

    result = pd.concat([historical, forecast_out]).sort_values("month")

    result_path = os.path.join(output_dir, "forecast_result.csv")
    result.to_csv(result_path, index=False)
    logger.info("Forecast result written to %s", result_path)

    validation = monthly_pd.tail(6).copy()
    validation["predicted"] = model.predict(validation["month_num"].values.reshape(-1, 1))
    validation["error_pct"] = ((validation["total_cost"] - validation["predicted"]) / validation["total_cost"] * 100).round(2)

    validation_path = os.path.join(output_dir, "forecast_validation.csv")
    validation.to_csv(validation_path, index=False)
    logger.info("Validation CSV written to %s", validation_path)

    mean_error = validation["error_pct"].abs().mean()
    r2 = model.score(x, y)

    return {
        "forecast_csv": result_path,
        "validation_csv": validation_path,
        "mean_error_pct": mean_error,
        "r2": r2,
        "history_months": history_months,
        "forecast_horizon": forecast_horizon,
        "spark_available": SPARK_AVAILABLE,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the IT cost forecast demo with synthetic data."
    )
    parser.add_argument(
        "--output-dir",
        default=report_dir,
        help="Directory to save forecast and validation CSV reports.",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=25,
        help="Number of historical synthetic months to generate.",
    )
    parser.add_argument(
        "--forecast-horizon",
        type=int,
        default=3,
        help="Number of future months to forecast.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    output = run_forecast(
        output_dir=args.output_dir,
        history_months=args.months,
        forecast_horizon=args.forecast_horizon,
    )
    logger.info("Run complete: %s", output)
    print(output)


if __name__ == "__main__":
    main(sys.argv[1:])
