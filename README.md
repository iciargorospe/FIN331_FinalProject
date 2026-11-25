# FIN331 Final Project: Did Academic Research Kill the Anomalies?

**Team 7 | Lehigh University | FIN331: Data and AI in Finance**

**Checkpoint 3:** Completed and merged into `main`
**Checkpoint 4:** Final research development on `checkpoint4-v1`

**Live Website:** https://iciargorospe.github.io/FIN331_FinalProject/

**Note:** The 209-anomaly Checkpoint 3 analysis is on `main`. Our additional Checkpoint 4 robustness analyses, economic sensitivity tests, and final validation improvements are currently on `checkpoint4-v1`. The live website still displays our five-anomaly prototype and is being updated separately.

## Project Overview
Our project investigates whether investment anomalies become less profitable after academic research about them is published.

An investment anomaly is a pattern in stock returns that appears to offer a predictable investment opportunity. Once researchers publish an anomaly, more investors may learn about and trade the strategy, potentially reducing its profitability.

We investigate three main research questions:

1. Do investment anomalies become less profitable after publication?
2. Which types of anomalies are more likely to remain profitable?
3. Does trading difficulty help explain which anomalies continue to perform well?

Our Checkpoint 3 analysis addresses the first two questions. Our third question remains under development because we have not yet incorporated direct measures of trading difficulty.

## Data
We use the October 2026 release (`202610`) of the Open Asset Pricing (OpenAP) dataset, developed by Andrew Chen and Tom Zimmermann.

Data are accessed using the `openassetpricing` Python package (version 0.1.0).

We download:
- Signal documentation containing publication years, original sample periods, and economic categories.
- Monthly long-short (`LS`) portfolio returns from the original-paper (`op`) portfolio collection.

These returns are calculated by OpenAP using each anomaly's original-paper portfolio construction. We do not construct the underlying stock portfolios ourselves.

Returns are expressed as percentages per month.

### Full-Sample Selection
The OpenAP documentation contains:
- 331 unique signals.
- 212 signals classified as `Predictor`.
- 114 signals classified as `Placebo`.
- 5 signals classified as `Drop`.

We selected the 212 Predictor signals for our primary research sample.

To ensure sufficient data for comparisons, we required at least 24 monthly return observations in both the original research sample and post-publication period.

This left 209 eligible anomalies.

The excluded anomalies were:
- `Activism1`: 14 post-publication observations.
- `Activism2`: 14 post-publication observations.
- `PatentsRD`: no post-publication observations.

### Final Analysis Dataset
Our full-sample dataset contains 135,466 anomaly-month observations:

| Period | Observations |
|---|---:|
| Original Sample | 73,796 |
| Pre-Publication Gap | 8,952 |
| Post-Publication | 52,718 |
| **Total** | **135,466** |

Each observation represents one anomaly in one calendar month.

We exclude observations before the original research sample and during the publication year from our primary analyses.

We exclude the publication year because our metadata identifies publication years rather than exact publication dates.

## Methodology
### 1. Descriptive Analysis
For each anomaly, we calculate its arithmetic average monthly long-short return during:

- The original research sample.
- The pre-publication gap.
- The post-publication period.

We then compare original-sample returns with post-publication returns.

Our overall descriptive statistics weight each anomaly equally, regardless of the number of monthly observations available.

### 2. Individual Statistical Tests
For each anomaly, we test whether its average monthly return differs between the original research sample and post-publication period.

We use:
- Two-sided tests.
- Newey-West standard errors with 12 monthly lags.
- An approximation treating the separated original and post-publication periods as independent when combining standard errors.
- Benjamini-Hochberg adjustment across all 209 tests, using a 5% false discovery rate.

### 3. Panel Regressions
We estimate panel regressions of monthly anomaly returns on two indicators:

- `post_sample`: equals 1 after the original research sample ends, including the pre-publication gap and post-publication period.
- `post_publication`: equals 1 only during the post-publication period.

The `post_sample` coefficient captures the change from the original research sample to the pre-publication gap.

The `post_publication` coefficient captures the additional change from the gap to the post-publication period.

The sum of these coefficients measures the overall original-to-post-publication difference.

We include anomaly fixed effects in both models and calendar-month fixed effects in our preferred specification.

Standard errors are clustered by calendar month.

To handle the full dataset efficiently, we use sparse matrices to absorb fixed effects rather than constructing a large dense dummy-variable matrix.

