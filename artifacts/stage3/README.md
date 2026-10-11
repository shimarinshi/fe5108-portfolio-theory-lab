# Stage 3: Fama–French three-factor analysis

This folder contains the FE5108 Track A Stage 3 FF3 calculation and exhibits for the same 30 US stocks and 108 monthly observations (2017-01 through 2025-12) used in Stage 2. It adds published SMB and HML return spreads to the existing Mkt-RF market factor. It does not construct those factors from the 30 test stocks or perform a trading backtest.

## Required exhibits

- 3a, factor construction: `exhibit_3a_factor_construction.md`
- 3b, CAPM versus FF3 alphas for all 30 stocks: `exhibit_3b_alpha_before_after.csv` and `.png`
- 3c, Stage 2 alpha-screen verdict: `exhibit_3c_verdict.md`
- Full estimates and checks: `all_30_model_results.csv` and `checks.json`
- Code and review: `run_stage3.py` and `AUDIT.md`

## Reproduce from the repository root

After Stage 2 outputs exist, install the root `requirements.txt` and run:

```bash
python artifacts/stage3/run_stage3.py --repo .
```

The script reads the existing selected universe, monthly total and excess returns, monthly RF, cached FF3 factors, and Stage 2 CAPM/GRS results. It writes the listed files into this folder and does not edit Stage 1 or 2. Input returns are monthly decimals; Exhibit 3b columns named `percent_per_month` are percentages. The |OLS t(alpha)| > 2 screen is descriptive, not a multiple-testing-adjusted finding of mispricing.

This folder is a Stage 3 supplement. The repository’s current `run_all.py` does not invoke it; integration into the project’s single entry point and verification of a full rerun remain necessary for the final course submission.
