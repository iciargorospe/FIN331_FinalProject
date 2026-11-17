# FIN331 Final Project: Did Academic Research Kill the Anomalies?

**Live Dashboard:** https://iciargorospe.github.io/FIN331_FinalProject/

## Reproducing Our Results
To rebuild the dataset, website data, and results table from scratch:

```bash
pip install -r requirements.txt
python run_all.py
```

This generates:
- `outputs/checkpoint1_sample.csv`
- `outputs/explorer_data.json`
- `outputs/period_summary.csv`

## Project Overview
Our group is investigating whether investment anomalies become less profitable after their findings are published in academic research.

Our main research questions are:
1. Do anomaly returns decline after publication?
2. Which types of anomalies are most likely to remain profitable?
3. Does the difficulty of trading an anomaly help explain its post-publication performance?

## Data
We use the October 2026 release (`202610`) of the Open Asset Pricing dataset, accessed through the `openassetpricing` Python package.

Our initial proof of concept includes five anomalies: Book-to-Market (BM), Initial Public Offerings (IndIPO), 12-Month Momentum (Mom12m), Accruals, and Asset Growth.

The dataset contains 4,454 anomaly-month observations, including monthly long-short returns, publication years, economic categories, and original research sample years. Returns are expressed as monthly percentages.

### Data Source and Construction
Our data comes from Open Asset Pricing (OpenAP), developed by Andrew Chen and Tom Zimmermann. We use the October 2026 release (`202610`), accessed through the `openassetpricing` Python package (version 0.1.0).

Our notebook downloads two datasets:
- **Signal documentation:** Information about each anomaly, including its publication year, original research sample period, and category.
- **Portfolio returns:** Monthly returns from the `op` (original-paper) portfolio collection. We select the `LS` (long-short) portfolio for each anomaly.

These are portfolio returns already constructed by OpenAP. We are not calculating individual stock returns or building portfolios from scratch. Because we use the original-paper portfolio collection, the construction methods may differ across anomalies.

Each observation in our dataset represents one anomaly in one month. Returns are measured in percentages per month. We use these returns to compare average profitability across the original research sample, pre-publication gap, and post-publication periods.

**Data retrieval:** The pipeline successfully downloaded and processed the October 2026 release on November 12, 2026. Rerunning `run_all.py` downloads the selected release again.

**Sources:**
- OpenAP website: https://www.openassetpricing.com/
- OpenAP source code: https://github.com/OpenSourceAP/CrossSection
- Python package: https://pypi.org/project/openassetpricing/

## Methodology
Following feedback on Checkpoint 1 and the approach discussed by McLean and Pontiff, we distinguish three comparison periods:
- **Original Sample:** Years included in the original academic study.
- **Pre-Publication Gap:** Years between the end of the original sample and publication.
- **Post-Publication:** Years after the paper was published.

We exclude publication-year observations and observations before the original research sample from our primary comparisons.

### Period Classification and Comparison
Our dataset includes two related variables: `period` and `post_publication`.

The `period` column identifies the original research sample, pre-publication gap, publication year, post-publication period, and observations before the original sample. We use this more detailed classification for our current results and website.

The `post_publication` indicator equals 0 for observations in the original sample or pre-publication gap, and 1 for observations after publication. It is missing for the publication year and observations before the original sample.

For our main analysis, we plan to compare original-sample returns directly with post-publication returns. We will examine the pre-publication gap separately to help distinguish declines that began before publication from those occurring afterward. We will not treat all observations with `post_publication = 0` as if they belonged to the original research sample.

### Threats to Validity
Our current results are preliminary, and several factors could affect how we interpret them:

- **Correlation vs. causation:** A decline in anomaly returns after publication does not necessarily mean publication caused the decline. Market conditions, changes in investor behavior, and other factors may also explain it.
- **Data mining and original-sample bias:** Anomalies may look especially profitable in their original research samples because researchers identified them using those historical data. We examine the pre-publication gap separately to help investigate this possibility.
- **Unequal sample periods:** Some anomalies have much longer post-publication histories than original research samples. We plan to test equal-length windows as a robustness check.
- **Trading costs:** Our current comparisons do not adjust for additional transaction costs or other implementation difficulties. A strategy with positive returns may not be profitable after these costs.
- **Limited prototype sample:** We currently study only five anomalies. They were selected for our initial prototype, so we cannot assume our findings represent the entire universe of published anomalies.
- **Portfolio construction and timing:** We rely on OpenAP's original-paper portfolios, which may use different construction methods across anomalies. We still need to verify the underlying signal timing and address possible look-ahead or selection biases.
- **Publication timing:** Because we have publication years rather than exact publication dates, we exclude the entire publication year instead of trying to divide it into before and after publication.

We will address these limitations where possible as we expand the analysis. For now, our findings are descriptive rather than causal.

### Data Validation and Verification
We have implemented several checks to help ensure our results are accurate and reproducible:

1. **Merges:** Our notebook uses `validate='m:1'` when combining returns with anomaly metadata and confirms that every return matches a metadata record.
2. **Unique observations:** We check that each anomaly-month appears only once.
3. **Metadata:** We verify that publication years are available and that each anomaly has consistent metadata across observations.
4. **Date consistency:** We check that original research sample years follow a logical order and end before publication.
5. **Return values:** We check for invalid or non-finite returns before generating the website data.
6. **Period classifications:** We tested seven boundary months for the Momentum anomaly to confirm that observations are correctly assigned to the original sample, pre-publication gap, publication year, and post-publication period.
7. **Summary statistics:** We checked the observation counts and average monthly returns against the underlying dataset and confirmed that the website results agree with our calculations.
8. **Reproducibility:** We successfully ran `run_all.py` in a fresh Google Colab environment and regenerated the dataset, website JSON, and summary table.

Our current dataset contains 4,454 anomaly-month observations. Of these, 3,524 are included in the three comparison periods used by the website. The remaining observations fall in excluded periods.

These checks support the reliability of our current prototype, but they do not replace the additional statistical and methodological tests planned for the final analysis.

## Running the Proof of Concept
1. Open `01_seed4_poc.ipynb` in Google Colab or a Jupyter notebook environment.
2. Run the notebook's cells in order. The first cell installs the required packages.
3. The notebook downloads the data, constructs the dataset, and performs validation checks.
4. The resulting CSV is saved to `outputs/checkpoint1_sample.csv`.

The notebook uses `openassetpricing` version `0.1.0` and data release `202610`.

## Website Prototype
Our interactive website currently uses the five proof-of-concept anomalies to display descriptions, publication years, historical return charts, and summary statistics across the three comparison periods.

The website uses HTML, CSS, JavaScript, and a JSON data file generated by `prepare_data.py`. It does not require Streamlit.

### Running the Website Locally
1. From the repository folder, run `python3 prepare_data.py` to generate `outputs/explorer_data.json` from `outputs/checkpoint1_sample.csv`.
2. Start a local server with `python3 -m http.server 8000`.
3. Open `http://localhost:8000` in your browser. Stop the server with Ctrl+C.

The Python script checks for duplicate observations and consistent metadata, calculates summary statistics, and prepares annual chart averages.

The website displays arithmetic average monthly returns. The chart's annual points are averages of monthly observations, not compounded annual returns.

### Limitations
This website is currently a descriptive prototype using five anomalies, not our final analysis. Differences in returns before and after publication do not establish that publication caused those changes.

## Current Status
Checkpoint 1 establishes our initial dataset and methodology using five anomalies. Our next steps are to expand the analysis, evaluate statistical significance, compare anomaly categories, and develop the interactive website further to present our findings.