### 4. Economic Category Analysis
We group anomalies into 35 economic categories and calculate category-level average returns, changes in profitability, and the proportion of anomalies experiencing declines.

We distinguish categories with at least five anomalies from smaller categories when presenting comparisons.

These comparisons are exploratory rather than formal tests of differences between economic categories.

### 5. Equal-Length Robustness Check
We also compare equally long original-sample and post-publication periods.

For each anomaly, we select the last N available original-sample observations and the first N available post-publication observations, where N is the smaller of the two sample sizes.

We repeat the individual anomaly tests and Benjamini-Hochberg adjustment on these observations.

This tests the sensitivity of our original-to-post comparisons to the selected observation windows. It does not independently retest the additional post-publication regression coefficient.

## Checkpoint 3 Results
### Descriptive Results
Average monthly returns, weighted equally across anomalies:

| Period | Average Monthly Return |
|---|---:|
| Original Sample | 0.6911% |
| Pre-Publication Gap | 0.4372% |
| Post-Publication | 0.3095% |

The average original-to-post-publication decline was 0.3816 percentage points per month.

Overall, 181 of 209 anomalies (86.6%) experienced lower average returns after publication.

### Statistical Significance
Of 209 anomalies:
- 54 had statistically significant changes before multiple-testing adjustment.
- 30 had statistically significant changes after Benjamini-Hochberg adjustment.
- All 30 BH-significant changes were declines.

### Panel Regression Results
All coefficients are measured in percentage points of monthly return.

| Model | Coefficient | Estimate | p-value |
|---|---|---:|---:|
| Without Month FE | Post-sample | -0.2251 | 0.00155 |
| Without Month FE | Additional post-publication | -0.1477 | 0.06034 |
| Without Month FE | Total original-to-post | -0.3727 | <0.00001 |
| With Month FE | Post-sample | -0.2171 | 0.00040 |
| With Month FE | Additional post-publication | +0.0097 | 0.88370 |
| With Month FE | Total original-to-post | -0.2073 | 0.01106 |

Our preferred specification includes calendar-month fixed effects.

Under this specification, the overall decline remains statistically significant, but we do not detect an additional statistically significant decline specifically after publication.

This does not establish that publication has no effect. The analysis identifies associations rather than causal effects.

### Economic Category Results
We identified 35 economic categories, including 20 with at least five anomalies.

Among categories with at least five anomalies, volatility, momentum, and liquidity showed some of the largest average declines.

External financing and profitability showed comparatively smaller declines.

We have not formally established that these differences between categories are statistically significant.

### Equal-Length Robustness Results
Using equally long original and post-publication observation windows:

- 172 of 209 anomalies (82.3%) experienced declining returns.
- 21 anomalies had BH-significant declines.
- No anomalies had BH-significant increases.
- The average monthly decline was 0.3740 percentage points.
- 188 of 209 anomalies had the same direction of change as in the primary analysis.

The overall descriptive pattern remains similar, although individual significance findings are sensitive to the observations selected.

## Checkpoint 4 Research Extensions
### Full-Sample Trading-Cost Sensitivity
We extended our hypothetical trading-cost analysis to all 209 anomalies.

| Assumed monthly cost | Average post-publication net return | Anomalies with positive average net returns |
|---|---:|---:|
| 0 bps | +0.3095% | 174 / 209 |
| 25 bps | +0.0595% | 101 / 209 |
| 50 bps | -0.1905% | 46 / 209 |

These scenarios subtract assumed monthly costs from gross returns. They are not estimates of actual transaction costs, and positive average net returns do not necessarily imply statistically significant profitability.

Analysis: `full_sample_economic.py`
Output: `outputs/full_sample_economic.csv`

### Winsorized Regression Robustness
We capped monthly returns at the pooled 1st and 99th percentiles and reran our panel regressions.

In our preferred model with anomaly and calendar-month fixed effects:
| Coefficient | Original estimate | Winsorized estimate | Winsorized p-value |
|---|---:|---:|---:|
| Post-sample | -0.2171 | -0.1780 | 0.00023 |
| Additional post-publication | +0.0097 | +0.0250 | 0.65048 |
| Total original-to-post | -0.2073 | -0.1530 | 0.02126 |

Coefficients are percentage points of monthly return.

