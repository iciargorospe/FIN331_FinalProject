
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
from pathlib import Path

# Load our existing five-anomaly dataset
df = pd.read_csv("outputs/checkpoint1_sample.csv")

# Calculate a period mean with Newey-West standard errors
def hac_mean(returns):
    y = returns.to_numpy()

    model = sm.OLS(
        y, np.ones((len(y), 1))
    ).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": 12}
    )

    return model.params[0], model.bse[0]

rows = []

# Test the original-to-post change for each anomaly
for anomaly, group in df.groupby("signalname"):
    group = group.sort_values("month")

    original = group.loc[
        group["period"] == "Original Sample", "ret"
    ].dropna()

    post = group.loc[
        group["period"] == "Post-Publication", "ret"
    ].dropna()

    original_mean, original_se = hac_mean(original)
    post_mean, post_se = hac_mean(post)

    difference = post_mean - original_mean

    # Approximation: treat the separated periods
    # as independent when combining standard errors
    se_difference = np.sqrt(
        original_se**2 + post_se**2
    )

    z_stat = difference / se_difference
    p_value = 2 * norm.sf(abs(z_stat))

    rows.append({
        "anomaly": anomaly,
        "original_mean": original_mean,
        "post_mean": post_mean,
        "difference_pp": difference,
        "standard_error": se_difference,
        "p_value": p_value
    })

results = pd.DataFrame(rows)

# Adjust p-values for testing multiple anomalies
results["adjusted_p_value"] = multipletests(
    results["p_value"],
    method="fdr_bh"
)[1]

results["significant_after_BH"] = (
    results["adjusted_p_value"] < 0.05
)

# Save our results for reproducibility
Path("outputs").mkdir(exist_ok=True)

results.to_csv(
    "outputs/prototype_anomaly_tests.csv",
    index=False
)

print("Individual anomaly tests completed successfully!")
print("\nINDIVIDUAL ANOMALY TESTS:")
print(results.round(4).to_string(index=False))
