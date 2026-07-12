"""Generate demo plots (forecast and validation) for portfolio README.

This script runs the forecast demo to produce CSV outputs and then
creates two PNG images saved under `images/`:
 - forecast_plot.png
 - validation_plot.png

Usage:
    python scripts/generate_demo_plots.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

# Run the forecast demo to produce CSV outputs in the images folder
cmd = [sys.executable, str(ROOT / "fp-cost-forecast" / "notebooks" / "it_cost_forecast.py"),
       "--output-dir", str(IMAGES), "--months", "36", "--forecast-horizon", "6"]
print("Running demo to generate CSVs:", " ".join(cmd))
subprocess.run(cmd, check=True)

# Load forecast results
forecast_csv = IMAGES / "forecast_result.csv"
validation_csv = IMAGES / "forecast_validation.csv"

if forecast_csv.exists():
    df = pd.read_csv(forecast_csv, parse_dates=["month"])
    actual = df[df["type"] == "actual"].set_index("month")
    forecast = df[df["type"] == "forecast"].set_index("month")

    plt.figure(figsize=(10, 5))
    plt.plot(actual.index, actual["cost"], label="Actual")
    plt.plot(forecast.index, forecast["cost"], label="Forecast", linestyle="--")
    plt.title("IT Cost: Actual vs Forecast (demo)")
    plt.xlabel("Month")
    plt.ylabel("Cost (BRL)")
    plt.legend()
    plt.grid(True)
    out1 = IMAGES / "forecast_plot.png"
    plt.savefig(out1, bbox_inches="tight")
    print("Saved", out1)
    plt.close()
else:
    print("forecast_result.csv not found; skipping forecast plot generation")

if validation_csv.exists():
    vdf = pd.read_csv(validation_csv, parse_dates=["month"])
    plt.figure(figsize=(8, 4))
    plt.bar(vdf["month"].astype(str), vdf["error_pct"].abs())
    plt.title("Forecast absolute error % (last periods)")
    plt.xlabel("Month")
    plt.ylabel("Absolute error (%)")
    plt.xticks(rotation=45)
    out2 = IMAGES / "validation_plot.png"
    plt.savefig(out2, bbox_inches="tight")
    print("Saved", out2)
    plt.close()
else:
    print("forecast_validation.csv not found; skipping validation plot generation")
