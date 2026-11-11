# FIN331 Final Project: Did Academic Research Kill the Anomalies?

## Project Overview
Our group is investigating whether investment anomalies become less profitable after their findings are published in academic research.

Our main research questions are:
1. Do anomaly returns decline after publication?
2. Which types of anomalies are most likely to remain profitable?
3. Does the difficulty of trading an anomaly help explain its post-publication performance?

## Data
We use the October 2026 release (`202610`) of the Open Asset Pricing dataset, accessed through the `openassetpricing` Python package.

Our initial proof of concept includes five anomalies: Book-to-Market (BM), Industry IPO Activity (IndIPO), 12-Month Momentum (Mom12m), Accruals, and Asset Growth.

The dataset contains 4,454 anomaly-month observations, including monthly long-short returns, publication years, economic categories, and original research sample years. Returns are expressed as monthly percentages.

## Methodology
Following feedback on Checkpoint 1 and the approach discussed by McLean and Pontiff, we distinguish three comparison periods:
- **Original Sample:** Years included in the original academic study.
- **Pre-Publication Gap:** Years between the end of the original sample and publication.
- **Post-Publication:** Years after the paper was published.

We exclude publication-year observations and observations before the original research sample from our primary comparisons.

## Running the Proof of Concept
1. Open `01_seed4_poc.ipynb` in Google Colab or a Jupyter notebook environment.
2. Run the notebook's cells in order. The first cell installs the required packages.
3. The notebook downloads the data, constructs the dataset, and performs validation checks.
4. The resulting CSV is saved to `outputs/checkpoint1_sample.csv`.

The notebook uses `openassetpricing` version `0.1.0` and data release `202610`.

## Current Status
Checkpoint 1 establishes our initial dataset and methodology using five anomalies. Our next steps are to expand the analysis, evaluate statistical significance, compare anomaly categories, and develop an interactive website to present our findings.
