"""Independent spot-checks for FIN331 final project (exploratory, not yet committed).

Run from the repository root after ``python run_all.py`` or ``python verify_offline.py``.
Uses separate direct arithmetic to check selected entries; not a source-data audit.
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
RAW = OUT / "full_sample_analysis.csv"
if not RAW.exists():
    RAW = OUT / "full_sample_analysis.csv.gz"
assert RAW.exists(), "Missing full_sample_analysis.csv or .csv.gz in outputs/"

def close(a, b, description, atol=1e-9, rtol=1e-8):
    assert math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol), (
        f"{description}: independently calculated {a}, saved output {b}"
    )

def one_row(frame, key_col, key):
    selected = frame.loc[frame[key_col] == key]
    assert len(selected) == 1, (key_col, key, len(selected))
    return selected.iloc[0]

def normal_two_sided(z):
    # Normal upper-tail probability computed via the error function,
    # separately from the project's scipy.stats.norm implementation.
    return math.erfc(abs(float(z)) / math.sqrt(2.0))

# 1. Independently inspect every period assignment and regression indicator.
raw = pd.read_csv(RAW)
period_counts = {"Original Sample": 0, "Pre-Publication Gap": 0, "Post-Publication": 0}
assert len(raw) == 135466
assert raw["signalname"].nunique() == 209
assert not raw.duplicated(["signalname", "month"]).any()
for row in raw.itertuples(index=False):
    year = int(str(row.month)[:4])
    if int(row.sample_start_year) <= year <= int(row.sample_end_year):
        period, sample_flag, publication_flag = "Original Sample", 0, 0
    elif int(row.sample_end_year) < year < int(row.publication_year):
        period, sample_flag, publication_flag = "Pre-Publication Gap", 1, 0
    elif year > int(row.publication_year):
        period, sample_flag, publication_flag = "Post-Publication", 1, 1
    else:
        raise AssertionError(f"Unexpected included year for {row.signalname} {row.month}")
    assert row.period == period, (row.signalname, row.month, row.period, period)
    assert int(row.post_sample) == sample_flag
    assert int(row.post_publication) == publication_flag
    period_counts[period] += 1
assert period_counts == {
    "Original Sample": 73796,
    "Pre-Publication Gap": 8952,
    "Post-Publication": 52718,
}
print("PASS 1: Raw sample keys, 135,466 period labels and regression indicators")

summary = pd.read_csv(OUT / "full_sample_summary.csv")
tests = pd.read_csv(OUT / "full_sample_tests.csv")
categories = pd.read_csv(OUT / "full_sample_categories.csv")
robust = pd.read_csv(OUT / "full_sample_robustness.csv")
economic = pd.read_csv(OUT / "full_sample_economic.csv")
regressions = pd.read_csv(OUT / "full_sample_regression.csv")
winsor = pd.read_csv(OUT / "full_sample_winsorized_regression.csv")
twoway = pd.read_csv(OUT / "full_sample_two_way_clustering.csv")
assert len(summary) == len(tests) == len(robust) == len(economic) == 209

# 2. Manual arithmetic for a familiar anomaly, BM, straight from raw months.
by_period = defaultdict(list)
for row in raw.loc[raw["signalname"] == "BM"].itertuples(index=False):
    by_period[row.period].append(float(row.ret))
bm_summary = one_row(summary, "signalname", "BM")
original = sum(by_period["Original Sample"]) / len(by_period["Original Sample"])
post = sum(by_period["Post-Publication"]) / len(by_period["Post-Publication"])
close(original, bm_summary.original_mean_pct, "BM original mean")
close(post, bm_summary.post_mean_pct, "BM post mean")
close(post-original, bm_summary.change_pp, "BM post-original change")
assert len(by_period["Original Sample"]) == int(bm_summary.original_months)
assert len(by_period["Post-Publication"]) == int(bm_summary.post_months)
print(f"PASS 2: BM means from raw rows; original {original:.6f}%, post {post:.6f}%")

# 3. Independent hand implementation of the lag-12 Bartlett HAC standard
#    error for an intercept-only regression, plus the two-sided z probability.
def manual_hac_mean_se(values, lag=12):
    x = np.asarray(values, dtype=float)
    n = len(x)
    mean = sum(float(t) for t in x) / n
    e = x - mean
    variance_numerator = float(np.dot(e, e))
    for l in range(1, min(lag, n-1)+1):
        variance_numerator += 2.0 * (1.0 - l / (lag+1.0)) * float(np.dot(e[l:], e[:-l]))
    return mean, math.sqrt(variance_numerator / (n*n))

acc = raw.loc[raw["signalname"] == "Accruals"].sort_values("month")
orig_ret = acc.loc[acc["period"] == "Original Sample", "ret"].to_numpy()
post_ret = acc.loc[acc["period"] == "Post-Publication", "ret"].to_numpy()
m_orig, se_orig = manual_hac_mean_se(orig_ret)
m_post, se_post = manual_hac_mean_se(post_ret)
manual_difference = m_post - m_orig
manual_se = math.hypot(se_orig, se_post)
manual_p = normal_two_sided(manual_difference/manual_se)
acc_test = one_row(tests, "anomaly", "Accruals")
close(manual_difference, acc_test.difference_pp, "Accruals difference")
close(manual_se, acc_test.standard_error, "Accruals independent HAC SE", atol=1e-7)
close(manual_p, acc_test.p_value, "Accruals independent p-value", atol=1e-8)
print(f"PASS 3: Accruals independent lag-12 HAC SE {manual_se:.6f}, p={manual_p:.6g}")

# 4. Independent Benjamini-Hochberg adjustment on all 209 saved raw p-values.
pvals = sorted((float(row.p_value), str(row.anomaly)) for row in tests.itertuples(index=False))
m = len(pvals)
bh = {}
running_min = 1.0
for i in range(m-1, -1, -1):
    p, anomaly = pvals[i]
    running_min = min(running_min, p * m / (i+1), 1.0)
    bh[anomaly] = running_min
for row in tests.itertuples(index=False):
    close(bh[row.anomaly], row.adjusted_p_value, f"BH adjusted p for {row.anomaly}", atol=1e-8)
assert sum(q < 0.05 for q in bh.values()) == 30
print("PASS 4: Independent Benjamini-Hochberg correction, 30 significant anomalies")

# 5. Independently aggregate one category without using pandas groupby.
momentum = [r for r in summary.itertuples(index=False) if r.economic_category == "momentum"]
mom = one_row(categories, "economic_category", "momentum")
assert len(momentum) == int(mom.n_anomalies) == 11
mom_change = sum(float(r.change_pp) for r in momentum) / len(momentum)
mom_declines = sum(float(r.change_pp) < 0 for r in momentum)
close(mom_change, mom.mean_change_pp, "Momentum mean change")
assert mom_declines == int(mom.n_declined)
close(100*mom_declines/len(momentum), mom.pct_declined, "Momentum percent declined")
print(f"PASS 5: Momentum category, {len(momentum)} anomalies, mean change {mom_change:.6f} pp")

# 6. Equal-window calculation using direct date sorting, not robustness code.
original_rows = sorted((str(r.month), float(r.ret)) for r in acc.itertuples(index=False) if r.period == "Original Sample")
post_rows = sorted((str(r.month), float(r.ret)) for r in acc.itertuples(index=False) if r.period == "Post-Publication")
window = min(len(original_rows), len(post_rows))
original_equal = sum(v for _, v in original_rows[-window:]) / window
post_equal = sum(v for _, v in post_rows[:window]) / window
acc_robust = one_row(robust, "anomaly", "Accruals")
assert window == int(acc_robust.months_per_period)
close(original_equal, acc_robust.original_mean, "Accruals equal-length original mean")
close(post_equal, acc_robust.post_mean, "Accruals equal-length post mean")
close(post_equal-original_equal, acc_robust.difference_pp, "Accruals equal-length change")
print(f"PASS 6: Accruals equal-length comparison, {window} months each")

# 7. Independent cost deductions and positive-net-return counts.
by_signal = {r.signalname: r for r in economic.itertuples(index=False)}
for cost_bps in (0,25,50):
    deduction_pct = cost_bps/100.0
    count_positive = 0
    for r in summary.itertuples(index=False):
        expected = float(r.post_mean_pct)-deduction_pct
        saved = by_signal[r.signalname]
        close(expected, getattr(saved, f"post_net_{cost_bps}bps_pct"), f"{r.signalname} {cost_bps}bps net")
        assert (expected>0) == bool(getattr(saved, f"post_profitable_{cost_bps}bps"))
        count_positive += expected>0
    assert count_positive == {0:174,25:101,50:46}[cost_bps]
print("PASS 7: Independent hypothetical-cost deductions; positive counts 174/101/46")

# 8. Check winsorization thresholds and the number of capped observations.
vals = raw["ret"].to_numpy(dtype=float)
low, high = np.percentile(vals, (1,99))
w = winsor.iloc[0]
close(low, w.lower_cutoff_pct, "Winsor lower cutoff")
close(high, w.upper_cutoff_pct, "Winsor upper cutoff")
assert int(np.count_nonzero(vals<low)) == int(w.observations_capped_lower) == 1355
assert int(np.count_nonzero(vals>high)) == int(w.observations_capped_upper) == 1355
print(f"PASS 8: Winsorized 1%/99% cutoffs ({low:.4f}%, {high:.4f}%) and tail counts")

# 9. Regression arithmetic and p-values recalculated via erfc, not scipy norm.
r = regressions.loc[regressions["model"] == "With Month FE"].set_index("variable")
close(r.loc["post_sample", "coefficient"]+r.loc["post_publication", "coefficient"],
      r.loc["total_post_vs_original", "coefficient"], "Panel combined coefficient")
for variable in ("post_sample", "post_publication", "total_post_vs_original"):
    x = r.loc[variable]
    close(normal_two_sided(x.coefficient/x.standard_error), x.p_value, f"Regression p {variable}")
    t = one_row(twoway, "variable", variable)
    close(t.coefficient, x.coefficient, f"2-way coefficient {variable}")
    close(normal_two_sided(t.coefficient/t.se_two_way), t.p_two_way, f"2-way p {variable}")
print("PASS 9: Regression totals, original p-values and two-way-clustered p-values")
print("\nSUCCESS: ALL NINE INDEPENDENT SPOT-CHECKS PASSED!")
print("Note: These are independent arithmetic spot-checks, not a source-data audit or")
print("an independent re-estimation of all panel coefficients and covariance matrices.")
