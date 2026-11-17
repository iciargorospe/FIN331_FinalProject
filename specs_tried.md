# Analysis Specification Log
This file documents the analytical choices we make throughout our project. We will update it as we test additional approaches so that our final results do not selectively report only favorable findings.

## Checkpoint 1–2: Current Prototype
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

## Changes and Findings Log

We will record future specification changes here, including their purpose, results, and whether we retain them in the final analysis.

We will also document approaches that do not support our hypotheses rather than reporting only favorable findings.
