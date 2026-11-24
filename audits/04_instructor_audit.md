# Instructor audit: iciargorospe, Checkpoint 3

**Repo:** iciargorospe/FIN331_FinalProject · **Audited commit:** `e3d0b87` (2026-11-20, head of PR #6, branch `checkpoint3-v1`, not merged) · **Seed:** 4, did academic research kill the anomalies? · **CP2 audit:** `audits/02_instructor_audit.md` (commit `a687510`)

> Note from your human teacher: This review is generated with minimal supervision from Opus 5.5-high. It is thorough, but can be too generous at times and doesn't know my taste for what is "good". Grades it and I would assign are correlated, but noisy, ok? If you want additional feedback from _me_, you need to find me before/after/during class or during office hours for a guaranteed speedy reply. I will try to respond to emails and issues, but can not respond to student inquiries around the clock across the final weeks of class. Response times will be unpredictable, though during Thanksgiving week, I will do my best to respond quickly virtually, as in person options will be nil.

## Summary

A solid v1 on all 209 predictor anomalies, and all four CP2 findings are fixed.
- The prototype steps rerun identically.
- Every full-sample number in the README traces to `outputs/`. Your Benjamini–Hochberg adjustment checks out when recomputed from your p-values (30 significant, all declines).
- Your preferred month-fixed-effects result is interpreted carefully: the decline is real, but none of it is specifically post-publication.

Your v1 lives on PR #6 and isn't merged. That's fine for this checkpoint, but **please get it onto `main`**. Your live site deploys from `main`, so today it still shows the five-anomaly prototype (B1). The full-sample panel also isn't committed, so the full-sample results can't be rerun without a fresh download (B2).

## Follow-up on your Checkpoint 2 audit

Response file: `audits/03_audit_response.md` found (on `main` and PR #6).

| CP2 finding | Status | Evidence |
|---|---|---|
| A1 · CP2 work only on an unmerged PR | fixed | PRs #2 and #3 are merged. `git ls-tree origin/main` lists `PROPOSAL.md`, `run_all.py`, `specs_tried.md`, `index.html`, `audits/` and the analysis scripts. (The same issue is back for v1: see B1) |
| A2 · Pre/post means vs time trend | fixed | `outputs/full_sample_regression.csv` has "Without Month FE" and "With Month FE" models (135,466 obs, 209 anomalies, 1,200 months). With month FE: post-sample −0.2171 (p 0.0004), additional post-publication +0.0097 (p 0.884). The prototype version (`prototype_regression_results.csv`) regenerated identically |
| A3 · No tests; no multiple-testing plan | fixed | `specs_tried.md` was updated at `652b9cf` (2026-11-20 04:26), before the full-sample build (`a5979fb`, 15:21). `full_sample_tests.csv` has Newey–West SEs and BH-adjusted p-values. My BH recomputation from your `p_value` column matches `adjusted_p_value` to 9e-16 |
| A4 · Unpinned deps; `%pip`; no hand check | fixed | `requirements.txt` pins all 10 packages, and a venv built from it ran steps 2–6. `01_seed4_poc.ipynb` has no `%pip`. `hand_check.py` exists, but wasn't rerun: it downloads from Open Asset Pricing (see below) |

**4 of 4 fixed, 0 still open.**

## Checkpoint 3 checks

| Check | Result |
|---|---|
| Reruns from scratch (full sample) | ⚠️ steps 2–6 (prototype) reproduce exactly. Steps 1 and 7 download from Open Asset Pricing (not rerun, see below), and steps 8–12 need `outputs/full_sample_analysis.csv`, which isn't committed (B2) |
| Inputs have provenance | ✅ release `202610` is pinned in `build_full_sample.py`, and the package version is pinned |
| Keys unique, merges validated | ✅ `Acronym` asserted unique, and the metadata asserted complete |
| No look-ahead / survivorship | ✅ periods from each paper's own sample and publication years |
| LLM leakage handled | n/a |
| `specs_tried.md` complete | ✅ the full-sample plan was logged before the build |
| Magnitudes discussed | ✅ −0.38 pp per month average change (55% of the original-sample mean), plus a prototype trading-cost sensitivity |
| Hand checks | ⚠️ `hand_check.py` for Mom12m (prototype). None yet for the full-sample panel (B2) |
| Threats to validity | ✅ README, including "associations, not causal effects" |
| Every number traces to `outputs/` | ✅ README Table (0.6911 / 0.4372 / 0.3095%), "181 of 209 (86.6%)", "30 BH-significant, all declines" and the regression table match `full_sample_summary.csv`, `full_sample_tests.csv` and `full_sample_regression.csv` |
| Dashboard matches `outputs/` | ⚠️ it matches the prototype outputs. Full-sample results aren't on it (B1) |

Steps not rerun by design: the Open Asset Pricing downloads (`01_seed4_poc.ipynb`, `build_full_sample.py`, `hand_check.py`), whose data host was blocked at CP2. These are not counted against you.

## Getting ready for Dec 1

Presentations run only from URLs, with a hard cutoff at 9 minutes (10:45 section) or 10 minutes (12:10 section). Put your URL(s) in column G of the Team Projects sheet.

| Check | Result |
|---|---|
| Dashboard launches from a clean clone | ✅ static site. `python -m http.server` in a clean export of `e3d0b87`, then `index.html` returned 200. A headless browser loaded it with 0 console errors, 0 page errors and 0 failed requests (it fetches `outputs/explorer_data.json`) |
| Dashboard shows the v1 numbers from `outputs/` | ❌ it shows "Five-anomaly prototype · Not final results" (B1) |
| README links the live URL(s) | ✅ `README.md:9` links https://iciargorospe.github.io/FIN331_FinalProject/ (the live site itself wasn't checked). `README.md:11` says the live site still shows the prototype |

**Core story for 9–10 minutes:** the 209-anomaly decline (0.69% → 0.31% a month); the month-FE regression that splits it into post-sample and post-publication; then the categories. Comparing your split with McLean & Pontiff's would make a strong closing slide.

## What holds up

- **Reproduction of the prototype steps.** `prepare_data.py`, the `run_all.py` step-3 table, `regression_analysis.py`, `anomaly_tests.py` and `economic_analysis.py`, run on the committed `checkpoint1_sample.csv`, regenerate `period_summary.csv`, `prototype_anomaly_tests.csv`, `prototype_economic_results.csv` and `prototype_regression_results.csv` (max relative difference 1.4e-13). `explorer_data.json` matches except 2 floats differing at 2e-16.
- **Independent checks on the full-sample outputs.** Recomputing BH (5% FDR) from the 209 p-values gives the same 30 rejections, all declines. Averaging `full_sample_summary.csv` gives the README's original 0.6911%, post 0.3095% and change −0.3816 pp (median −0.3696), with 181 declines. `full_sample_summary.csv` and `full_sample_tests.csv` agree on every mean (max difference 9e-16).
- **Careful interpretation.** You call the month-FE specification preferred, report that the additional post-publication effect is +0.0097 (p 0.88), and say this "does not establish that publication has no effect."
- **Seed 4 items:**
  - **In-sample vs out-of-sample:** each paper's own sample end, plus a gap period.
  - **Multiple testing:** BH, named before the results.
  - **Data version:** `202610`, recorded.

## New findings

### B1 · Major · v1 isn't on `main`, so the live site shows the prototype

**Evidence:**
- `README.md:11` on PR #6: "The live website currently displays our original five-anomaly proof of concept. The expanded 209-anomaly results are implemented in the `checkpoint3-v1` branch and have not yet been incorporated into the live dashboard."
- The rendered `index.html` says "Five-anomaly prototype · Not final results". `script.js:1` loads `outputs/explorer_data.json` (5 anomalies).
- Your response to A1 says GitHub Pages deploys from `main`. `main` (`ebc07a9`) has none of the `full_sample_*` scripts or outputs.

**Why it matters:** Presentations run from the URL. Not merging was fine for this checkpoint, but the final repo and the live site are what readers see.

**Fix:** Merge PR #6. Then add the full-sample results to the site (e.g. the category table and a searchable list of the 209 anomalies from `full_sample_summary.csv` and `full_sample_tests.csv`), and drop the "prototype" banner.

**How to show it's fixed:** `main` contains `e3d0b87` or its successor, and the site shows 209 anomalies.

### B2 · Minor · The full-sample panel isn't committed, so steps 8–12 can't be rerun without a download

**Evidence:** `build_full_sample.py:172` writes `outputs/full_sample_analysis.csv`, which `full_sample_summary.py:10`, `full_sample_tests.py:14` and `full_sample_regression.py:17` read. That file isn't in the repo (`outputs/` on `e3d0b87` lists the summaries only). `hand_check.py` covers only the prototype's Mom12m.

**Why it matters:** Every headline number comes from that panel. Anyone without access to the Open Asset Pricing host (as here) can't rerun or check them.

**Fix:** Commit `full_sample_analysis.csv` (or a compressed copy) with its release and pull date, or commit a SHA-256 of it plus a script to rebuild it. Add one full-sample hand check, e.g. one anomaly's original-sample mean recomputed with plain loops.

**How to show it's fixed:** On a fresh clone with no network, steps 8–12 reproduce the `full_sample_*.csv` files.

## How to respond

This audit is `audits/04_instructor_audit.md` in your repo. Fix what you can, then add `audits/05_audit_response.md`, replying to each **B** finding (no CP2 findings are still open): fixed (the commit), disputed (why), or disclosed as a limitation (where).

There's no separate deadline for this response. Keep working through these until your final deliverables are due: the final repo is audited again then.
