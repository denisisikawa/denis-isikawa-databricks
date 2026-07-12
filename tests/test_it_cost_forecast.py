import importlib.util
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "fp-cost-forecast" / "notebooks" / "it_cost_forecast.py"

spec = importlib.util.spec_from_file_location("it_cost_forecast", SCRIPT_PATH)
it_cost_forecast = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = it_cost_forecast
spec.loader.exec_module(it_cost_forecast)


def test_generate_synthetic_data_shape():
    df = it_cost_forecast.generate_synthetic_data(history_months=12)
    assert len(df) == 12 * 5
    assert set(df.columns) == {"month", "cost_center", "amount"}


def test_build_monthly_summary_pandas_columns():
    df = it_cost_forecast.generate_synthetic_data(history_months=6)
    summary = it_cost_forecast.build_monthly_summary_pandas(df)
    assert set(summary.columns) == {"month", "total_cost", "num_centers"}
    assert len(summary) == 6


def test_run_forecast_outputs(tmp_path):
    output = it_cost_forecast.run_forecast(
        output_dir=str(tmp_path), history_months=12, forecast_horizon=3
    )
    assert os.path.exists(output["forecast_csv"])
    assert os.path.exists(output["validation_csv"])
    assert output["r2"] >= 0
    assert output["history_months"] == 12
    assert output["forecast_horizon"] == 3
