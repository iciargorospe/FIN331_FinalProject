
# FIN331 Checkpoint 3: Full-sample descriptive results

from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("outputs")

# Step 1: Load the 209-anomaly analysis dataset
df = pd.read_csv(OUTPUT_DIR / "full_sample_analysis.csv")

# Step 2: Calculate average monthly returns for each
# anomaly in each of our three research periods
period_stats = (
    df.groupby(["signalname", "period"])
    .agg(
        observations=("ret", "size"),
        mean_monthly_pct=("ret", "mean")
    )
    .reset_index()
)

# Step 3: Keep each anomaly's research information
metadata = (
    df[[
        "signalname", "publication_year",
        "economic_category", "data_category"
    ]]
    .drop_duplicates("signalname")
    .set_index("signalname")
)

assert metadata.index.is_unique

summary = metadata.copy()

# Step 4: Add average returns and observation counts
periods = {
    "Original Sample": "original",
    "Pre-Publication Gap": "gap",
    "Post-Publication": "post"
}

for period, label in periods.items():
    subset = period_stats.loc[
        period_stats["period"] == period
    ].set_index("signalname")

    summary[f"{label}_mean_pct"] = subset["mean_monthly_pct"]
    summary[f"{label}_months"] = subset["observations"]

# Step 5: Measure the change after publication
summary["change_pp"] = (
    summary["post_mean_pct"] - summary["original_mean_pct"]
)

summary["declined"] = summary["change_pp"] < 0

# Step 6: Validate our results
assert len(summary) == 209
assert (summary["original_months"] >= 24).all()
assert (summary["post_months"] >= 24).all()
assert summary["change_pp"].notna().all()

# Step 7: Save the complete anomaly-level results
summary = summary.reset_index().sort_values("signalname")

output_file = OUTPUT_DIR / "full_sample_summary.csv"
summary.to_csv(output_file, index=False)

# Step 8: Display our first research findings
print("FULL-SAMPLE DESCRIPTIVE RESULTS")
print("Anomalies analyzed:", len(summary))

print("\nAVERAGE MONTHLY RETURNS (EQUAL-WEIGHTED ACROSS ANOMALIES)")
print(f"Original sample: {summary['original_mean_pct'].mean():.4f}%")
print(f"Pre-publication gap: {summary['gap_mean_pct'].mean():.4f}%")
print(f"Post-publication: {summary['post_mean_pct'].mean():.4f}%")

print("\nCHANGE IN PROFITABILITY")
print(f"Average change: {summary['change_pp'].mean():.4f} percentage points")
print(f"Median change: {summary['change_pp'].median():.4f} percentage points")

n_declined = summary["declined"].sum()

print(f"Anomalies with declining returns: {n_declined} of {len(summary)}")
print(f"Percentage declining: {100 * n_declined / len(summary):.1f}%")

print("\nANOMALIES WITH PRE-PUBLICATION GAP DATA:")
print(summary["gap_mean_pct"].notna().sum())

print("\nFIRST FIVE ANOMALY RESULTS:")
print(summary[[
    "signalname", "original_mean_pct",
    "gap_mean_pct", "post_mean_pct", "change_pp"
]].head().round(4).to_string(index=False))

print("\nSaved to:", output_file)
