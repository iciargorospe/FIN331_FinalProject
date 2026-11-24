
# FIN331 Checkpoint 3: Equal-length sample robustness test

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

OUTPUT_DIR = Path("outputs")

# 1. Load our original data and results
df = pd.read_csv(
    OUTPUT_DIR / "full_sample_analysis.csv"
)

full_tests = pd.read_csv(
    OUTPUT_DIR / "full_sample_tests.csv"
)

assert df["signalname"].nunique() == 209
assert full_tests["anomaly"].nunique() == 209


# 2. Same Newey-West calculation used in our primary tests
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

# 3. Compare equally many observations for each anomaly
for anomaly, group in df.groupby("signalname"):

    group = group.sort_values("month")

    original = group.loc[
        group["period"] == "Original Sample"
    ].sort_values("month")

    post = group.loc[
        group["period"] == "Post-Publication"
    ].sort_values("month")

    # Use the smaller of the two sample sizes
    window = min(len(original), len(post))

    assert window >= 24

    # Select observations nearest the end of the original
    # sample and the beginning of the post-publication period
    original_balanced = original.tail(window)
    post_balanced = post.head(window)

    assert len(original_balanced) == len(post_balanced)

    original_mean, original_se = hac_mean(
        original_balanced["ret"]
    )

    post_mean, post_se = hac_mean(
        post_balanced["ret"]
    )

    difference = post_mean - original_mean

    # Same separated-period independence approximation
    # used in the primary statistical tests
    se_difference = np.sqrt(
        original_se**2 + post_se**2
    )

    assert se_difference > 0

    z_stat = difference / se_difference
    p_value = float(2 * norm.sf(abs(z_stat)))

    rows.append({
        "anomaly": anomaly,
        "months_per_period": window,
        "original_mean": original_mean,
        "post_mean": post_mean,
        "difference_pp": difference,
        "standard_error": se_difference,
        "p_value": p_value
    })


# 4. Adjust all 209 p-values together
results = pd.DataFrame(rows).sort_values(
    "anomaly"
).reset_index(drop=True)

results["adjusted_p_value"] = multipletests(
    results["p_value"],
    alpha=0.05,
    method="fdr_bh"
)[1]

results["declined"] = results["difference_pp"] < 0

results["significant_decline"] = (
    results["declined"] &
    (results["adjusted_p_value"] < 0.05)
)

results["significant_increase"] = (
    (results["difference_pp"] > 0) &
    (results["adjusted_p_value"] < 0.05)
)


# 5. Compare with our original full-period results
comparison = results.merge(
    full_tests[[
        "anomaly", "difference_pp", "significant_decline"
    ]],
    on="anomaly",
    how="inner",
    validate="one_to_one",
    suffixes=("_balanced", "_full")
)

assert len(comparison) == 209

comparison["same_direction"] = (
    np.sign(comparison["difference_pp_balanced"]) ==
    np.sign(comparison["difference_pp_full"])
)


# 6. Validate and save
assert len(results) == 209
assert (results["months_per_period"] >= 24).all()
assert results["p_value"].between(0, 1).all()
assert results["adjusted_p_value"].between(0, 1).all()

output_file = OUTPUT_DIR / "full_sample_robustness.csv"
results.to_csv(output_file, index=False)


# 7. Print the findings
print("EQUAL-LENGTH ROBUSTNESS RESULTS")
print("Anomalies tested:", len(results))

print("\nNUMBER OF MONTHS PER PERIOD")
print("Minimum:", results["months_per_period"].min())
print("Median:", results["months_per_period"].median())
print("Maximum:", results["months_per_period"].max())

print("\nORIGINAL FULL-PERIOD RESULTS")
print(
    "Declining anomalies:",
    (full_tests["difference_pp"] < 0).sum()
)
print(
    "BH-significant declines:",
    full_tests["significant_decline"].sum()
)
print(
    "Mean change:",
    round(full_tests["difference_pp"].mean(), 4)
)

print("\nEQUAL-LENGTH RESULTS")
print("Declining anomalies:", results["declined"].sum())
print(
    "BH-significant declines:",
    results["significant_decline"].sum()
)
print(
    "BH-significant increases:",
    results["significant_increase"].sum()
)
print(
    "Mean change:",
    round(results["difference_pp"].mean(), 4)
)
print(
    "Median change:",
    round(results["difference_pp"].median(), 4)
)

print("\nCONSISTENCY WITH ORIGINAL RESULTS")
print(
    "Anomalies with the same direction of change:",
    comparison["same_direction"].sum(),
    "of 209"
)
print(
    "Significant declines in BOTH approaches:",
    (
        comparison["significant_decline_balanced"] &
        comparison["significant_decline_full"]
    ).sum()
)

print("\nSaved to:", output_file)
