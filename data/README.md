# Included inputs

Both original CSV files are included in this **public repository** at the owner's request:

```text
data/train/companies.csv
data/holdout/companies.csv
```

The labeled CSV has 4,818 rows and 68 columns, including `Id` and binary `Bankrupt`; the unlabeled CSV has 1,092 rows and 67 columns. The remaining 66 attributes include `num_*`, `ratio_*`, `total_assets`, `sales`, `total_liabilities`, and `short_term_liabilities`. CSVs contain missing values. The notebook contains the supplied attribute definitions, with provenance and unit limitations retained.

`results/input_manifest.json` records the original SHA-256 fingerprints. `python scripts/check_project.py` verifies the included files, fingerprints, dimensions, and expected target/identifier columns. The reproduction script also rejects changed inputs before fitting.

From the repository root, run `python scripts/reproduce.py --data-dir data --kernel bankruptcy-risk --mode final` after installing the documented environment. Interactive notebook execution uses this directory automatically. `BANKRUPTCY_DATA_DIR` can override it.

The supplied materials do not establish the authoritative dataset origin or redistribution rights. The owner explicitly authorized public visibility, including these files, on November 2, 2026. Repository availability does not establish redistribution rights or grant a dataset license. Local execution reports, fitted models, and per-company prediction exports remain excluded.
