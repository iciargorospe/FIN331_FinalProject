# Checkpoint 3 Instructor Audit Response
**Audit:** `audits/04_instructor_audit.md`

**Project:** Did Academic Research Kill the Anomalies?

## B1 - Partially Fixed: Full-Sample Analysis Not on Main / Live Website Still Shows Prototype
**Finding:** Our Checkpoint 3 analysis was available only through PR #6, while the `main` branch and live website still displayed our five-anomaly prototype.

**Actions taken:**
We merged PR #6 into `main`, making our expanded 209-anomaly analysis, statistical tests, panel regressions, robustness checks, results tables, and updated documentation available in the main repository.

We also merged PR #7 to preserve the instructor's Checkpoint 3 audit in the repository.

**Evidence:**
- PR #6: [https://github.com/iciargorospe/FIN331_FinalProject/pull/6](https://github.com/iciargorospe/FIN331_FinalProject/pull/6)
- PR #6 merge commit: `3bce03e9079f4210436fac6e97a5694bee4536f1`
- PR #7: [https://github.com/iciargorospe/FIN331_FinalProject/pull/7](https://github.com/iciargorospe/FIN331_FinalProject/pull/7)

**Remaining work:**
The live website still uses the five-anomaly prototype through `outputs/explorer_data.json`.

Before the final presentation, we will update the website to display our full-sample findings, including the 209 anomalies, economic category comparisons, and regression results. We will also remove the prototype-only labeling and verify that the published site matches the committed outputs.

**Status:** Repository issue fixed; website integration pending.
## B2 - Fixed: Full-Sample Dataset Not Available for Offline Verification

**Finding:** Although our main pipeline was reproducible with access to Open Asset Pricing, the full-sample dataset was not committed. Consequently, someone unable to access the OpenAP data host could not independently rerun the downstream analyses.

**Actions taken:**
We committed a compressed snapshot of our 209-anomaly analysis dataset to `outputs/full_sample_analysis.csv.gz`.

The snapshot comes from the October 2026 Open Asset Pricing release (`202610`) and contains 135,466 anomaly-month observations.

We also created `verify_offline.py`, a separate verification script that:

1. Decompresses the committed dataset into a temporary directory.
2. Validates its observation counts, anomaly count, and unique anomaly-month keys.
3. Runs the five downstream full-sample analysis scripts.
4. Compares the regenerated output tables against our committed results.
5. Independently calculates the original-sample mean for the Accruals anomaly using a basic Python loop.

**Verification results:**
All five downstream analysis files reproduced successfully:

- `full_sample_summary.csv`: 209 rows
- `full_sample_tests.csv`: 209 rows
- `full_sample_regression.csv`: 6 rows
- `full_sample_categories.csv`: 35 rows
- `full_sample_robustness.csv`: 209 rows

The independent hand check for Accruals used 360 original-sample monthly observations and obtained an average monthly return of 0.686739%, matching the summary results.

The verification script does not require downloading data from Open Asset Pricing. Python dependencies must still be installed.

**Evidence:**
- Compressed dataset commit: `5c10a986643ec1759007bff1852b84b365275636`
- Offline verification script commit: `bf0a4c121e4b557647ea3fbc1ddfab2ebb953dec`
- Verification command: `python verify_offline.py`

**Status:** Fixed.

## Remaining Work Before Final Presentation
We will continue developing the final project by:

- Updating and validating the live website using the full-sample.
- Evaluating whether there are reliable trading-difficulty measures we can access for our third research question.
- Completing additional statistical robustness or trading-cost sensitivity analyses where appropriate.
- Updating the project documentation to reflect the final methodology and results.
- Requesting a final independent audit before presentation day.

We will continue distinguishing statistically significant associations from direct cause-and-effect and documenting limitations transparently.
