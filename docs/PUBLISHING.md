# Private GitHub repository

Repository: [Imemat16/bankruptcy-risk-modeling](https://github.com/Imemat16/bankruptcy-risk-modeling).

The owner authorized uploading the project and both original CSV files to a **private repository**. Public visibility has not been authorized. The input files are in `data/train/companies.csv` and `data/holdout/companies.csv` and are verified against the original manifest. Local execution reports, original coursework archives, credentials, and fitted models remain excluded.

## Subsequent updates

1. Run `python scripts/check_project.py`. Use the README reproduction command when changes affect the model or its evaluation.
2. Review `git status --short` and the staged diff. Keep credentials, local reports, and unrelated data out of commits.
3. Commit the reviewed changes and run `git push origin main`.
4. Verify that GitHub continues to show **Private**. Public release requires separate explicit owner approval and a review of dataset/course-material rights. No open-source license is asserted.

Project description: "Cost-sensitive corporate bankruptcy prediction with financial feature audits, grouped nested validation, and reproducible evaluation."

Suggested application project sentence: "Built a financial-risk classification pipeline that reduced illustrative 5:1 bankruptcy screening cost by 75% versus a majority baseline on a 964-company retrospective test split; evaluated threshold selection, grouped nested validation, missingness sensitivity, and uncertainty." Include the retrospective qualification when discussing the result.

## Automated checks

The saved publishing credential cannot create GitHub workflows. The complete check workflow is retained at `ci/validate.yml` as an inactive template. To enable automated checks, an authorized maintainer must move it to `.github/workflows/validate.yml` using a credential with workflow permission. Until then, run `python scripts/check_project.py` locally. This does not affect the completed local full replay or clean-environment rebuild.
