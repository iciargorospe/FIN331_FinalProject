# Analysis Specification Log
This file documents the analytical choices we make throughout our project. We will update it as we test additional approaches so that our final results do not selectively report only favorable findings.

## Checkpoint 1-2: Current Prototype
**Sample:** Five anomalies (BM, IndIPO, Mom12m, Accruals, and AssetGrowth) from the Open Asset Pricing October 2026 release.

**Return measure:** Monthly long-short portfolio returns, expressed as percentages.

**Comparison periods:**
- Original research sample
- Pre-publication gap
- Post-publication period

We exclude the publication year and observations before the original research sample from our main comparisons.

**Current method:** Calculate the arithmetic average monthly return for each anomaly within each comparison period. Compare original-sample and post-publication averages, while reporting the pre-publication gap separately.

**Status:** Implemented in our prototype, with results saved to `outputs/period_summary.csv` and displayed on the website.

**Limitations:** These are descriptive comparisons. We have not established statistical significance or causality.

## Specifications Planned but Not Yet Tested
1. **Full anomaly sample:** Expand beyond the five-anomaly prototype to the broader Open Asset Pricing universe.
2. **Equal-length windows:** Compare returns using equal-length periods as a robustness check against unequal sample lengths.
3. **Statistical inference:** Test whether changes in returns are statistically distinguishable from zero, accounting for time-series dependence.
4. **Anomaly categories:** Compare persistence across different economic and data categories.
5. **Trading difficulty:** Explore whether measures of trading costs or implementation difficulty help explain post-publication performance, subject to data availability.

## Statistical Analysis Plan (Instructor Audit A2-A3)
Before running our full-sample analysis, we picked the following methods based on the instructor audit's recommendations:

**1. Overall publication effect:** We will run a panel regression of monthly anomaly returns on post-sample and post-publication indicators, including anomaly and calendar-month fixed effects. This will allow us to compare strategies during the same calendar months rather than relying only on raw pre/post averages. We will report the post-publication coefficients with and without calendar-month fixed effects, using standard errors clustered by month.

**2. Individual anomaly tests:** We will compare each anomaly's original-sample and post-publication average monthly returns, using two-sided statistical tests with Newey-West standard errors to account for possible correlation between monthly returns. Our primary specification will use a maximum lag of 12 months.

**3. Multiple-testing adjustment:** Since we plan to test 200+ anomalies, we will use the Benjamini-Hochberg procedure to control the false discovery rate at 5%. We will apply this adjustment to the full set of eligible per-anomaly pre/post tests rather than reporting only significant findings.

**4. Economic magnitude:** We will report changes in average monthly returns in percentage points and relative percentage changes where the original-sample mean is positive and sufficiently far from zero. We will also report standard errors, p-values, and adjusted p-values.

**5. Trading-cost sensitivity:** We will examine how profitability changes after subtracting hypothetical monthly trading costs. Our baseline assumption will be 25 basis points per month, with additional scenarios of 0 and 50 basis points. These are hypothetical assumptions rather than actual measured trading costs, and we will disclose this limitation.

**Status:** These methods have been selected and documented before running the full-sample analysis. They haven't been implemented or tested yet. We will record our results and any subsequent specification changes in the log below.

## Changes and Findings Log
We will record future specification changes here, including their purpose, results, and whether we retain them in the final analysis. We will also document approaches that do not support our hypotheses rather than reporting only favorable findings.

### November 17, 2026 - Instructor Audit A2-A3 Implementation
We implemented the statistical methods documented above using our five-anomaly prototype before expanding to the full dataset.

**Panel regressions (A2):** We ran models with and without calendar-month fixed effects, using standard errors clustered by month. The estimated total change from the original research sample to post-publication was -0.5531 percentage points per month without month fixed effects (p = 0.0010), compared with -0.6967 percentage points with month fixed effects (p = 0.0812). The additional post-publication coefficient was not statistically significant in either model.

**Individual anomaly tests (A3):** We implemented Newey-West standard errors with 12-month lags and applied the Benjamini-Hochberg adjustment at a 5% false discovery rate. Two of the five anomalies (Accruals and AssetGrowth) showed statistically significant original-to-post-publication declines after the adjustment.

**Economic magnitude (A3):** We calculated absolute and relative changes in monthly returns and tested hypothetical monthly trading costs of 0, 25, and 50 basis points. At our baseline 25-basis-point assumption, Accruals had a negative average post-publication net return.

**Reproducibility:** We added `regression_analysis.py`, `anomaly_tests.py`, and `economic_analysis.py` to our pipeline. Their results are saved in `outputs/prototype_regression_results.csv`, `outputs/prototype_anomaly_tests.csv`, and `outputs/prototype_economic_results.csv`. We successfully reproduced the complete six-step pipeline in a fresh Google Colab environment.

**Limitations:** These results cover only five prototype anomalies, not the full sample. The individual tests approximate the original and post-publication periods as independent when combining their Newey-West standard errors. Trading costs are hypothetical rather than measured, and the observed relationships do not establish causation. We will revisit the findings when we expand the analysis.
