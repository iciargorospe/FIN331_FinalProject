# Instructor audit: Team 7, Checkpoint 2

**Repo:** iciargorospe/FIN331_FinalProject · **Audited commit:** `a687510` (2026-11-12, tip of PR #2 `website`, not merged) · **Seed:** 4, did academic research kill the anomalies?

> Note from your human teacher: This review is generated with minimal supervision from Opus 5.5-high. It is thorough, but can be too generous at times and doesn't know my taste for what is "good". Grades it and I would assign are correlated, but noisy, ok? If you want additional feedback from _me_, you need to find me before/after/during class or during office hours for a guaranteed speedy reply. I will try to respond to emails and issues, but can not respond to student inquiries around the clock across the final weeks of class. Response times will be unpredictable, though during Thanksgiving week, I will do my best to respond quickly virtually, as in person options will be nil.

## Summary

The v0 pipeline is small, clean and correct as far as I could test it. The data version is pinned (Open Asset Pricing release `202610`, package `0.1.0`). The period split follows McLean & Pontiff. Keys and merges are checked. I recomputed every number in `outputs/period_summary.csv` independently and matched all 15 to machine precision. I couldn't rerun the download step, because the audit environment can't reach the data host (not your bug). Before v1, three things matter most:
1. Your Checkpoint 2 work is only on an unmerged PR (A1).
2. Comparing raw pre/post means can't separate "publication" from "later calendar years" (A2).
3. There is no statistical test or multiple-testing plan yet, and you'll need both at 200+ anomalies (A3).

| Check | Result |
|---|---|
| Reruns from scratch | ⚠️ step 1 (the notebook) couldn't download in the audit environment (host blocked). Steps 2–3 on your committed dataset reproduce `period_summary.csv` and `explorer_data.json` exactly |
| Inputs have provenance | ✅ release `202610` is passed to `OpenAP()`, package pinned, retrieval date in the README |
| Keys unique, merges validated | ✅ `validate='m:1'` with an `_merge` check, `(signalname, month)` asserted unique |
| No look-ahead / survivorship | ✅ for v0. Original sample, gap and post periods come from the paper's sample and publication years. The publication year is dropped |
| LLM leakage handled | n/a |
| `specs_tried.md` complete | ✅ for v0. The planned specs are listed |
| Magnitudes discussed | ⚠️ means only. No costs or tests yet (A3) |
| Hand checks | ⚠️ boundary-month asserts for Mom12m, but no independent recomputation of a result (A4) |
| Threats to validity | ✅ README section. A2 adds the main one |
| Every number traces to `outputs/` | ✅ 4,454 and 3,524 rows, the proposal's example rows, and every period mean |

## What holds up

- **Every result recomputed.** My own code reclassifies all 4,454 rows of `outputs/checkpoint1_sample.csv` into periods from `month`, `sample_start_year`, `sample_end_year` and `publication_year`. It agrees with your `period` column on all 4,454 rows. It reproduces all 15 counts and means in `period_summary.csv` (largest difference 2.2e-16). Example: Mom12m original sample 312 months at 1.2758%/month, post-publication 384 months at 0.8966%.
- **Seed 4, data version recorded:** `OpenAP(202610)` fetches the fixed path `Data-Release-2026.10`, so a rerun gets the same data, and `requirements.txt` pins `openassetpricing==0.1.0`.
- **Seed 4, in-sample vs. out-of-sample:** three periods (original sample, pre-publication gap, post-publication), with the publication year and pre-sample years excluded. This is the McLean & Pontiff design. The Momentum boundary asserts (notebook cell 7) are a good test.
- **Traceability:** the proposal's example rows (Mom12m 1989-12: 5.43, 1990-01: −7.90, 1994-01: −4.67) match `checkpoint1_sample.csv`.

## Findings

### A1 · Major · The Checkpoint 2 work is only on an unmerged pull request

**Evidence:** `main` at the deadline (`59cf6ce`, 2026-11-11) has no `PROPOSAL.md`, `audits/01_self_audit.md`, `run_all.py`, `specs_tried.md` or `index.html`. They exist only on the `website` branch (PR #2, last commit `a687510`, 2026-11-12), which is not merged.

**Why it matters:** The default branch is what readers, the dashboard host and later audits see. Today a fresh clone of `main` doesn't contain your pipeline or dashboard.

**Fix:** Merge PR #2 into `main`. Serve GitHub Pages from `main`, and make sure the README link points to the site built from `main`.

**How to show it's fixed:** `git ls-tree origin/main` lists the CP2 files, and the Pages site shows the Results section.

### A2 · Major · Pre/post means can't separate a publication effect from a time trend

**Evidence:** In `period_summary.csv`, post-publication averages are lower for all five anomalies. The post/original ratio is 0.13 (Accruals), 0.32 (AssetGrowth), 0.58 (BM), 0.74 (IndIPO) and 0.70 (Mom12m), an average decline of 50%. But each anomaly's post period covers different calendar years: BM from 1981, AssetGrowth from 2009 (from `publication_year` in `checkpoint1_sample.csv`).

**Why it matters:** If anomaly returns are falling for everyone over time (cheaper trading, more quant capital), the pre/post gap mixes that trend with the effect of publication. You list "correlation vs. causation" as a threat, but the analysis plan doesn't yet address it. McLean & Pontiff handle this with calendar-time controls.

**Fix:** In v1, run McLean & Pontiff's panel regression: anomaly-month returns on post-sample and post-publication dummies, with month fixed effects (or a time trend), and standard errors clustered by month. Comparing anomalies in the same calendar months separates publication from time.

**How to show it's fixed:** A regression table in `outputs/` with month fixed effects, and the post-publication coefficient reported with and without them.

### A3 · Minor · No statistical tests, and no multiple-testing plan yet

**Evidence:** `outputs/period_summary.csv` has counts and means only. There are no standard errors or t-stats. `specs_tried.md` lists "statistical inference" as planned, but has no multiple-testing rule. Your self-audit marks magnitudes as a "Problem".

**Why it matters:** This is on the seed's audit list: "the multiple-testing adjustment you chose". At 200+ anomalies, some per-anomaly declines will look significant by chance, and the seed's stretch goal (ranking signals) needs a stated adjustment (e.g. Benjamini–Hochberg, or Harvey–Liu–Zhu's t > 3). Monthly anomaly returns are also autocorrelated, so the tests need Newey–West errors.

**Fix:** Decide and record in `specs_tried.md`, before running the full sample:
- the test (pooled regression as in A2, plus per-anomaly differences with Newey–West SEs),
- the multiple-testing adjustment,
- how magnitudes will be reported (percent decline, and net of a simple cost assumption).

**How to show it's fixed:** `specs_tried.md` names the adjustment before the v1 results, and the outputs report SEs.

### A4 · Minor · Reproducibility details: unpinned dependencies, `%pip` inside the pipeline, no independent hand check

**Evidence:**
- `requirements.txt` pins only `openassetpricing`. `pandas` (and the `polars` that `openassetpricing` uses for downloads) float, and the audit environment resolved `pandas 3.1.1` and `polars 2.1.0`.
- Notebook cell 0 runs `%pip install -q openassetpricing==0.1.0 pandas`, so `run_all.py` changes the environment while it runs. It fails where pip isn't available.
- The checklist says "Checks by hand: Not yet". There is no script that recomputes a result a second way.

**Fix:**
- Pin all packages (`pip freeze > requirements.txt`) and remove the `%pip` cell (the README already installs requirements).
- Add a short `hand_check.py` that recomputes one period mean directly from the OpenAP download without the notebook's code, and asserts it equals `period_summary.csv`.

**How to show it's fixed:** The auditor will rerun `run_all.py` in a clean environment and run the hand check.

## How to respond

This audit is `audits/02_instructor_audit.md` in your repo. Fix what you can, then add `audits/03_audit_response.md`, replying to each finding ID: fixed (the commit), disputed (why), or disclosed as a limitation (where).

**Deadline: Saturday, November 21, 2026.**
