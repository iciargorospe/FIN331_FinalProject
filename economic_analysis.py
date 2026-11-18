
import numpy as np
import pandas as pd
from pathlib import Path

# Load results from our individual anomaly tests
economic = pd.read_csv(
    "outputs/prototype_anomaly_tests.csv"
)

# Calculate relative changes in profitability
# Only when original mean exceeds 0.05% per month
economic["relative_change_pct"] = np.where(
    economic["original_mean"] > 0.05,
    100 * economic["difference_pp"] / economic["original_mean"],
    np.nan
)

# Apply hypothetical monthly trading costs
for cost_bps in [0, 25, 50]:
    cost_pct = cost_bps / 100

    economic[f"net_return_{cost_bps}bps"] = (
        economic["post_mean"] - cost_pct
    )

# Select the economic results we want to report
columns = [
    "anomaly",
    "original_mean",
    "post_mean",
    "difference_pp",
    "relative_change_pct",
    "net_return_0bps",
    "net_return_25bps",
    "net_return_50bps"
]

results = economic[columns]

# Save the results
Path("outputs").mkdir(exist_ok=True)

results.to_csv(
    "outputs/prototype_economic_results.csv",
    index=False
)

print("Economic magnitude analysis completed successfully!")
print("\nECONOMIC MAGNITUDE AND TRADING-COST SENSITIVITY:")
print(results.round(4).to_string(index=False))
