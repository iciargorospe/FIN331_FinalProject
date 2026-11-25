
# FIN331 Final Project
# Full-sample economic magnitude and hypothetical trading-cost sensitivity

from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs")

summary = pd.read_csv(
    OUTPUT_DIR / "full_sample_summary.csv"
)

# Validate the data
assert len(summary) == 209
assert summary["signalname"].is_unique

required = [
    "original_mean_pct",
    "post_mean_pct",
    "change_pp"
]

assert np.isfinite(summary[required].to_numpy()).all()

# Preserve the original gross-return results
results = summary[[
    "signalname",
    "economic_category",
    "original_mean_pct",
    "post_mean_pct",
    "change_pp"
]].copy()

# Apply hypothetical monthly trading-cost deductions
scenarios_bps = [0, 25, 50]

for cost_bps in scenarios_bps:
    cost_pct = cost_bps / 100

    net_col = f"post_net_{cost_bps}bps_pct"
    profitable_col = f"post_profitable_{cost_bps}bps"

    results[net_col] = (
        results["post_mean_pct"] - cost_pct
    )

    results[profitable_col] = results[net_col] > 0

# Save complete anomaly-level results
results = results.sort_values("signalname")

output_file = OUTPUT_DIR / "full_sample_economic.csv"
results.to_csv(output_file, index=False)

print("FULL-SAMPLE ECONOMIC ANALYSIS")
print("Anomalies:", len(results))

print("\nGROSS RETURNS")
print(
    "Original mean monthly return:",
    round(results["original_mean_pct"].mean(), 4), "%"
)
print(
    "Post-publication mean monthly return:",
    round(results["post_mean_pct"].mean(), 4), "%"
)
print(
    "Average return change:",
    round(results["change_pp"].mean(), 4), "pp"
)

print("\nHYPOTHETICAL TRADING-COST SCENARIOS")

for cost_bps in scenarios_bps:
    net_col = f"post_net_{cost_bps}bps_pct"
    profitable_col = f"post_profitable_{cost_bps}bps"

    n_profitable = int(results[profitable_col].sum())

    print(f"\nMonthly cost: {cost_bps} bps")
    print(
        "Average post-publication net return:",
        round(results[net_col].mean(), 4), "%"
    )
    print(
        "Anomalies with positive net returns:",
        f"{n_profitable} / 209"
    )

print("\nSaved:", output_file)
print(
    "\nNOTE: Costs are hypothetical monthly deductions,"
    " not measured transaction costs."
)
