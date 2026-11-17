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
We will record future specification changes here, including their purpose, results, and whether we retain them in the final analysis.

We will also document approaches that do not support our hypotheses rather than reporting only favorable findings.