The overall decline remains statistically significant, while the additional post-publication effect remains statistically insignificant. Extreme returns affect the magnitude of our estimates, and some findings in the model without calendar-month fixed effects are sensitive to winsorization.

Analysis: `full_sample_winsorized_regression.py`
Output: `outputs/full_sample_winsorized_regression.csv`

### Two-Way Clustering Robustness
As an additional exploratory sensitivity check, we recalculated standard errors for our preferred regression using two-way clustering by anomaly and calendar month, instead of clustering only by calendar month.

| Coefficient | Original p-value | Two-way clustered p-value |
|---|---:|---:|
| Post-sample | 0.00040 | 0.00133 |
| Additional post-publication | 0.88370 | 0.89020 |
| Total original-to-post | 0.01106 | 0.01078 |

Regression coefficients were unchanged.

The overall original-to-post decline remains statistically significant at the 5% level, while the additional post-publication effect remains statistically insignificant. This strengthens the robustness of our inference but does not establish a causal effect of publication.

Analysis: `full_sample_two_way_clustering.py`
Output: `outputs/full_sample_two_way_clustering.csv`

### Trading-Difficulty Research Question
We investigated the Tidy Finance Factor Library as a potential source of trading-difficulty measures.

Although 177 of our 209 anomalies had matching names, selected candidate portfolios produced substantially different monthly returns from our OpenAP portfolios. We therefore did not combine their estimated trading costs with our returns.

We have not directly tested whether harder-to-trade anomalies experience smaller profitability declines. Our hypothetical trading-cost scenarios address economic profitability, not the relationship between actual trading difficulty and anomaly persistence.

The investigation and limitations are documented in `specs_tried.md`.

## Reproducing Our Results
The completed Checkpoint 3 analysis is available on main. The Checkpoint 4 extensions are currently on checkpoint4-v1.

### Step 1: Clone the Repository
```bash
git clone --branch checkpoint4-v1 --single-branch https://github.com/iciargorospe/FIN331_FinalProject.git
cd FIN331_FinalProject
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Complete Pipeline
```bash
python run_all.py
```

The pipeline runs 15 steps: six preserving the original prototype and nine building and analyzing the expanded sample.

The full-sample analysis generates:

| Output | Description |
|---|---|
| `outputs/full_sample_analysis.csv` | Final 209-anomaly dataset |
| `outputs/full_sample_summary.csv` | Anomaly-level descriptive statistics |
| `outputs/full_sample_tests.csv` | Individual tests and adjusted p-values |
| `outputs/full_sample_regression.csv` | Panel regression estimates |
| `outputs/full_sample_categories.csv` | Economic category comparisons |
| `outputs/full_sample_robustness.csv` | Equal-length robustness results |
| `outputs/full_sample_economic.csv` | Full-sample hypothetical trading-cost sensitivity |
| `outputs/full_sample_winsorized_regression.csv` | Winsorized panel-regression robustness |
| `outputs/full_sample_two_way_clustering.csv` | Two-way clustered regression sensitivity results |

### Offline Verification
We also commit a compressed snapshot of our analysis dataset at `outputs/full_sample_analysis.csv.gz`, constructed from OpenAP release `202610`.

After installing the dependencies, run:

```bash
python verify_offline.py
```

This restores the dataset in a temporary directory, reruns the eight downstream full-sample analyses, and compares their results with our committed output tables.

The script also independently recalculates Accruals' original-sample mean using a Python loop.

This verification does not require access to the Open Asset Pricing data host. The complete `run_all.py` pipeline still requires access to OpenAP to download its original inputs.

The pipeline also regenerates the original prototype outputs.

When the complete pipeline runs, it downloads the original data from OpenAP and rebuilds outputs/full_sample_analysis.csv. For offline verification, we have also committed a compressed copy of the dataset, so users can reproduce our downstream statistical results without accessing OpenAP.

### Independent Arithmetic Spot-Checks
In addition to reproducing our existing results, we developed a separate audit script to independently check selected calculations throughout the research pipeline.

To run these checks after installing dependencies:

```bash
python independent_hand_checks.py
```

The script verifies nine areas:
1. Dataset keys, period classifications, and regression indicators.
2. Original and post-publication average returns calculated directly from monthly observations.
3. An independently calculated Newey-West lag-12 standard error and p-value for Accruals.
4. Benjamini-Hochberg multiple-testing adjustments across 209 anomalies.
5. Economic category averages and anomaly counts.
6. Equal-length sample selection and average-return comparisons.
7. Hypothetical trading-cost deductions and profitability counts.
8. Winsorization thresholds and extreme-observation counts.
9. Regression coefficient totals and reported p-value calculations, including two-way clustering.

On November 25, 2026, all nine independent spot-checks passed.

These checks supplement our eight offline reproducibility comparisons. They provide independent arithmetic validation of selected results, but do not constitute an independent audit of the OpenAP source data or a complete re-estimation of every regression and covariance matrix.

### Reproducibility Validation
On November 20, 2026, we cloned the `checkpoint3-v1` branch in a fresh Google Colab environment, installed the pinned dependencies, and successfully executed the entire 12-step pipeline.

All six full-sample output files were generated, with the expected observation counts and findings.

We separately validated our full-sample significance-testing and sparse fixed-effects regression implementations against the original five-anomaly results.

On November 23, 2026, we also validated the complete Checkpoint 4 pipeline using a fresh clone of `checkpoint4-v1`. All 14 steps ran successfully, including the full-sample economic analysis and winsorized regression robustness check.

We separately ran `python verify_offline.py` using the committed compressed dataset. All seven downstream full-sample output tables matched their committed results, and an independent calculation confirmed Accruals' original-sample average monthly return of 0.686739% across 360 observations.

On November 25, 2026, we validated the updated 15-step pipeline using another fresh Google Colab clone of `checkpoint4-v1`. All 15 steps completed successfully, including the new two-way clustering robustness analysis.

We also expanded `verify_offline.py` to reproduce eight downstream full-sample output tables using the committed compressed dataset. All eight comparisons passed, and the independent Accruals hand calculation continued to match.

These checks establish computational reproducibility of our reported analyses, not causal identification or independent validation of the source data.

## Original Five-Anomaly Prototype
Our original proof of concept used five anomalies:
- Book-to-Market (`BM`)
- Industry IPO Activity (`IndIPO`)
- 12-Month Momentum (`Mom12m`)
- Accruals
- Asset Growth (`AssetGrowth`)

This prototype contained 4,454 anomaly-month observations, of which 3,524 were included in the three main comparison periods.

The prototype code and website remain in the repository to preserve our earlier work.

The website is built with HTML, CSS, and JavaScript and reads `outputs/explorer_data.json`.

To run it locally, first generate the prototype website data with `python run_all.py`, then start a local server:

```bash
python -m http.server 8000
```

Open `http://localhost:8000` in a browser.

