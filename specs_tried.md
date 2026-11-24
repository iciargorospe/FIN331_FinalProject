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


---
### November 17, 2026 - Instructor Audit A2-A3 Implementation
We implemented the statistical methods documented above using our five-anomaly prototype before expanding to the full dataset.

**Panel regressions (A2):** We ran models with and without calendar-month fixed effects, using standard errors clustered by month. The estimated total change from the original research sample to post-publication was -0.5531 percentage points per month without month fixed effects (p = 0.0010), compared with -0.6967 percentage points with month fixed effects (p = 0.0812). The additional post-publication coefficient was not statistically significant in either model.

**Individual anomaly tests (A3):** We implemented Newey-West standard errors with 12-month lags and applied the Benjamini-Hochberg adjustment at a 5% false discovery rate. Two of the five anomalies (Accruals and AssetGrowth) showed statistically significant original-to-post-publication declines after the adjustment.

**Economic magnitude (A3):** We calculated absolute and relative changes in monthly returns and tested hypothetical monthly trading costs of 0, 25, and 50 basis points. At our baseline 25-basis-point assumption, Accruals had a negative average post-publication net return.

**Reproducibility:** We added `regression_analysis.py`, `anomaly_tests.py`, and `economic_analysis.py` to our pipeline. Their results are saved in `outputs/prototype_regression_results.csv`, `outputs/prototype_anomaly_tests.csv`, and `outputs/prototype_economic_results.csv`. We successfully reproduced the complete six-step pipeline in a fresh Google Colab environment.

**Limitations:** These results cover only five prototype anomalies, not the full sample. The individual tests approximate the original and post-publication periods as independent when combining their Newey-West standard errors. Trading costs are hypothetical rather than measured, and the observed relationships do not establish causation. We will revisit the findings when we expand the analysis.


---
### November 20, 2026 - Checkpoint 3 Full-Sample Selection
We expanded our analysis beyond the five-anomaly prototype using the October 2026 Open Asset Pricing release (`202610`). We picked our eligibility criteria after examining data availability but before running the full-sample statistical analyses.

**Initial universe:** OpenAP documentation contained 331 unique signals: 212 classified as Predictor, 114 as Placebo, and 5 as Drop. We chose the 212 Predictor signals for our primary analysis because our research focuses on published return predictors rather than placebo or excluded signals.

**Data retrieval and validation:** We downloaded monthly long-short returns from the original-paper (`op`) portfolio collection. The initial dataset contained 175,529 anomaly-month observations across all 212 predictors. All returns matched their metadata, all research timelines were valid, and we found no missing or infinite returns or duplicate anomaly-month observations.

**Period classification:** We classified observations as Original Sample, Pre-Publication Gap, Publication Year, Post-Publication, or Before Original Sample. Consistent with our previous methodology, we exclude the publication year and observations before the original sample from our main analyses.

**Minimum sample requirement:** For our primary analysis, we require at least 24 monthly return observations in both the Original Sample and Post-Publication periods. We did this to try and avoid running statistical tests on extremely short return histories. We retain available pre-publication gap observations for the panel regressions.

**Final eligible sample:** 209 anomalies met our 24-month requirement. We excluded:
- Activism1: 135 original-sample observations and only 14 post-publication observations.
- Activism2: 135 original-sample observations and only 14 post-publication observations.
- PatentsRD: 318 original-sample observations and no post-publication observations.

Our resulting analysis dataset contains 135,466 anomaly-month observations: 73,796 in the original research sample, 8,952 in the pre-publication gap, and 52,718 post-publication.

**Sample-length sensitivity:** A 12-month minimum would include 211 anomalies, while a 36-month minimum would include the same 209 anomalies as our primary 24-month requirement.

**Status at the time of sample selection:** We completed dataset construction and chose the eligibility rules before running the full-sample statistical analyses. The subsequent results are documented in the entry below.


---
### November 20, 2026 - Checkpoint 3 Full-Sample Analysis and Validation
We implemented our previously documented statistical methods on the 209 eligible anomalies. Our analysis uses 135,466 observations from the October 2026 Open Asset Pricing release.

**Descriptive analysis:**
We calculated each anomaly's average monthly return in the Original Sample, Pre-Publication Gap, and Post-Publication periods, then averaged these values equally across anomalies.

Average monthly returns were:
- Original Sample: 0.6911%
- Pre-Publication Gap: 0.4372%
- Post-Publication: 0.3095%

The average original-to-post change was -0.3816 percentage points per month. Overall, 181 of 209 anomalies (86.6%) experienced declining returns.

