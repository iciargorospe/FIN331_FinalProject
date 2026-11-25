
# FIN331 Final Project
# Robustness check: 1st/99th percentile winsorized returns

from pathlib import Path
import subprocess
import sys
import tempfile

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = Path("outputs")

# Load the original full-sample dataset
source = OUTPUT_DIR / "full_sample_analysis.csv"

if source.exists():
    data = pd.read_csv(source)
else:
    data = pd.read_csv(
        OUTPUT_DIR / "full_sample_analysis.csv.gz",
        compression="gzip"
    )

assert len(data) == 135466
assert data["signalname"].nunique() == 209
assert not data.duplicated(["signalname", "month"]).any()

# Calculate pooled 1st and 99th percentile thresholds
lower = data["ret"].quantile(0.01)
upper = data["ret"].quantile(0.99)

n_lower = int((data["ret"] < lower).sum())
n_upper = int((data["ret"] > upper).sum())

# Cap extreme monthly returns
winsorized = data.copy()
winsorized["ret"] = winsorized["ret"].clip(
    lower=lower,
    upper=upper
)

# Rerun the existing regression using temporary files
# This protects the original dataset and regression results.
with tempfile.TemporaryDirectory() as temp:
    work = Path(temp)
    (work / "outputs").mkdir()

    winsorized.to_csv(
        work / "outputs/full_sample_analysis.csv",
        index=False
    )

    subprocess.run(
        [sys.executable, str(ROOT / "full_sample_regression.py")],
        cwd=work,
        check=True
    )

    robust = pd.read_csv(
        work / "outputs/full_sample_regression.csv"
    )

# Load the original regression results
original = pd.read_csv(
    OUTPUT_DIR / "full_sample_regression.csv"
)

# Compare the same six estimates
columns = [
    "model",
    "variable",
    "coefficient",
    "standard_error",
    "p_value"
]

results = original[columns].merge(
    robust[columns],
    on=["model", "variable"],
    suffixes=("_original", "_winsorized"),
    validate="one_to_one"
)

assert len(results) == 6

# Record the thresholds for reproducibility
results["lower_cutoff_pct"] = lower
results["upper_cutoff_pct"] = upper
results["observations_capped_lower"] = n_lower
results["observations_capped_upper"] = n_upper

# Save without overwriting the original regression
output_file = (
    OUTPUT_DIR / "full_sample_winsorized_regression.csv"
)
results.to_csv(output_file, index=False)

print("WINSORIZED REGRESSION ROBUSTNESS CHECK")
print("Lower cutoff:", round(lower, 4), "%")
print("Upper cutoff:", round(upper, 4), "%")
print("Observations capped below:", n_lower)
print("Observations capped above:", n_upper)

print("\nORIGINAL VS. WINSORIZED RESULTS")
print(results[[
    "model",
    "variable",
    "coefficient_original",
    "p_value_original",
    "coefficient_winsorized",
    "p_value_winsorized"
]].round(5).to_string(index=False))

print("\nSaved:", output_file)