The live website has not yet been updated to display the full 209-anomaly analysis.

## Limitations
Our findings do not establish that academic publication caused changes in anomaly returns.

Important limitations include:

- Original-sample selection bias: published anomalies may look especially profitable in the historical samples used to discover them.
- Publication timing: we know publication years, not exact publication dates.
- Calendar-time conditions: market-wide changes may influence anomaly profitability.
- Portfolio construction differences: the OpenAP original-paper portfolios may use different construction methods across anomalies.
- Sample selection: our primary analysis includes only eligible Predictor signals.
- Multiple testing: our significance results depend on testing assumptions and the dependence among anomalies.
- Statistical approximation: our individual difference tests approximate the two separated periods as independent.
- Unequal sample lengths: we address this descriptively with an equal-length-window robustness check.
- Our hypothetical trading-cost scenarios now cover all 209 anomalies. However, they are assumed monthly deductions, not measured transaction costs. We have not incorporated actual anomaly-specific trading costs or directly tested the effect of trading difficulty on profitability persistence.
- Different weighting: descriptive results weight anomalies equally, while panel regressions use anomaly-month observations and fixed effects.

## Project Documentation
- `STATUS.md`: Project progress and Checkpoint 3 findings.
- `specs_tried.md`: Statistical specifications, decisions, results, and limitations.
- `PROPOSAL.md`: Original research proposal.
- `audits/`: Instructor audit materials and responses.

## Remaining Work
Before the final project submission, we plan to:
1. Integrate full-sample results into the live interactive website.
2. Merge the finalized Checkpoint 4 research into `main`.
3. Complete an independent final audit.
4. Finalize and rehearse the presentation.

## Data Sources
- Open Asset Pricing: https://www.openassetpricing.com/
- OpenAP source code: https://github.com/OpenSourceAP/CrossSection
- Python package: https://pypi.org/project/openassetpricing/

Our research is a course project and should not be interpreted as investment advice.
