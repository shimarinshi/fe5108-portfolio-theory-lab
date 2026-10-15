# Stage 3: Fama–French three-factor analysis

This folder contains the FE5108 Track A Stage 3 FF3 calculation and exhibits for the same 30 US stocks and 108 monthly observations (2017-01 through 2025-12) used in Stage 2. It adds published SMB and HML return spreads to the existing Mkt-RF market factor. It does not construct those factors from the 30 test stocks or perform a trading backtest.

## Required exhibits

- 3a, factor construction: `exhibit_3a_factor_construction.md`
- 3b, CAPM versus FF3 alphas for all 30 stocks: `exhibit_3b_alpha_before_after.csv` and `.png`
- 3c, Stage 2 alpha-screen verdict: `exhibit_3c_verdict.md`
- Full estimates and checks: `all_30_model_results.csv` and `checks.json`
- Code and review: [`scripts/stage3.py`](../../scripts/stage3.py) and `AUDIT.md`

## Reproduce from the repository root

Install the root `requirements.txt` and run the integrated entry point (automatically rebuilding Stage 1 and Stage 2 first):

```bash
python3 run_all.py --stage3
```

The script reads the existing selected universe, monthly total and excess returns, monthly RF, cached FF3 factors, and Stage 2 CAPM/GRS results. It writes the listed files into this folder and does not edit Stage 1 or 2. Input returns are monthly decimals; Exhibit 3b columns named `percent_per_month` are percentages. The |OLS t(alpha)| > 2 screen is descriptive, not a multiple-testing-adjusted finding of mispricing.

To run all four stages, use `python3 run_all.py --stage3 --stage4`. With existing Stage 2 outputs, `python3 scripts/stage3.py` runs Stage 3 alone. The original `python3 artifacts/stage3/run_stage3.py --repo .` command remains supported; both standalone commands accept `--repo` and `--out`. The canonical implementation is in `scripts/stage3.py`.
