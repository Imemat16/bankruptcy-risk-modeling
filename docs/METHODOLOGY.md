# Methodology and statistical interpretation

## Prediction and decision

The label is `Bankrupt` (0/1), described in the supplied notebook as bankruptcy in the following year. The input is one row of financial attributes per company. `Id` is not a predictor. The relative cost is `5*FN + FP`; no dollar conversion is justified by these data. Under calibrated risk and these fixed costs, flagging at probability 1/6 is the theoretical rule. The empirical final threshold is 0.15, chosen from training validation together with classifier settings.

## Data boundaries

An 80/20 stratified random split with seed 42 yields 3,854 training and 964 test rows. Training is further partitioned into development and policy subsets using `StratifiedGroupKFold`; development comparison uses five grouped folds. Exact financial-profile hashes exclude both IDs and labels. Subsequent nested training studies use two five-fold outer arrangements with seeds 20261004 and 20261011 and three grouped inner folds. Preprocessing is fitted within each fitting fold. The final refit learns transformations on the 3,854 training rows only.

Grouping controls duplicate profiles within development validation. It does not make the original outer random test group-disjoint: 11 test rows share profiles with training. The reported sensitivity excludes these rows without retraining or adjusting the cutoff. Other entities may still be related in ways the supplied attributes cannot identify. No time-based evaluation is available.

## Financial transformations

`FinancialFeatures` removes ID/target columns, maps infinities and invalid divisions to missing, divides stored inventory and receivables by 365, and recomputes six financial columns according to the supplied formulas. Internal agreement with turnover-based amounts supports the 365 conversion; it is not independent accounting verification. Several supplied ratios disagree with reconstructions, so these are alternative representations, not guaranteed recovery of ground truth.

The normalized representation scales monetary attributes by positive assets and includes leverage, working capital, current ratio, net margin, and inventory/sales. The final liquidity bundle adds near cash/short debt, quick assets/short debt, inventory/current assets, short-debt share, approximate collection days, and nonnegative working capital interacted with a quick-asset shortfall. Zero denominators remain missing. A deterministic correlation filter retains columns in original order if absolute correlation with already-kept columns does not exceed 0.995. Median imputation retains missingness indicators; a signed log compresses extremes. The final tree model uses neither PCA nor an additional scaler.

## Model selection and evidence

Family screening compares logistic regression representations, logistic regression plus PCA, Naive Bayes, KNN, a decision tree, random forest, boosting, and a majority baseline. Subsequent analysis examines imputation (including targeted ratio_21 reconstruction), residuals, subgroup mistakes, liquidity candidates, calibration, and missingness reliance. Training studies led to median filling plus flags rather than regression imputation or calibration in the final recipe.

Matched eight-setting classifier/cutoff searches compare original and six-feature representations: recorded repeated costs are 912 and 875. The later broader 24-setting procedure costs 849 versus 875 for the eight-setting procedure and wins seven of ten paired folds. These reuse the same 3,854 companies twice, not 7,708 distinct companies. The final all-training inner optimized cost of 423 is a tuning estimate, not validation performance. The fixed recipe contains recorded summaries for traceability; the short reproduction route does not recompute them.

Repeated exploration, nested-procedure choice, and capacity-grid boundary selection reduce independence of the training comparisons. Fold standard deviations are descriptive, not confidence intervals or significance tests. A 99-permutation, deduplicated-profile logistic-regression check tests exploratory label association; it is not a significance test for the selected boosted model or its superiority. Its finite permutation resolution must be respected.

## Final evaluation

The frozen model gives TN=870, FP=32, FN=9, TP=53: cost 77 versus 310, recall 53/62, precision 53/85. Average precision is computed by `average_precision_score`. Brier score evaluates probability error; ROC-AUC evaluates ranking. A descriptive paired bootstrap resamples 964 test rows 1,000 times with seed 42 for baseline-minus-model cost and recall. It conditions on the fitted model, ignores selection uncertainty and correlated profiles, and is not an external deployment guarantee. Excluding overlapping profiles gives 953 test rows and unchanged cost 77.

The original notebook states that test results had previously been seen; the current execution order alone cannot restore their independence. Treat the test result as a transparent retrospective benchmark. The 1,092-row unlabeled file provides input-contract and shift checks only. All 29 holdout rows missing ratio_21 are flagged, which motivates collection-process scrutiny rather than a claim about true bankruptcy rates.
