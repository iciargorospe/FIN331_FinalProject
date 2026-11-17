# Run the entire Checkpoint 2 pipeline

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

print("Pipeline completed successfully!")
