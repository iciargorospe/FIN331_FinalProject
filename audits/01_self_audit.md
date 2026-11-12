# Checkpoint 2: Self-Audit

## 1. Issues Flagged by ChatGPT
We asked ChatGPT to review our repository as a skeptical finance professor. It flagged the following issues:

1. **No automated pipeline:** we had to run our notebook and website data script separately instead of using one command.
2. **Missing results:** our website didn't have a dedicated Results section, and we hadn't saved a separate results table.
3. **Period classification:** our `post_publication` indicator groups the original sample and pre-publication gap together, which could lead to incorrect comparisons.
4. **Data validation:** we needed stronger checks for missing or inconsistent metadata and dates.
5. **Small sample:** our prototype only includes five anomalies instead of the full dataset of 200+.
6. **Incomplete data documentation:** we needed to better explain our data source, retrieval date, and how portfolio returns were constructed.
7. **Limited analysis:** we had not tested statistical significance, trading costs, or differences across anomaly categories.
8. **Methodological limitations:** we needed to better explain possible biases, other explanations for our results, and how we plan to address them.
9. **Minor documentation issues:** we incorrectly labeled `IndIPO` in the README, and our website JSON identified the source CSV by filename rather than its full relative path.

**What passed:** ChatGPT did not find any confirmed look-ahead bias, data leakage, incorrect merges, duplicate anomaly-month observations, or inconsistent return units in our current calculations. However, some risks still need further investigation.

## 2. What We Fixed and What's Still Open
### What We Fixed in This Pull Request
- Created `run_all.py` and `requirements.txt` so we can reproduce our full pipeline with one command. We tested it successfully in a fresh Google Colab environment.
- Added a Results section to our live website and saved our results in `outputs/period_summary.csv`.
- Clarified our period classifications and how we will use them in our main analysis.
- Added checks for invalid research sample and publication dates.
- Expanded our README to explain our data source, portfolio construction, and retrieval date.
- Corrected the `IndIPO` description.
- Created `specs_tried.md` to track our analytical choices and prevent selective reporting.
- Added sections to our README covering threats to validity and the data checks we performed.

### What We Still Need to Fix
- **Expand our sample:** We will include the broader OpenAP anomaly dataset and add validation checks as needed.
- **Improve our statistical analysis:** We will test whether return changes are statistically significant, compare anomaly categories, and check equal-length periods.
- **Account for trading difficulty:** We will explore trading costs and other measures of how difficult each strategy is to implement, depending on available data.
- **Investigate possible biases:** We will further check the underlying portfolio construction, information timing, and potential look-ahead or selection bias.
- **Complete our verification:** We will document independent calculations for each pipeline step, make the JSON source path more specific, and continue updating our specification log.

## 3. Ten-Point Project Checklist
1. **It reproduces - OK:** We tested `run_all.py` in a fresh Colab environment, and it successfully regenerated our outputs.
2. **Every input has a provenance - OK:** Our README documents our data source, version, retrieval date, and download process.
3. **The unit of observation is right - OK:** Each row represents one anomaly-month; we check unique keys and validate merges.
4. **No look-ahead - Not Yet:** We found no confirmed errors but still need to check the timing of the underlying portfolio data.
5. **No LLM leakage - OK:** We do not use LLM-generated predictions or data in our financial analysis.
6. **No p-hacking - OK:** We created `specs_tried.md` and will update it as we test more specifications.
7. **Magnitudes, not just stars - Problem:** We report actual return changes but have not yet accounted for trading costs.
8. **Checks by hand - Not Yet:** We checked sample calculations and period classifications but still need independent checks for every pipeline step.
9. **Honest limits - OK:** Our README includes a Threats to Validity section explaining our main limitations.
10. **You understand it - Not Yet:** We still need to confirm that we can all individually explain the full pipeline and methodology.
