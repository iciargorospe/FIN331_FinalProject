# Checkpoint 1 - STATUS
Our group picked Seed 4, "Did Academic Research Kill the Anomalies?" We want to investigate whether investment anomalies become less profitable after their findings are published in academic research. Specifically, we plan to look at three questions in order of priority: (1) Do anomaly returns decline after publication? (2) Which types of anomalies are most likely to remain profitable? And (3) Does the difficulty of trading an anomaly help explain its post-publication performance? (still need to investigate this last question and what data to use for it a bit further) We chose this topic because we thought it was interesting that publishing research on a profitable investment strategy could actually make that strategy less profitable.

For our proof of concept, we used the October 2026 release of the Open Asset Pricing dataset. We downloaded monthly long-short portfolio returns and publication metadata for five anomalies: Book-to-Market (BM), Industry IPO Activity (IndIPO), 12-Month Momentum (Mom12m), Accruals, and Asset Growth. On Colab, we then combined the datasets to create an anomaly-month table with 4,454 observations and 10 variables including returns, publication years, pre/post-publication indicators, economic categories, and original research sample dates. We also validated the merges, checked for duplicate observations, and manually inspected observations surrounding each publication year. Luckily, the code successfully produced our intended dataset structure!

Before continuing with the full analysis, we wanted feedback on a few method decisions:

- We were planning on comparing all available qualifying pre- and post-publication returns and then using equal-length windows to check/validate the results. => Do you recommend this approach, or should we just  use equal-length windows from the start?
- Since the dataset provides publication years rather than exact dates, we were also planning on excluding publication-year observations from our main comparisons. Is that ok?
- Finally, do you have any recommendations for measuring trading difficulty for our third research question?

---
# Checkpoint 3 - STATUS
**November 20, 2026**

## Progress Since Checkpoint 2
We expanded our project, "Did Academic Research Kill the Anomalies?", from a five-anomaly proof of concept to a full-sample analysis of published investment predictors.

We continue to use the October 2026 Open Asset Pricing release (`202610`). From 331 documented signals, we identified 212 classified as Predictor. We then required at least 24 monthly observations in both the original research sample and post-publication period, leaving 209 eligible anomalies.

Our final analysis dataset contains 135,466 anomaly-month observations across three periods:
- Original Sample: 73,796 observations
- Pre-Publication Gap: 8,952 observations
- Post-Publication: 52,718 observations

We exclude the publication year because the metadata provides publication years rather than exact dates.

## Main Findings
**1. Overall changes in profitability**
The equal-weighted average monthly return across anomalies declined from 0.6911% during the original research sample to 0.4372% during the pre-publication gap and 0.3095% after publication.

Overall, 181 of 209 anomalies (86.6%) experienced lower average monthly returns after publication than in their original research samples. The average decline was 0.3816 percentage points per month.

**2. Statistical significance**
We conducted individual original-to-post-publication tests using Newey-West standard errors with 12-month lags. We then applied the Benjamini-Hochberg procedure across all 209 tests at a 5% false discovery rate.

We found 54 statistically significant changes before multiple-testing adjustment and 30 afterward. All 30 BH-significant changes were declines.

**3. Panel regression results**
We estimated panel regressions with anomaly fixed effects, both with and without calendar-month fixed effects. Standard errors are clustered by calendar month.

In our preferred model with calendar-month fixed effects:
- The post-sample coefficient was -0.2171 percentage points per month (p = 0.0004).
- The additional post-publication coefficient was +0.0097 percentage points per month (p = 0.8837).
- The combined original-to-post-publication change was -0.2073 percentage points per month (p = 0.0111).

These results suggest that anomaly profitability was already lower after the original research sample ended. We do not find statistically significant evidence of an additional decline specifically after publication once we control for calendar-month effects.

These associations should not be interpreted as evidence that academic publication caused or did not cause changes in returns.

**4. Economic category differences**
We compared anomalies across 35 economic categories. Among categories with at least five anomalies, volatility, momentum, and liquidity showed some of the largest average declines. External financing and profitability showed comparatively smaller declines.

These comparisons are exploratory; we have not formally established that differences between categories are statistically significant.

**5. Equal-length robustness check**
We repeated our individual anomaly analysis using equally many original-sample and post-publication monthly observations for each anomaly.

Under this alternative specification:
- 172 of 209 anomalies experienced declining returns.
- 21 declines remained statistically significant after BH adjustment.
- The average monthly decline was 0.3740 percentage points.
- 188 anomalies showed the same direction of change as in our primary analysis.

The overall descriptive pattern remains similar, although significance results for individual anomalies are sensitive to the selected observations.

## Reproducibility and Validation
We expanded `run_all.py` into a 12-step automated pipeline covering data construction, descriptive statistics, significance tests, panel regressions, economic category comparisons, and equal-length robustness testing.

On November 20, we cloned the `checkpoint3-v1` branch into a fresh Google Colab environment and successfully reproduced the complete pipeline. All six full-sample output files were generated, with the expected observation counts and results.

We also confirmed that the full-sample significance-testing and regression implementations reproduce the corresponding results from our original five-anomaly prototype.

## Remaining Work
Our primary full-sample analysis is implemented and reproducible. Before the final project submission, we plan to:

- Update the README and analysis specification log to reflect our full-sample methods and findings.
- Prepare results files for our interactive website and update the site beyond the five-anomaly prototype.
- Expand the hypothetical trading-cost sensitivity analysis.
- Investigate whether suitable data are available to measure actual trading difficulty.
- Conduct additional robustness checks and finalize our interpretations and presentation.

Our current findings are descriptive and associational rather than causal. Important limitations include original-sample selection bias, differing anomaly portfolio constructions, approximate publication timing, and the absence of directly measured trading costs.

