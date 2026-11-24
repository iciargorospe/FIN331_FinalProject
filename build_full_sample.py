
# FIN331 Checkpoint 3: Build the full-sample analysis dataset

from pathlib import Path
import numpy as np
import pandas as pd
import openassetpricing as oap

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

DATA_RELEASE = 202610
MIN_MONTHS = 24

openap = oap.OpenAP(DATA_RELEASE)

# Step 1: Download metadata and select Predictor signals
docs = openap.dl_signal_doc("pandas")

assert docs["Acronym"].is_unique

metadata = docs.loc[
    docs["Cat.Signal"] == "Predictor",
    [
        "Acronym", "Year", "SampleStartYear",
        "SampleEndYear", "Cat.Economic", "Cat.Data"
    ]
].rename(columns={
    "Acronym": "signalname",
    "Year": "publication_year",
    "SampleStartYear": "sample_start_year",
    "SampleEndYear": "sample_end_year",
    "Cat.Economic": "economic_category",
    "Cat.Data": "data_category"
}).copy()

for col in ["publication_year", "sample_start_year", "sample_end_year"]:
    metadata[col] = pd.to_numeric(metadata[col], errors="raise")

assert metadata.notna().all().all()
assert (
    (metadata["sample_start_year"] <= metadata["sample_end_year"]) &
    (metadata["sample_end_year"] < metadata["publication_year"])
).all()

names = sorted(metadata["signalname"].tolist())
print(f"Selected {len(names)} Predictor signals.")

# Step 2: Download their long-short monthly returns
batches = []

for i in range(0, len(names), 25):
    batch_names = names[i:i + 25]
    batch = openap.dl_port("op", "pandas", batch_names)

    batches.append(
        batch.loc[
            batch["port"] == "LS",
            ["signalname", "date", "ret"]
        ].copy()
    )

returns = pd.concat(batches, ignore_index=True)

assert set(returns["signalname"]) == set(names)

# Step 3: Merge returns with research metadata
data = returns.merge(
    metadata,
    on="signalname",
    how="left",
    validate="m:1",
    indicator=True
)

assert (data["_merge"] == "both").all()
data = data.drop(columns="_merge")

data["date"] = pd.to_datetime(data["date"], errors="raise")
data["ret"] = pd.to_numeric(data["ret"], errors="raise")
data["month"] = data["date"].dt.to_period("M").astype(str)
data["observation_year"] = data["date"].dt.year

assert data["date"].notna().all()
assert np.isfinite(data["ret"]).all()
assert not data.duplicated(["signalname", "month"]).any()

# Step 4: Classify each monthly observation
year = data["observation_year"]

conditions = [
    year < data["sample_start_year"],
    year.between(data["sample_start_year"], data["sample_end_year"]),
    (year > data["sample_end_year"]) &
    (year < data["publication_year"]),
    year == data["publication_year"],
    year > data["publication_year"]
]

labels = [
    "Before Original Sample",
    "Original Sample",
    "Pre-Publication Gap",
    "Publication Year",
    "Post-Publication"
]

data["period"] = np.select(
    conditions, labels, default="Unclassified"
)

assert (data["period"] != "Unclassified").all()

# Step 5: Apply our prespecified 24-month eligibility rule
counts = pd.crosstab(
    data["signalname"], data["period"]
).reindex(
    index=names,
    columns=["Original Sample", "Post-Publication"],
    fill_value=0
)

eligible = counts.index[
    (counts["Original Sample"] >= MIN_MONTHS) &
    (counts["Post-Publication"] >= MIN_MONTHS)
].tolist()

excluded = sorted(set(names) - set(eligible))

comparison_periods = [
    "Original Sample",
    "Pre-Publication Gap",
    "Post-Publication"
]

analysis = data.loc[
    data["signalname"].isin(eligible) &
    data["period"].isin(comparison_periods)
].copy()

# Step 6: Create regression indicators
analysis["post_sample"] = (
    analysis["period"] != "Original Sample"
).astype(int)

analysis["post_publication"] = (
    analysis["period"] == "Post-Publication"
).astype(int)

# Step 7: Save the completed dataset
columns = [
    "signalname", "month", "ret", "publication_year",
    "period", "post_sample", "post_publication",
    "economic_category", "data_category",
    "sample_start_year", "sample_end_year"
]

analysis = analysis[columns].sort_values(
    ["signalname", "month"]
).reset_index(drop=True)

assert analysis["signalname"].nunique() == len(eligible)
assert not analysis.duplicated(["signalname", "month"]).any()
assert np.isfinite(analysis["ret"]).all()

# Verify we recreated our independently explored sample
assert len(eligible) == 209
assert len(analysis) == 135466
assert excluded == ["Activism1", "Activism2", "PatentsRD"]

output_file = OUTPUT_DIR / "full_sample_analysis.csv"
analysis.to_csv(output_file, index=False)

print("\nFULL-SAMPLE DATASET COMPLETE!")
print("Predictors downloaded:", len(names))
print("Eligible anomalies:", len(eligible))
print("Analysis observations:", len(analysis))
print("Excluded anomalies:", excluded)

print("\nObservations by period:")
print(analysis["period"].value_counts())

print("\nSaved to:", output_file)
