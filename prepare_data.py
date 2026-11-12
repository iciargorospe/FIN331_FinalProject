"""Prepare the prototype website data from checkpoint1_sample.csv."""

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "outputs" / "checkpoint1_sample.csv"
OUTPUT_FILE = ROOT / "outputs" / "explorer_data.json"

PERIODS = {
    "original_sample": "Original research sample",
    "gap": "Pre-publication gap",
    "post_publication": "Post-publication",
}

ANOMALY_LABELS = {
    "Accruals": "Accruals",
    "AssetGrowth": "Asset Growth",
    "BM": "Book-to-Market (BM)",
    "IndIPO": "Initial Public Offerings (IndIPO)",
    "Mom12m": "12-Month Momentum",
}

ANOMALY_DESCRIPTIONS = {
    "Accruals": "Ranks firms by accruals, an accounting measure based on changes in balance-sheet items relative to average assets.",
    "AssetGrowth": "Ranks firms by the annual growth rate of their total assets.",
    "BM": "Ranks firms by book-to-market: accounting book equity relative to market equity.",
    "IndIPO": "Flags firms that went public 6 to 36 months earlier; it is a firm-level IPO signal, not an industry-wide measure.",
    "Mom12m": "Ranks stocks by their return from months t−12 through t−1, the prior 12 months.",
}


def assign_period(year, sample_start, sample_end, publication_year):
    if year < sample_start or year == publication_year:
        return None
    if sample_start <= year <= sample_end:
        return "original_sample"
    if sample_end < year < publication_year:
        return "gap"
    if year > publication_year:
        return "post_publication"
    return None


def main():
    observations = []
    metadata = {}
    seen = set()

    with INPUT_FILE.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {
            "signalname", "month", "ret", "publication_year",
            "sample_start_year", "sample_end_year", "economic_category",
            "data_category",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input CSV is missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            signal = row["signalname"]
            month = row["month"]
            key = (signal, month)
            if key in seen:
                raise ValueError(f"Duplicate anomaly-month observation: {signal}, {month}")
            seen.add(key)

            years = {
                "publication_year": int(row["publication_year"]),
                "sample_start_year": int(row["sample_start_year"]),
                "sample_end_year": int(row["sample_end_year"]),
            }
            
# Verify that the research sample dates make sense
if not (
    years["sample_start_year"]
    <= years["sample_end_year"]
    < years["publication_year"]
):
    raise ValueError(
        f"Invalid research sample or publication years for {signal}"
    )
  
            current_metadata = {
                **years,
                "economic_category": row["economic_category"],
                "data_category": row["data_category"],
            }
            if signal in metadata and metadata[signal] != current_metadata:
                raise ValueError(f"Inconsistent metadata for {signal}")
            metadata[signal] = current_metadata

            value = float(row["ret"])
            if not math.isfinite(value):
                raise ValueError(f"Non-finite return for {signal}, {month}")

            period = assign_period(
                int(month[:4]),
                years["sample_start_year"],
                years["sample_end_year"],
                years["publication_year"],
            )
            if period is not None:
                observations.append({
                    "signal": signal,
                    "month": month,
                    "year": int(month[:4]),
                    "return_pct": value,
                    "period": period,
                })

    if set(metadata) != set(ANOMALY_LABELS):
        raise ValueError("Expected the five prototype anomalies listed in ANOMALY_LABELS")

    grouped = defaultdict(list)
    annual = defaultdict(list)
    for observation in observations:
        key = (observation["signal"], observation["period"])
        grouped[key].append(observation)
        annual[(*key, observation["year"])].append(observation["return_pct"])

    anomalies = []
    for signal in sorted(metadata, key=lambda item: ANOMALY_LABELS[item]):
        details = metadata[signal]
        summary = {}
        for period, label in PERIODS.items():
            rows = grouped[(signal, period)]
            values = [row["return_pct"] for row in rows]
            summary[period] = {
                "label": label,
                "observations": len(values),
                "mean_monthly_pct": statistics.mean(values) if values else None,
                "median_monthly_pct": statistics.median(values) if values else None,
                "std_monthly_pct": statistics.stdev(values) if len(values) > 1 else None,
                "first_month": min((row["month"] for row in rows), default=None),
                "last_month": max((row["month"] for row in rows), default=None),
            }

        annual_means = [
            {
                "year": year,
                "period": period,
                "mean_monthly_pct": statistics.mean(values),
                "observations": len(values),
            }
            for (name, period, year), values in sorted(annual.items())
            if name == signal
        ]
        anomalies.append({
            "signal": signal,
            "label": ANOMALY_LABELS[signal],
            "description": ANOMALY_DESCRIPTIONS[signal],
            **details,
            "summary": summary,
            "annual_means": annual_means,
        })

    payload = {
        "title": "Did Academic Research Kill the Anomalies?",
        "source_file": "checkpoint1_sample.csv",
        "data_release": "Open Asset Pricing, October 2026 (202610)",
        "return_unit": "percent per month",
        "periods": PERIODS,
        "anomalies": anomalies,
    }
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE.relative_to(ROOT)} for {len(anomalies)} anomalies.")
    print(f"Included {len(observations):,} observations in the three comparison periods.")


if __name__ == "__main__":
    main()
