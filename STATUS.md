# Checkpoint 1 - STATUS

Our group picked Seed 4, "Did Academic Research Kill the Anomalies?" We want to investigate whether investment anomalies become less profitable after their findings are published in academic research. Specifically, we plan to look at three questions in order of priority: (1) Do anomaly returns decline after publication? (2) Which types of anomalies are most likely to remain profitable? And (3) Does the difficulty of trading an anomaly help explain its post-publication performance? (still need to investigate this last question and what data to use for it a bit further) We chose this topic because we thought it was interesting that publishing research on a profitable investment strategy could actually make that strategy less profitable.

For our proof of concept, we used the October 2026 release of the Open Asset Pricing dataset. We downloaded monthly long-short portfolio returns and publication metadata for five anomalies: Book-to-Market (BM), Industry IPO Activity (IndIPO), 12-Month Momentum (Mom12m), Accruals, and Asset Growth. On Colab, we then combined the datasets to create an anomaly-month table with 4,454 observations and 10 variables including returns, publication years, pre/post-publication indicators, economic categories, and original research sample dates. We also validated the merges, checked for duplicate observations, and manually inspected observations surrounding each publication year. Luckily, the code successfully produced our intended dataset structure!

Before continuing with the full analysis, we wanted feedback on a few method decisions:

- We were planning on comparing all available qualifying pre- and post-publication returns and then using equal-length windows to check/validate the results. => Do you recommend this approach, or should we just  use equal-length windows from the start?
- Since the dataset provides publication years rather than exact dates, we were also planning on excluding publication-year observations from our main comparisons. Is that ok?
- Finally, do you have any recommendations for measuring trading difficulty for our third research question?
