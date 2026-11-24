
# FIN331 Checkpoint 3: Economic category analysis

from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs")

# 1. Load our existing anomaly-level results
summary = pd.read_csv(
    OUTPUT_DIR / "full_sample_summary.csv"
)

tests = pd.read_csv(
    OUTPUT_DIR / "full_sample_tests.csv"
)

# 2. Join descriptive results with significance tests
assert summary["signalname"].is_unique
assert tests["anomaly"].is_unique

df = summary.merge(
    tests[[
        "anomaly", "difference_pp",
        "significant_decline", "significant_increase"
    ]],
    left_on="signalname",
    right_on="anomaly",
    how="inner",
    validate="one_to_one"
)

# 3. Validate that both datasets describe the same 209 anomalies
assert len(df) == 209
assert set(summary["signalname"]) == set(tests["anomaly"])

assert np.allclose(
    df["change_pp"],
    df["difference_pp"]
)

# 4. Summarize each economic category
categories = (
    df.groupby("economic_category")
    .agg(
        n_anomalies=("signalname", "nunique"),
        original_mean_pct=("original_mean_pct", "mean"),
        post_mean_pct=("post_mean_pct", "mean"),
        mean_change_pp=("change_pp", "mean"),
        median_change_pp=("change_pp", "median"),
        n_declined=("declined", "sum"),
        n_significant_declines=("significant_decline", "sum"),
        n_significant_increases=("significant_increase", "sum")
    )
    .reset_index()
)

# 5. Calculate percentages within each category
categories["pct_declined"] = (
    100 * categories["n_declined"]
    / categories["n_anomalies"]
)

categories["pct_significant_declines"] = (
    100 * categories["n_significant_declines"]
    / categories["n_anomalies"]
)

# Flag categories with enough anomalies for more useful comparison
categories["at_least_5_anomalies"] = (
    categories["n_anomalies"] >= 5
)

# 6. Validate that category counts match our overall results
assert len(categories) == 35
assert categories["n_anomalies"].sum() == 209
assert categories["n_declined"].sum() == 181
assert categories["n_significant_declines"].sum() == 30
assert categories["n_significant_increases"].sum() == 0

# 7. Save all 35 categories
categories = categories.sort_values(
    ["n_anomalies", "economic_category"],
    ascending=[False, True]
)

output_file = OUTPUT_DIR / "full_sample_categories.csv"
categories.to_csv(output_file, index=False)

# 8. Display results
print("FULL-SAMPLE ECONOMIC CATEGORY ANALYSIS")
print("Total categories:", len(categories))
print("Total anomalies:", categories["n_anomalies"].sum())

print("\nCATEGORY SIZE DISTRIBUTION")
print(
    "Categories with at least 5 anomalies:",
    categories["at_least_5_anomalies"].sum()
)
print(
    "Categories with fewer than 5 anomalies:",
    (~categories["at_least_5_anomalies"]).sum()
)

columns = [
    "economic_category",
    "n_anomalies",
    "original_mean_pct",
    "post_mean_pct",
    "mean_change_pp",
    "pct_declined",
    "n_significant_declines"
]

print("\nTEN LARGEST CATEGORIES:")
print(
    categories[columns]
    .head(10)
    .round(3)
    .to_string(index=False)
)

# Avoid ranking tiny categories as if their estimates were reliable
larger = categories[
    categories["at_least_5_anomalies"]
].copy()

print("\nFIVE LARGEST AVERAGE DECLINES (CATEGORIES WITH 5+ ANOMALIES):")
print(
    larger.sort_values("mean_change_pp")
    [columns]
    .head(5)
    .round(3)
    .to_string(index=False)
)

print("\nFIVE SMALLEST DECLINES / LARGEST INCREASES (5+ ANOMALIES):")
print(
    larger.sort_values("mean_change_pp", ascending=False)
    [columns]
    .head(5)
    .round(3)
    .to_string(index=False)
)

print("\nSaved to:", output_file)
