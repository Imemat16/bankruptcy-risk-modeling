# Reproducibility report

Review date: November 2, 2026.

## Completed checks

- The frozen final model was refitted in a fresh Python kernel with an empty temporary working directory. Sixteen tagged notebook cells plus an evidence-check cell executed successfully.
- Both CSVs matched the SHA-256 fingerprints in `results/input_manifest.json`.
- The rebuild matched TN=870, FP=32, FN=9, TP=53, final cost 77, baseline cost 310, AP 0.8571, and ROC-AUC 0.9726. No model parameters, features, split, or threshold were changed to obtain these results.
- Prediction-contract checks passed: finite normalized probabilities, binary predictions, embedded cutoff, one output per input row, and invariance to ID/target columns. Inputs were not mutated.
- The fitted pipeline retained 59 financial columns and 57 missingness indicators.
- The descriptive bootstrap and 11-row duplicate-profile sensitivity reproduced. The same frozen model predicted 120 positive flags among 1,092 unlabeled companies; this is not a holdout accuracy estimate.
- Notebook schema, all 50 code-cell syntax trees, execution tags, metric arithmetic, and release-content checks passed. Both original CSVs are included in the public repository at the owner's request and checked against their original fingerprints; local output exclusion rules were checked with Git.
- The original notebook remains unchanged. It is fingerprinted in the manifest; no original history or submission archive was copied into Git.

## Checked environment

Python 3.11.16, Windows. Direct dependency versions:

| Package | Version |
|---|---|
| numpy | 2.4.6 |
| pandas | 3.0.5 |
| scipy | 1.17.1 |
| scikit-learn | 1.9.0 |
| matplotlib | 3.11.0 |
| nbformat | 5.11.0 |
| nbclient | 0.11.0 |
| ipykernel | 6.29.5 |
| threadpoolctl | 3.5.0 |
| joblib | 1.5.3 |

The original source records Python 3.11.16. A separate clean Windows virtual environment successfully installed `requirements.txt`, passed `python -m pip check` with no broken requirements, and repeated the complete final-model rebuild with the same reference metrics and contracts. `requirements-lock.windows.txt` records its full resolved dependency set, including notebook tooling. The clean rebuild completed in approximately 62 seconds after installation. No changes were made to the existing course environment.

## Execution scope

The short route uses fixed hyperparameters and recorded validation summaries from the research notebook. It verifies fitting, prediction, metrics, bootstrap, and holdout diagnostics. It does not reproduce nested searches, calibration studies, imputation comparisons, or the permutation test. The full route subsequently completed successfully in approximately 46.6 minutes on the review machine: all 50 research code cells plus the evidence-check cell executed in a fresh kernel and empty working directory. The final recipe agreement assertions passed, including capacity costs 849 versus 875, the selected hyperparameters, cutoff 0.15, and optimized training cost 423. Final metrics again matched the reference. Full-run aggregate evidence is in `results/full_replay_metrics.json`; the complete executed notebook is local under ignored `reports/`.

Local full execution can be slow. Run the commands in the README with authorized inputs; generated notebooks and logs belong under ignored `reports/`. Public aggregate results are in `results/verified_metrics.json`. The public notebook embeds fresh full-replay outputs, with per-company previews and stderr warnings containing local paths removed. All scientific computations remain; the original narrative and caveats are retained. Convergence-warning counts reported as research tables remain visible. The browser review copy is exported from this cleaned notebook.

## Practical limits

Exact numerical reproducibility is checked against the supplied files and pinned numerical stack. Fresh execution does not establish independent statistical validation, repair the original train/test profile overlap, establish data redistribution rights, or resolve the previous exposure to test outcomes. No labeled external or temporal test has been run. The local check script validates structure, arithmetic, and included input fingerprints/schema. `ci/validate.yml` provides an inactive GitHub Actions template for these checks; automation is not enabled because the publishing credential lacks workflow permission. Model-reproduction evidence comes from the documented local runs.
