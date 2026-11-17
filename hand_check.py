# Independent verification of our Momentum original-sample mean.

import csv
import math
from pathlib import Path

import pandas as pd
import openassetpricing as oap

ROOT = Path(__file__).resolve().parent
DATA_RELEASE = 202610
SIGNAL = "Mom12m"

# Step 1: Download the original data independently.
openap = oap.OpenAP(DATA_RELEASE)
documentation = openap.dl_signal_doc("pandas")
portfolios = openap.dl_port("op", "pandas", [SIGNAL])

# Step 2: Get the original research sample dates.
paper = documentation.loc[
    documentation["Acronym"] == SIGNAL
]

assert len(paper) == 1, "Expected one Momentum documentation row."

start_year = int(paper.iloc[0]["SampleStartYear"])
end_year = int(paper.iloc[0]["SampleEndYear"])

# Step 3: Select monthly long-short returns from those years.
returns = portfolios.loc[
    (portfolios["signalname"] == SIGNAL)
    & (portfolios["port"] == "LS")
].copy()

years = pd.to_datetime(returns["date"]).dt.year

original_returns = returns.loc[
    years.between(start_year, end_year), "ret"
].astype(float)

assert len(original_returns) > 0, "No original-sample returns found."

# Calculate the mean independently.
hand_count = len(original_returns)
hand_mean = sum(original_returns) / hand_count

# Step 4: Read the result from our existing pipeline.
summary_path = ROOT / "outputs" / "period_summary.csv"

with summary_path.open(newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

matches = [
    row for row in rows
    if row["signalname"] == SIGNAL
    and row["period"] == "Original research sample"
]

assert len(matches) == 1, "Expected one matching summary row."

pipeline_count = int(matches[0]["observations"])
pipeline_mean = float(matches[0]["avg_monthly_return"])

# Step 5: Compare the two independently calculated results.
assert hand_count == pipeline_count, "Observation counts do not match."

assert math.isclose(
    hand_mean, pipeline_mean, rel_tol=1e-10, abs_tol=1e-10
), "Average monthly returns do not match."

print("Independent hand check PASSED!")
print(f"Anomaly: {SIGNAL}")
print(f"Original sample: {start_year}-{end_year}")
print(f"Observations: {hand_count}")
print(f"Independent mean: {hand_mean:.6f}%")
print(f"Pipeline mean:    {pipeline_mean:.6f}%")