**Individual anomaly tests (A3):**
We followed our prespecified approach: two-sided original-to-post-publication tests using Newey-West standard errors with 12-month lags. We approximated the separated periods as independent when combining their standard errors.

Before multiple-testing adjustment, 54 of 209 changes were significant at the 5% level.

After applying Benjamini-Hochberg across all 209 tests at a 5% false discovery rate, 30 changes remained significant. All 30 were declines.

The individual statistics for all five prototype anomalies matched our earlier analysis. Adjusted p-values can differ because the number of tested hypotheses increased from five to 209.

**Panel regressions (A2):**
We estimated monthly returns using post-sample and post-publication indicators with anomaly fixed effects and calendar-month clustered standard errors.

Without calendar-month fixed effects:
- Post-sample: -0.2251 percentage points (p = 0.00155)
- Additional post-publication: -0.1477 percentage points (p = 0.06034)
- Combined original-to-post change: -0.3727 percentage points (p < 0.00001)

With calendar-month fixed effects:
- Post-sample: -0.2171 percentage points (p = 0.00040)
- Additional post-publication: +0.0097 percentage points (p = 0.88370)
- Combined original-to-post change: -0.2073 percentage points (p = 0.01106)

The post-sample coefficient measures the difference between the original research sample and pre-publication gap. The additional post-publication coefficient measures the change from the gap to the post-publication period. Their sum measures the original-to-post difference.

We retain the calendar-month fixed-effects specification as our preferred model because it accounts for common calendar-time conditions. It does not detect a statistically significant additional post-publication decline.

**Computational method and validation:**
Because the full sample is substantially larger than the prototype, we implemented a memory-efficient sparse fixed-effects regression instead of generating a large dense dummy-variable matrix.

We validated this implementation against the original five-anomaly regression. All six coefficients, standard errors, and p-values matched the conventional implementation.

**Economic category analysis:**
We grouped the 209 anomalies into 35 economic categories, of which 20 contain at least five anomalies.

Among categories with at least five anomalies, volatility (-0.754 percentage points), momentum (-0.673), and liquidity (-0.601) had some of the largest average monthly return declines. External financing (-0.054) and profitability (-0.124) had comparatively smaller declines.

These category rankings are exploratory. We have not formally tested whether differences between categories are statistically significant.

**Equal-length robustness specification:**
We repeated the individual anomaly tests using an equal number of monthly observations in the original and post-publication periods for each anomaly.

For each anomaly, we selected the last N available original-sample observations and the first N available post-publication observations, where N is the smaller of the two period lengths.

This produced:
- 172 of 209 anomalies with declining returns
- 21 BH-significant declines
- 0 BH-significant increases
- Average return change of -0.3740 percentage points
- 188 of 209 anomalies with the same direction of change as in the primary analysis
- 15 anomalies significant under both specifications

The broad descriptive decline remains similar, although the set of individually significant anomalies is sensitive to sample selection.

This robustness check concerns the original-to-post comparison; it does not independently test the additional post-publication regression coefficient.

**Reproducibility:**
We integrated the full-sample analyses into `run_all.py`, creating a 12-step pipeline.

On November 20, 2026, we cloned the `checkpoint3-v1` branch into a fresh Google Colab environment, installed the pinned dependencies, and successfully ran the complete pipeline.

All six full-sample output files were generated and verified:
- `outputs/full_sample_analysis.csv`
- `outputs/full_sample_summary.csv`
- `outputs/full_sample_tests.csv`
- `outputs/full_sample_regression.csv`
- `outputs/full_sample_categories.csv`
- `outputs/full_sample_robustness.csv`

**Interpretation and limitations:**
The results consistently show lower anomaly profitability after the original research sample. However, our preferred panel regression does not find evidence of an additional statistically significant decline following publication.

These findings are associational, not causal. Important limitations include original-sample selection bias, differing portfolio construction methods, publication timing measured only by year, and possible changes in market conditions.

Our Newey-West difference tests also approximate original and post-period estimation errors as independent. The Benjamini-Hochberg procedure relies on assumptions about the dependence among tests.

Our descriptive results weight anomalies equally, while the panel regressions use anomaly-month observations and fixed effects. Therefore, their estimates need not be identical.

**Remaining specifications:**
We have not yet expanded hypothetical trading-cost sensitivity to the complete 209-anomaly sample or implemented an actual trading-difficulty measure. Additional sensitivity analysis of the publication regression remains planned.

We will report these remaining limitations rather than treating unfinished analyses as completed findings.


