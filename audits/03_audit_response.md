# Instructor Audit Response

**Audit:** `audits/02_instructor_audit.md`

### A1 - Fixed: (checkpoint 2 work wasn't merged into main)
We merged PR #2 (Checkpoint 2 + Research Proposal) and PR #3 (Instructor Audit) into `main`. We also changed our GitHub Pages deployment source from the `website` branch to `main` (root).

Then, we verified that the project files are available on `main` and confirmed that our live dashboard still works, including the Preliminary Results and Explore sections.

**Evidence:** [PR #2](https://github.com/iciargorospe/FIN331_FinalProject/pull/2), [PR #3](https://github.com/iciargorospe/FIN331_FinalProject/pull/3), and our [live dashboard](https://iciargorospe.github.io/FIN331_FinalProject/).

### A2 - Fixed for our five-anomaly prototype: (pre/post means didn't account for calendar-time trends)
We implemented panel regressions with post-sample and post-publication indicators, anomaly fixed effects, and standard errors clustered by calendar month. We ran two models: one without calendar-month fixed effects and another including them, as recommended in the instructor audit.

Without calendar-month fixed effects, the estimated total change from the original research sample to post-publication was -0.5531 percentage points per month (p = 0.0010). With calendar-month fixed effects, the estimated change was -0.6967 percentage points (p = 0.0812).

The additional post-publication coefficient was +0.3787 percentage points per month (p = 0.2133) without calendar-month fixed effects and +0.2807 percentage points (p = 0.5471) with calendar-month fixed effects. Neither was statistically significant at the 5% level. This suggests that some of the decline in profitability may have occurred before publication, although our results do not establish causation.

We added the regressions to our reproducible pipeline and saved the results in `outputs/prototype_regression_results.csv`.

**Evidence:** [Regression analysis commit](https://github.com/iciargorospe/FIN331_FinalProject/commit/4f3bcc4591443de6899fbe6c50ca3fbbe90d2897), [pipeline integration commit](https://github.com/iciargorospe/FIN331_FinalProject/commit/5bdb33d4180030f20612576f0d01e9562c3443b0), and `outputs/prototype_regression_results.csv` on `audit-fixes`.

**Remaining limitation:** These regressions currently only cover the five prototype anomalies. We plan to repeat the analysis using the broader anomaly dataset.

### A3 - Fixed for our five-anomaly prototype: (statistical testing and multiple-testing plan)
Before running our full-sample analysis, we documented our statistical testing methods in `specs_tried.md`, following the instructor audit's recommendations.

For individual anomalies, we implemented tests comparing original-sample and post-publication average monthly returns using Newey-West standard errors with a 12-month lag. We also applied the Benjamini-Hochberg procedure to control the false discovery rate at 5%.

In our five-anomaly prototype, two anomalies (Accruals and AssetGrowth) experienced statistically significant declines after the multiple-testing adjustment. The other three anomalies had lower average post-publication returns, but their declines were not statistically significant at the 5% level.

We also calculated changes in profitability in percentage points and relative percentages, along with a trading-cost sensitivity analysis using hypothetical monthly costs of 0, 25, and 50 basis points. At our baseline 25-basis-point assumption, Accruals had a negative average post-publication net return.

We integrated these analyses into our pipeline and saved the results in `outputs/prototype_anomaly_tests.csv` and `outputs/prototype_economic_results.csv`.

**Evidence:** Updated `specs_tried.md`, [anomaly tests commit](https://github.com/iciargorospe/FIN331_FinalProject/commit/e2c4bd379e6486288404f0f213e86b7c5fcfbf9e), [economic analysis commit](https://github.com/iciargorospe/FIN331_FinalProject/commit/bb79537c8bbc2a542e3d60f899a5b3694483da98), and the corresponding results in `outputs/` on `audit-fixes`.

**Remaining limitations:** The multiple-testing adjustment currently only covers five anomalies and will need to be recalculated with the full sample. Our trading costs are hypothetical rather than measured, and our statistical comparisons do not prove that academic publication caused the observed declines.

### A4 - Fixed: (reproducibility issues)
We updated `requirements.txt` to pin the versions of all seven Python packages used in our original pipeline, including pandas, polars, and numpy. We later added pinned versions of the statistical libraries needed for our new analyses. We also removed the `%pip install` cell from `01_seed4_poc.ipynb` so that dependencies are installed separately instead of during execution.

Additionally, we created `hand_check.py` to independently download the Momentum anomaly data from OpenAP and recalculate its average monthly return during the original research sample.

We tested everything in a fresh Google Colab notebook. Both `python run_all.py` and `python hand_check.py` ran successfully! Our independent calculation matched the original pipeline's result of 1.275804% per month across 312 observations.

We also successfully reproduced our updated six-step pipeline, including the regression analysis, individual statistical tests, and economic analysis, in a fresh Google Colab environment.

**Evidence:** [Pinned dependencies commit](https://github.com/iciargorospe/FIN331_FinalProject/commit/573f74934661be3ac05824a76dd66c9fb0222bda), [notebook installation fix](https://github.com/iciargorospe/FIN331_FinalProject/commit/1986b6de4439f03ae2772c7d59f874f863e38a34), [independent hand-check commit](https://github.com/iciargorospe/FIN331_FinalProject/commit/8ff3b0259b856ff51ba4e233368a5fcc318fcdda), and the updated `run_all.py` on `audit-fixes`.
