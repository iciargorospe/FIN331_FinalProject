# Run the full FIN331 project analysis pipeline

from pathlib import Path
import subprocess
import sys
import csv
import json

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

# Step 1: Run our original data notebook
print("Step 1: Building anomaly dataset...", flush=True)

notebook = nbformat.read(
    ROOT / "01_seed4_poc.ipynb", as_version=4
)

client = NotebookClient(
    notebook,
    timeout=900,
    kernel_name="python3",
    resources={"metadata": {"path": str(ROOT)}}
)

client.execute()

assert (OUTPUTS / "checkpoint1_sample.csv").exists()

# Step 2: Prepare website data
print("Step 2: Preparing website data...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "prepare_data.py")],
    cwd=ROOT,
    check=True
)

# Step 3: Save a results table
print("Step 3: Saving results table...", flush=True)

with (OUTPUTS / "explorer_data.json").open(
    encoding="utf-8"
) as f:
    data = json.load(f)

with (OUTPUTS / "period_summary.csv").open(
    "w", newline="", encoding="utf-8"
) as f:
    writer = csv.writer(f)

    writer.writerow([
        "signalname", "period",
        "observations", "avg_monthly_return"
    ])

    for anomaly in data["anomalies"]:
        for period in [
            "original_sample",
            "gap",
            "post_publication"
        ]:
            summary = anomaly["summary"][period]

            writer.writerow([
                anomaly["signal"],
                summary["label"],
                summary["observations"],
                summary["mean_monthly_pct"]
            ])

# Step 4: Run our panel regression analysis
print("Step 4: Running panel regressions...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "regression_analysis.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "prototype_regression_results.csv").exists()

# Step 5: Run individual anomaly significance tests
print("Step 5: Running anomaly significance tests...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "anomaly_tests.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "prototype_anomaly_tests.csv").exists()

# Step 6: Calculate economic magnitude and trading-cost sensitivity
print("Step 6: Running economic analysis...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "economic_analysis.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "prototype_economic_results.csv").exists()

# Step 7: Build our full-sample analysis dataset
print("Step 7: Building full-sample dataset...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "build_full_sample.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_analysis.csv").exists()

# Step 8: Generate full-sample descriptive results
print("Step 8: Calculating full-sample summary statistics...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_summary.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_summary.csv").exists()

# Step 9: Run full-sample statistical significance tests
print("Step 9: Running full-sample significance tests...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_tests.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_tests.csv").exists()

# Step 10: Run full-sample panel regressions
print("Step 10: Running full-sample panel regressions...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_regression.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_regression.csv").exists()

# Step 11: Analyze differences across economic categories
print("Step 11: Running full-sample category analysis...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_categories.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_categories.csv").exists()

# Step 12: Run equal-length sample robustness analysis
print("Step 12: Running equal-length robustness tests...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_robustness.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_robustness.csv").exists()

# Step 13: Analyze full-sample economic magnitude and trading-cost sensitivity
print("Step 13: Running full-sample economic analysis...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_economic.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_economic.csv").exists()

# Step 14: Test regression sensitivity to extreme monthly returns
print("Step 14: Running winsorized regression robustness check...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_winsorized_regression.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_winsorized_regression.csv").exists()

# Step 15: Test sensitivity to two-way clustered standard errors
print("Step 15: Running two-way clustering robustness check...", flush=True)

subprocess.run(
    [sys.executable, str(ROOT / "full_sample_two_way_clustering.py")],
    cwd=ROOT,
    check=True
)

assert (OUTPUTS / "full_sample_two_way_clustering.csv").exists()

print("Pipeline completed successfully!")
