# FIN331_FinalProject
SEED 4 :)

## Local website preview

1. From this folder, run `python3 prepare_data.py` to generate `outputs/explorer_data.json` from `checkpoint1_sample.csv`.
2. Start a local static server with `python3 -m http.server 8000`.
3. Open [http://localhost:8000](http://localhost:8000) in your browser. Stop the server with Ctrl+C.

The website uses only HTML, CSS, JavaScript, and saved JSON; Python's standard library is enough to prepare the data. The browser needs a local server to load the JSON file.

## Rebuild the explorer data

Run `python3 prepare_data.py` after updating the CSV. The script validates the expected columns, duplicate anomaly-month rows, and consistent metadata, then recreates `outputs/explorer_data.json` with period summaries and annual chart averages.

Comparison periods are constructed from `sample_start_year`, `sample_end_year`, and `publication_year`: the original sample is inclusive; the gap is after the sample and before publication; post-publication is strictly after the publication year. Observations before the original sample and in the publication year are excluded. The gap is reported separately.

The notebook uses Open Asset Pricing release 202610. Its upstream portfolio preparation converts CRSP returns with `ret = 100*ret` in [OpenSourceAP/CrossSection, Portfolios/Code/11_ProcessCRSP.R](https://github.com/OpenSourceAP/CrossSection/blob/master/Portfolios/Code/11_ProcessCRSP.R), so `ret` is displayed as a monthly percentage, not a decimal. We report arithmetic monthly averages; chart points aggregate those monthly returns by calendar year, without annualizing or compounding.

This is a five-anomaly descriptive prototype, not the group's final analysis. A post-publication difference is not evidence that publication caused it. `IndIPO` identifies firms that went public 6–36 months earlier; it does not measure industry-wide IPO activity.
