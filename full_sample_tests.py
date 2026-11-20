
# FIN331 Checkpoint 3: Full-sample anomaly significance tests

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

OUTPUT_DIR = Path("outputs")

# Load the final 209-anomaly dataset
df = pd.read_csv(OUTPUT_DIR / "full_sample_analysis.csv")

# Calculate a period's mean return and Newey-West standard error
def hac_mean(returns):
    y = returns.to_numpy(dtype=float)

    model = sm.OLS(
        y,
        np.ones((len(y), 1))
    ).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": 12}
    )

    return float(model.params[0]), float(model.bse[0])


rows = []

# Perform a separate original-vs-post test for each anomaly
for anomaly, group in df.groupby("signalname"):
    group = group.sort_values("month")

    original = group.loc[
        group["period"] == "Original Sample", "ret"
    ].dropna()

    post = group.loc[
        group["period"] == "Post-Publication", "ret"
    ].dropna()

    # Verify that both periods meet our selection rule
    assert len(original) >= 24
    assert len(post) >= 24

    original_mean, original_se = hac_mean(original)
    post_mean, post_se = hac_mean(post)

    # Change in mean monthly return, in percentage points
    difference = post_mean - original_mean

    # Same approximation used in our five-anomaly prototype:
    # treat the two separated periods as independent
    se_difference = np.sqrt(
        original_se**2 + post_se**2
    )

    assert se_difference > 0

    z_stat = difference / se_difference

    # Two-sided test: is the change different from zero?
    p_value = 2 * norm.sf(abs(z_stat))

    rows.append({
        "anomaly": anomaly,
        "original_months": len(original),
        "post_months": len(post),
        "original_mean": original_mean,
        "post_mean": post_mean,
        "difference_pp": difference,
        "standard_error": se_difference,
        "z_stat": z_stat,
        "p_value": p_value
    })

results = pd.DataFrame(rows).sort_values(
    "anomaly"
).reset_index(drop=True)

# Adjust ALL 209 p-values together using Benjamini-Hochberg
results["adjusted_p_value"] = multipletests(
    results["p_value"],
    alpha=0.05,
    method="fdr_bh"
)[1]

results["significant_after_BH"] = (
    results["adjusted_p_value"] < 0.05
)

# Identify whether each significant change is a decline or increase
results["significant_decline"] = (
    results["significant_after_BH"] &
    (results["difference_pp"] < 0)
)

results["significant_increase"] = (
    results["significant_after_BH"] &
    (results["difference_pp"] > 0)
)

# Validate results
assert len(results) == 209
assert results["anomaly"].nunique() == 209
assert np.isfinite(results["standard_error"]).all()
assert results["p_value"].between(0, 1).all()
assert results["adjusted_p_value"].between(0, 1).all()

# Save all results, not just significant ones
output_file = OUTPUT_DIR / "full_sample_tests.csv"
results.to_csv(output_file, index=False)

# Display summary findings
print("FULL-SAMPLE STATISTICAL TEST RESULTS")
print("Anomalies tested:", len(results))

print("\nBEFORE MULTIPLE-TESTING ADJUSTMENT")
print("Significant at 5%:",
      (results["p_value"] < 0.05).sum())

print("\nAFTER BENJAMINI-HOCHBERG ADJUSTMENT")
print("Significant changes:",
      results["significant_after_BH"].sum())
print("Significant declines:",
      results["significant_decline"].sum())
print("Significant increases:",
      results["significant_increase"].sum())

print("\nDESCRIPTIVE COMPARISON")
print("Total anomalies with declining returns:",
      (results["difference_pp"] < 0).sum())

print("\nTEN LOWEST ADJUSTED P-VALUES:")
display_columns = [
    "anomaly", "difference_pp", "standard_error",
    "p_value", "adjusted_p_value",
    "significant_decline"
]

print(
    results.sort_values("adjusted_p_value")[
        display_columns
    ].head(10).round(5).to_string(index=False)
)

print("\nSaved to:", output_file)
