"""Build website JSON exclusively from saved research output files."""

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
OUTPUT_FILE = OUTPUTS / "website_data.json"


def read_csv(name):
    with (OUTPUTS / name).open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def number(row, column):
    value = row[column]
    return None if value in ("", "nan", "None") else float(value)


def integer(row, column):
    value = row[column]
    return None if value in ("", "nan", "None") else int(float(value))


def boolean(row, column):
    return str(row[column]).strip().lower() in ("true", "1", "yes")


def mean(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


def main():
    summary = read_csv("full_sample_summary.csv")
    tests = read_csv("full_sample_tests.csv")
    regressions = read_csv("full_sample_regression.csv")
    categories = read_csv("full_sample_categories.csv")
    robustness = read_csv("full_sample_robustness.csv")
    economic = read_csv("full_sample_economic.csv")
    winsorized = read_csv("full_sample_winsorized_regression.csv")
    two_way = read_csv("full_sample_two_way_clustering.csv")

    if len(summary) != 209:
        raise ValueError(f"Expected 209 anomalies in full_sample_summary.csv, found {len(summary)}")

    annual = defaultdict(list)
    import gzip
    analysis_path = OUTPUTS / "full_sample_analysis.csv.gz"
    with gzip.open(analysis_path, "rt", encoding="utf-8") as decompressed:
        reader = csv.DictReader(decompressed)
        for row in reader:
            period = row["period"]
            if period not in ("Original Sample", "Pre-Publication Gap", "Post-Publication"):
                continue
            year = int(row["month"][:4])
            annual[(row["signalname"], period, year)].append(float(row["ret"]))

    anomalies = []
    test_by_signal = {row["anomaly"]: row for row in tests}
    robust_by_signal = {row["anomaly"]: row for row in robustness}
    economic_by_signal = {row["signalname"]: row for row in economic}

    for row in summary:
        signal = row["signalname"]
        test = test_by_signal[signal]
        equal = robust_by_signal[signal]
        cost = economic_by_signal[signal]
        period_summary = {}
        for period, mean_col, months_col in (
            ("original_sample", "original_mean_pct", "original_months"),
            ("gap", "gap_mean_pct", "gap_months"),
            ("post_publication", "post_mean_pct", "post_months"),
        ):
            period_summary[period] = {
                "mean_monthly_pct": number(row, mean_col),
                "observations": integer(row, months_col),
            }

        annual_means = []
        for (name, period, year), values in sorted(annual.items()):
            if name == signal:
                period_key = {
                    "Original Sample": "original_sample",
                    "Pre-Publication Gap": "gap",
                    "Post-Publication": "post_publication",
                }[period]
                annual_means.append({
                    "year": year,
                    "period": period_key,
                    "mean_monthly_pct": mean(values),
                    "observations": len(values),
                })

        anomalies.append({
            "signal": signal,
            "label": signal,
            "publication_year": integer(row, "publication_year"),
            "economic_category": row["economic_category"],
            "data_category": row["data_category"],
            "change_pp": number(row, "change_pp"),
            "declined": boolean(row, "declined"),
            "summary": period_summary,
            "annual_means": annual_means,
            "test": {
                "original_months": integer(test, "original_months"),
                "post_months": integer(test, "post_months"),
                "original_mean": number(test, "original_mean"),
                "post_mean": number(test, "post_mean"),
                "difference_pp": number(test, "difference_pp"),
                "standard_error": number(test, "standard_error"),
                "p_value": number(test, "p_value"),
                "adjusted_p_value": number(test, "adjusted_p_value"),
                "significant_after_BH": boolean(test, "significant_after_BH"),
                "significant_decline": boolean(test, "significant_decline"),
                "significant_increase": boolean(test, "significant_increase"),
            },
            "equal_length": {
                "months_per_period": integer(equal, "months_per_period"),
                "original_mean": number(equal, "original_mean"),
                "post_mean": number(equal, "post_mean"),
                "difference_pp": number(equal, "difference_pp"),
                "p_value": number(equal, "p_value"),
                "adjusted_p_value": number(equal, "adjusted_p_value"),
                "declined": boolean(equal, "declined"),
                "significant_decline": boolean(equal, "significant_decline"),
                "significant_increase": boolean(equal, "significant_increase"),
            },
            "hypothetical_costs": {
                "original_mean_pct": number(cost, "original_mean_pct"),
                "post_mean_pct": number(cost, "post_mean_pct"),
                "net_0bps_pct": number(cost, "post_net_0bps_pct"),
                "net_25bps_pct": number(cost, "post_net_25bps_pct"),
                "net_50bps_pct": number(cost, "post_net_50bps_pct"),
                "positive_0bps": boolean(cost, "post_profitable_0bps"),
                "positive_25bps": boolean(cost, "post_profitable_25bps"),
                "positive_50bps": boolean(cost, "post_profitable_50bps"),
            },
        })
    original_avg = mean([number(row, "original_mean_pct") for row in summary])
    gap_avg = mean([number(row, "gap_mean_pct") for row in summary])
    post_avg = mean([number(row, "post_mean_pct") for row in summary])
    declined_count = sum(boolean(row, "declined") for row in summary)
    raw_significant = sum(number(row, "p_value") < 0.05 for row in tests)
    bh_significant = sum(boolean(row, "significant_after_BH") for row in tests)
    bh_declines = sum(boolean(row, "significant_decline") for row in tests)

    regression_rows = []
    for model in ("Without Month FE", "With Month FE"):
        items = {row["variable"]: row for row in regressions if row["model"] == model}
        regression_rows.append({
            "model": model,
            "post_sample": {
                "coefficient": number(items["post_sample"], "coefficient"),
                "p_value": number(items["post_sample"], "p_value"),
            },
            "post_publication": {
                "coefficient": number(items["post_publication"], "coefficient"),
                "p_value": number(items["post_publication"], "p_value"),
            },
            "total": {
                "coefficient": number(items["total_post_vs_original"], "coefficient"),
                "p_value": number(items["total_post_vs_original"], "p_value"),
            },
        })

    category_rows = []
    for row in categories:
        category_rows.append({
            "economic_category": row["economic_category"],
            "n_anomalies": integer(row, "n_anomalies"),
            "original_mean_pct": number(row, "original_mean_pct"),
            "post_mean_pct": number(row, "post_mean_pct"),
            "mean_change_pp": number(row, "mean_change_pp"),
            "n_declined": integer(row, "n_declined"),
            "pct_declined": number(row, "pct_declined"),
            "n_significant_declines": integer(row, "n_significant_declines"),
            "at_least_5_anomalies": boolean(row, "at_least_5_anomalies"),
        })

    equal_declined = sum(boolean(row, "declined") for row in robustness)
    equal_bh = sum(boolean(row, "significant_decline") for row in robustness)
    equal_avg_change = mean([number(row, "difference_pp") for row in robustness])

    costs = []
    for bps, col, positive_col in (
        (0, "post_net_0bps_pct", "post_profitable_0bps"),
        (25, "post_net_25bps_pct", "post_profitable_25bps"),
        (50, "post_net_50bps_pct", "post_profitable_50bps"),
    ):
        costs.append({
            "bps": bps,
            "average_net_pct": mean([number(row, col) for row in economic]),
            "positive_count": sum(boolean(row, positive_col) for row in economic),
        })

    wins_rows = []
    cutoffs = {}
    for row in winsorized:
        if row["model"] == "With Month FE":
            wins_rows.append({
                "variable": row["variable"],
                "coefficient_original": number(row, "coefficient_original"),
                "p_value_original": number(row, "p_value_original"),
                "coefficient_winsorized": number(row, "coefficient_winsorized"),
                "p_value_winsorized": number(row, "p_value_winsorized"),
            })
        cutoffs["lower_cutoff_pct"] = number(row, "lower_cutoff_pct")
        cutoffs["upper_cutoff_pct"] = number(row, "upper_cutoff_pct")
        cutoffs["observations_capped_lower"] = integer(row, "observations_capped_lower")
        cutoffs["observations_capped_upper"] = integer(row, "observations_capped_upper")

    two_way_rows = [{
        "variable": row["variable"],
        "coefficient": number(row, "coefficient"),
        "p_month_only": number(row, "p_month_only"),
        "p_two_way": number(row, "p_two_way"),
    } for row in two_way]

    anomaly_month_observations = 0
    import gzip
    with gzip.open(OUTPUTS / "full_sample_analysis.csv.gz", "rt", encoding="utf-8") as decompressed:
        reader = csv.DictReader(decompressed)
        anomaly_month_observations = sum(1 for row in reader if row["period"] in (
            "Original Sample", "Pre-Publication Gap", "Post-Publication",
        ))

    payload = {
        "title": "Did Academic Research Kill the Anomalies?",
        "data_release": "Open Asset Pricing, October 2026 (202610)",
        "eligible_anomalies": len(anomalies),
        "anomaly_month_observations": anomaly_month_observations,
        "period_counts": {
            "original_sample": sum(integer(row, "original_months") for row in summary),
            "gap": sum(integer(row, "gap_months") for row in summary),
            "post_publication": sum(integer(row, "post_months") for row in summary),
        },
        "descriptive": {
            "original_average_pct": original_avg,
            "gap_average_pct": gap_avg,
            "post_average_pct": post_avg,
            "average_change_pp": post_avg - original_avg,
            "declined_count": declined_count,
        },
        "individual_tests": {
            "raw_significant": raw_significant,
            "bh_significant": bh_significant,
            "bh_declines": bh_declines,
        },
        "regressions": regression_rows,
        "categories": category_rows,
        "equal_length": {
            "declined_count": equal_declined,
            "bh_significant_declines": equal_bh,
            "average_change_pp": equal_avg_change,
        },
        "hypothetical_costs": costs,
        "winsorized": wins_rows,
        "winsorized_cutoffs": cutoffs,
        "two_way_clustering": two_way_rows,
        "anomalies": anomalies,
    }
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE.relative_to(ROOT)} for {len(anomalies)} anomalies.")


if __name__ == "__main__":
    main()