---
### November 23, 2026 - Checkpoint 4 Research Extensions and Final Validation
We extended our completed 209-anomaly research with two additional analyses: full-sample hypothetical trading-cost sensitivity and winsorized panel-regression robustness.

These extensions were exploratory follow-up analyses conducted after our Checkpoint 3 results.

**1. Research Question 3: Trading-difficulty data feasibility**
We investigated using the Tidy Finance Factor Library to obtain trading-cost or trading-difficulty measures for our existing Open Asset Pricing anomalies.

Of our 209 anomalies, 177 had directly matching signal names in the dataset's sorting-variable list.

However, matching names did not establish that the underlying portfolios were equivalent. The available portfolio specification files also lacked the reference flags described in parts of the documentation.

We compared monthly returns from selected Tidy Finance portfolio constructions with our existing OpenAP returns:
- Book-to-Market: correlations of 0.5730 and 0.5928 across two candidate specifications.
- Accruals: correlation of 0.3868.
- Asset Growth: correlation of 0.1402.

The mean absolute monthly return differences were approximately 2.41 to 3.56 percentage points across these comparisons.

These comparisons only tested selected specifications; they do not establish that no compatible portfolios exist. Nevertheless, they raised substantial concerns about directly applying trading costs from those portfolios to our original-paper OpenAP returns. Differences in underlying data releases also remained unresolved.

**Decision:** We did not merge the Tidy Finance trading-cost estimates into our primary dataset or claim to have directly measured trading difficulty. Research Question 3 remains unanswered directly.

**2. Full-sample hypothetical trading-cost sensitivity**
We expanded the prototype trading-cost analysis to all 209 eligible anomalies in `full_sample_economic.py`.

We considered assumed monthly cost deductions of 0, 25, and 50 basis points from each anomaly's average post-publication gross return.

Results:
| Assumed monthly cost | Average net monthly return | Anomalies with positive average net returns |
|---|---:|---:|
| 0 bps | +0.3095% | 174 / 209 |
| 25 bps | +0.0595% | 101 / 209 |
| 50 bps | -0.1905% | 46 / 209 |

These calculations illustrate how sensitive apparent economic profitability is to hypothetical trading costs.

They do not measure actual transaction costs, incorporate anomaly-specific turnover, establish risk-adjusted profitability, or test whether trading difficulty explains the persistence of anomalies.

Output: `outputs/full_sample_economic.csv`.

**3. Winsorized regression robustness**
We tested whether extreme monthly returns materially influenced our original panel-regression conclusions.

We capped returns below the pooled 1st percentile (-10.8256%) and above the pooled 99th percentile (+12.6634%). This affected 1,355 observations in each tail, or 2,710 of 135,466 observations overall.

We then reestimated both original panel specifications using the same regression methodology and calendar-month clustered standard errors.

In our preferred model with anomaly and calendar-month fixed effects:
| Coefficient | Original estimate | Winsorized estimate | Winsorized p-value |
|---|---:|---:|---:|
| Post-sample | -0.2171 | -0.1780 | 0.00023 |
| Additional post-publication | +0.0097 | +0.0250 | 0.65048 |
| Total original-to-post | -0.2073 | -0.1530 | 0.02126 |

All coefficients are measured in percentage points of monthly returns.

The preferred regression continues to show a statistically significant overall decline, without a statistically significant additional post-publication effect.

The estimated magnitude of the total decline becomes smaller after winsorization.

In the model without calendar-month fixed effects, the additional post-publication coefficient becomes statistically significant after winsorization (p = 0.02524), whereas it was not significant at the 5% level in the original specification (p = 0.06034).

Therefore, our preferred model's qualitative conclusions are robust to this treatment of extreme values, although magnitudes and some alternative-specification significance results are sensitive.

Output: `outputs/full_sample_winsorized_regression.csv`.

**4. Final reproducibility validation**
We expanded `run_all.py` from 12 to 14 steps, incorporating both Checkpoint 4 analyses.

We cloned the `checkpoint4-v1` branch in a fresh Google Colab environment, installed the pinned requirements, and successfully ran all 14 steps.

We also expanded `verify_offline.py` to reproduce seven downstream full-sample output tables using the committed compressed dataset, without downloading data from OpenAP.

All seven output comparisons passed.

An independent hand calculation for Accruals reproduced its original-sample average monthly return of 0.686739%, using 360 monthly observations.

**Final interpretation:** Our descriptive and regression findings remain the primary results. The additional analyses strengthen the economic interpretation and sensitivity checks but do not establish a causal publication effect or directly measure trading difficulty.

Remaining project tasks involve final documentation, website integration, independent review, and presentation preparation.

