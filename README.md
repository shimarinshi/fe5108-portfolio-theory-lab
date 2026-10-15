# Portfolio Theory in Practice

**FE5108 group project: portfolio choice, CAPM, factor models and investment judgment.**

The main project now uses **30 US stocks**, one per end-2024 text class, selected by **largest December 31, 2024 company market capitalization among members with 108 complete monthly return observations**. This replaces centrality-based stock selection. Stage 1 uses the frozen universe, monthly data, mean vectors, covariance matrices, weights and separate subsample tables. Stages 1–4 are integrated: portfolio choice, CAPM/SML/GRS, FF3 factor analysis and an alternative market-proxy comparison.

## Research design

1. Reuse the existing four-section TF-IDF/SVD → UMAP3 → Leiden classification at end-2024 (representative seed 20260831; 30 classes).
2. Rank each class by historical December 31, 2024 market capitalization. Select its largest member with complete January 2017–December 2025 daily-return coverage. No centrality-rank cutoff is applied.
3. Freeze all 30 securities and compound daily total returns to 108 monthly observations.
4. Estimate monthly arithmetic means, sample covariance and unconstrained tangency weights over 108, 96 and 84 months. Compare with fixed **December 31, 2025** capitalization weights in the same universe.
5. Estimate Stage 2 CAPM regressions on the same 30 stocks and 108 months, using Kenneth French `Mkt-RF` as the market proxy. Compare the empirical SML with theory and assess all alphas jointly with GRS.
6. Add published SMB and HML in Stage 3, then compare the CAPM market proxy with MSCI World in Stage 4. The distance-matrix allocation experiments are separate research, not the Stage 1 weighting formula.

This is a retrospectively constructed course universe. Full-history screening, 2024 classifications applied to earlier returns and retrospective method choices preclude a strict point-in-time investment claim. Historical vendor capitalization is not independently certified; see [selection](docs/03-universe-selection.md) and [endpoint audit](artifacts/stage1/market_cap_audit.md).

## Frozen universe

SHW, AAPL, ABBV, PLD, TMO, SF, VZ, META, SCCO, MSFT, UPS, WMT, PANW, RTX, AFL, ACN, V, EXEL, KO, UNH, WMB, MO, AGNC, CME, SRE, MAR, CMG, TSLA, SLB, DHI.

[Selected companies, cap ranks and coverage](artifacts/results/selected_universe.csv) · [All 30 class representatives](artifacts/results/candidates_30.csv) · [All 1,910 company rankings](artifacts/results/all_company_rankings_2024.csv).

Twenty-three selected stocks are their classes' absolute vendor-cap leaders. Seven classes use the largest complete-history member instead. The selected fallback ranks are 2–4; these are market-cap ranks, not centrality ranks. All 30 have 108 complete months.

## Classification evidence

The underlying classification evidence is unchanged. In the matched 48-group study, lexical four-section TF-IDF/SVD exceeds FF48 on Pearson and empirical lower-tail gaps in seven evaluated years. Native-count TF-IDF/SVD + UMAP3 + Leiden leads the nine studied Leiden routes on next-year Pearson gap in those seven years, and beats the historical-return control in five of six comparable years. Group counts vary; these descriptive results do not prove investment outperformance. The multi-text gain is representation-dependent.

![Native Leiden comparison](artifacts/figures/03_native_leiden_multiyear.png)

[Detailed comparisons and qualifications](docs/02-classification-evidence.md).

## Shared data and Stage 1

- [Monthly total returns](artifacts/monthly/monthly_total_returns.csv): 108 months × 30 stocks, decimals.
- [Monthly excess returns](artifacts/monthly/monthly_excess_returns.csv), [aligned RF](artifacts/monthly/risk_free_monthly.csv), and [security-level long table](artifacts/monthly/monthly_returns_long.csv).
- [Stage 1 report](artifacts/stage1/README.md): full-sample and separate subsample weight tables, mean vectors, full covariance matrices and charts. The 30 × 30 matrices are small enough to remain uncompressed.
- [2024 selection capitalization](artifacts/inputs/formation_market_caps_2024.csv) and [2025 endpoint capitalization](artifacts/input/year_end_market_cap_2025.csv) serve different purposes. Sanitized endpoint detail responses and selected raw closes are versioned.

Daily market panels, raw SEC text and credentials remain local and excluded from Git. The daily input spans September 30, 2016–December 31, 2025, with first finite return October 3, 2016; the project uses the nine full years 2017–2025. See [data processing](docs/01-data.md) and [artifact documentation](artifacts/README.md).

## Stage 2 CAPM and SML

[`scripts/stage2.py`](scripts/stage2.py) reproduces Stage 2 from the shared cached inputs. It requires no notebook, credentials or network access. Run it through the repository entry point so that Stage 1 mean files are generated first.

### Inputs

| File | Use |
|---|---|
| `artifacts/results/selected_universe.csv` | Canonical stock order and company names |
| `artifacts/monthly/monthly_total_returns.csv` | Total returns for unit and Stage 1 consistency checks |
| `artifacts/monthly/monthly_excess_returns.csv` | Dependent variables in the CAPM regressions |
| `artifacts/monthly/risk_free_monthly.csv` | The shared monthly risk-free series |
| `artifacts/inputs/ff3_monthly.csv` | Instructor-provided cached factor file; `Mkt-RF` is the market regressor |
| `artifacts/stage1/means_108m.csv` | Generated Stage 1 means used to check cross-stage consistency |

The sample is January 2017 to December 2025: 108 common monthly observations for all 30 stocks. The factor file is copied from the instructor's `data_bundle/data/ff3_monthly.csv` and its returns are already decimals. Use `Mkt-RF` directly; do not divide it by 100 or subtract RF again. The factor RF column matches the Stage 1 RF series. SMB and HML are available for Stage 3 and do not enter the Stage 2 regression.

The [Kenneth French factor definitions](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html) describe the broad US equity market excess-return proxy. It matches the currency and equity market of the chosen US stock universe, but remains a proxy for the theoretical market portfolio.

### Methods and outputs

For each stock, estimate `Ri - Rf = alpha + beta * (Mkt - Rf) + residual` with an intercept. Baseline alpha inference uses ordinary OLS standard errors and Student t with 106 residual degrees of freedom. A robustness comparison uses HAC with three Bartlett lags, a small-sample covariance correction and approximate Student-t p-values.

All 16 Stage 2 artifacts are saved under `artifacts/stage2/`:

| Files | Content |
|---|---|
| `capm_input_monthly.csv`, `input_checks.json` | Aligned data and source metadata |
| `capm_results.csv`, `capm_summary.csv` | Full CAPM estimates and presentation summary |
| `capm_residuals.csv`, `capm_fitted_values.csv` | Residuals and fitted values for all stocks |
| `data_audit_examples.csv`, `capm_checks.json` | Audit examples and regression method record |
| `sml_scatter.png`, `sml_points.csv`, `sml_lines.csv` | Security Market Line chart and plotting data |
| `sml_summary.csv`, `sml_checks.json` | Theoretical versus fitted intercept and slope, and method record |
| `grs_results.csv`, `grs_residual_covariance.csv`, `grs_checks.json` | Joint alpha test, residual covariance and method record |

Analytical returns and alphas remain monthly decimals in CSVs, except the explicitly named `alpha_monthly_percent` column in `capm_summary.csv`. The SML figure formats returns as percentages. Its fitted line is an equally weighted cross-sectional OLS of mean stock excess returns on estimated betas; the theoretical line passes through the origin with slope equal to mean market excess return.

The classical GRS test uses residual covariance `E.T @ E / T` and market variance with `ddof=0`. For `T=108`, `N=30` and one factor, the reference distribution is `F(30, 77)`. The [GRS paper](https://www2.itc.kansai-u.ac.jp/~koji_ota/GRS_test/GibbonsRossShanken_1989_Econometrica.pdf) gives the finite-sample test under conditionally joint-normal residuals with constant nonsingular covariance and independence across time. The joint test uses classical covariance rather than the HAC covariance from the individual regressions.

The fitted SML has a monthly intercept of 0.2108% and slope of 1.2396%, compared with a theoretical slope of 1.0771%; its cross-sectional R-squared is 0.3164. GRS is 1.1465 with p-value 0.3099, so the joint zero-alpha null is not rejected at 5%. These results do not establish that the CAPM holds. The SML slope and intercept comparisons are descriptive; no formal significance claim is made for their differences. A different market proxy remains part of Stage 4.

## Stage 3 Fama–French factor analysis

[`scripts/stage3.py`](scripts/stage3.py) adds published SMB and HML to the Stage 2 market factor, using the same 30 stocks and 108 months (January 2017–December 2025). It reads the shared cached FF3 file; factors are not constructed from our selected stocks. All returns enter the regressions as monthly decimals.

The program verifies RF alignment and reproduces Stage 2 CAPM alphas, OLS t-statistics and R-squared before comparing CAPM with FF3. It reports OLS inference, HAC(3) alpha inference and a per-stock joint test of SMB/HML loadings. The joint loading test is not an alpha test or an FF3 GRS test.

Absolute alpha falls for 13 of 30 stocks; mean absolute monthly alpha changes from 0.594% to 0.574%. Among the two stocks crossing the descriptive CAPM `|OLS t(alpha)| > 2` screen, MSFT continues to cross it under FF3 while WMT does not. These unadjusted screens do not establish mispricing or prove that the additional factors explain abnormal returns.

See the [Stage 3 report](artifacts/stage3/README.md), [factor definitions](artifacts/stage3/factor_definitions.md), [30-stock comparison table](artifacts/stage3/alpha_comparison.csv), [comparison chart](artifacts/stage3/alpha_comparison.png), [verdict](artifacts/stage3/factor_interpretation.md), and [full estimates](artifacts/stage3/all_30_model_results.csv). `checks.json` records input hashes, sample checks and package versions.

## Stage 4 Investment Judgment

Stage 4 combines an investment recommendation, a market-proxy comparison and an assessment of the result we trust least.

### Investment recommendation

We recommend a constrained allocation between value weighting and the estimated tangency portfolio. The tangency portfolio's higher in-sample Sharpe and stronger 2026 tracking return support retaining active allocations, but leverage, estimation sensitivity and implementation costs limit the case for holding it without constraints. See [the full recommendation](artifacts/stage4/investment_recommendation.md).

### Market-proxy comparison

[`scripts/stage4.py`](scripts/stage4.py) repeats Stage 2 using `excess_net_total_return_decimal` from `artifacts/monthly/msci_world_monthly.csv`, retaining the same 30 stocks, 108 months and estimation methods.

Mean absolute changes are **0.0951 percentage points per month for alpha** and **0.0808 for beta**. AAPL joins MSFT and WMT as having significant alphas at the unadjusted 5% level under both OLS and HAC(3). The GRS p-value falls from **0.3099 to 0.1154**, but neither proxy rejects joint zero alpha at 5%. These results illustrate that CAPM conclusions depend partly on the market proxy, consistent with Roll's critique.

### Result we trust least

We are least confident that the tangency portfolio's in-sample Sharpe of **2.197** represents future achievable performance. Weights were optimized and evaluated on the same sample, while the 2026 tracking evidence retains retrospective-selection and cost limitations. See [the limitations assessment](artifacts/stage4/limitations.md).

### Outputs

Results are saved to `artifacts/stage4/`, including CAPM, SML and GRS outputs. Main comparisons are available in [`alpha_beta_comparison.csv`](artifacts/stage4/alpha_beta_comparison.csv), [`grs_comparison.csv`](artifacts/stage4/grs_comparison.csv) and [`comparison_report.md`](artifacts/stage4/comparison_report.md).

## Analysis guide and assignment mapping

Files use descriptive `snake_case` names. Each stage directory provides context; assignment numbers are a navigation aid rather than file names. Tables use decimal returns unless a column explicitly specifies percent units.

| Analysis | Main outputs | Assignment requirement |
|---|---|---|
| Universe summary | `stage1/summary_statistics.csv` | 1a |
| Tangency versus value weights | `stage1/portfolio_weights.csv`, `stage1/weights_comparison.png` | 1b |
| Estimation sensitivity | `stage1/subsample_stability.csv`, `stage1/subsample_weights.png`, Stage 1 report | 1c |
| CAPM estimates | `stage2/capm_summary.csv`, `stage2/capm_results.csv` | 2a |
| Security Market Line | `stage2/sml_scatter.png`, `stage2/sml_summary.csv` | 2b, 2d |
| Joint alpha assessment | `stage2/grs_results.csv` and interpretation above | 2c |
| Factor definitions | `stage3/factor_definitions.md` | 3a |
| CAPM versus FF3 alphas | `stage3/alpha_comparison.csv`, `stage3/alpha_comparison.png` | 3b |
| Factor interpretation | `stage3/factor_interpretation.md` | 3c |
| Investment recommendation | `stage4/investment_recommendation.md` | Stage 4: recommendation |
| Alternative market proxy | `stage4/comparison_report.md`, `stage4/alpha_beta_comparison.csv`, `stage4/grs_comparison.csv` | Stage 4: Roll's critique |
| Limitations | `stage4/limitations.md` | Stage 4: intellectual honesty |

All paths in this table are relative to `artifacts/`. Stage 4 also saves `capm_summary.csv` using the same naming and units as Stage 2, with MSCI World as the market proxy.

## Reproduce

From the repository root, install the dependencies and regenerate the completed stages:

```bash
python3 -m pip install -r requirements.txt
python3 run_all.py --all
```

`--stage2` automatically runs Stage 1 first, so `python3 run_all.py --stage2` produces the same research, Stage 1 and Stage 2 artifacts. Existing commands remain available:

```bash
python3 run_all.py
python3 run_all.py --stage1
python3 -m unittest discover -s tests -v
```

The default command rebuilds selection and classification-evidence figures. `--stage1` adds portfolio-choice outputs; `--stage2` adds CAPM, SML and GRS. `--stage3` adds the FF3 factor analysis and automatically runs Stage 1 and Stage 2 first. Use `--all` to reproduce all four course stages from cached inputs; `--stage3 --stage4` remains equivalent. `--all` does not require local daily panels or run the separate research-branch experiments. `--stage4` adds the MSCI World market-proxy analysis and comparisons with Stage 2. Outputs are overwritten with the results of the current run. Figures are saved to disk with a noninteractive backend. The existing unit-test suite covers research and Stage 1 components; Stage 2 also retains data and result diagnostics in its execution path.

The pipeline runs offline from the versioned cached inputs. It does not refit upstream text models or recreate vendor daily panels. To rebuild monthly returns from local daily data before running both stages:

```bash
python3 run_all.py --daily-root ./tbic_returns --monthly --stage1 --stage2
```

The daily `tbic_returns` inputs must be supplied locally for this command; they are excluded from Git. The cached monthly inputs suffice to regenerate the Stage 1 and Stage 2 outputs. The historical-cap inputs are frozen, not downloaded by the main program. [Provenance](artifacts/inputs/provenance.json) and generated verification files record hashes. Hashes detect changed inputs and do not independently certify vendor accuracy.

If Stage 1 outputs already exist, Stage 2 can also run directly:

```bash
python3 scripts/stage2.py
```

To reproduce Stage 4 with MSCI World as the market proxy:

```bash
python3 run_all.py --stage4
```

`--stage4` automatically runs Stage 1 and Stage 2 first, then generates the MSCI World CAPM, SML and GRS results and comparisons with Stage 2. Outputs are saved to `artifacts/stage4/`.

If Stage 1 and Stage 2 outputs already exist, Stage 4 can also run directly:

```bash
python3 scripts/stage4.py
```

### Verified environment

The integrated pipeline was verified with Python 3.12.1 and the versions below. Dependency ranges in `requirements.txt` preserve the existing project constraints; statsmodels is pinned to the tested version. Runtime JSON files record the actual packages used for each run.

| Package | Verified version |
|---|---|
| NumPy | 2.4.6 |
| pandas | 3.0.3 |
| PyArrow | 24.0.0 |
| SciPy | 1.18.0 |
| scikit-learn | 1.9.0 |
| Matplotlib | 3.10.9 |
| statsmodels | 0.14.6 |

Stage 3 can also run independently after Stage 2 outputs exist:

```bash
python3 scripts/stage3.py
```

The original `python3 artifacts/stage3/run_stage3.py --repo .` command remains supported as a compatibility wrapper. Neither standalone command rebuilds Stage 2; use `python3 run_all.py --stage3` to refresh its dependencies automatically.

## Project status

| Stage | Status |
|---|---|
| Data and universe | Complete: 30 capitalization-selected representatives |
| Stage 1 | Complete: moments, static weights and subsample sensitivity |
| Stage 2: CAPM | Complete: CAPM table, SML and GRS; integrated into the entry point |
| Stage 3: factors | Complete: CAPM versus FF3, SMB/HML loading tests and alpha comparison; integrated into the entry point |
| Stage 4: investment judgment | Complete: investment recommendation, market-proxy comparison and limitations |

[Next-stage contracts](docs/04-next-steps.md) · [Team contributions](docs/contributions.md).

## Attribution

Upstream text and return research: TBIC / Tuoyuan. Market data: Massive; filings: SEC EDGAR; historical universe proxy: iShares IWV; standard industry control: SIC-based FF48; RF: Kenneth French Data Library. OpenAI Codex assisted with code, auditing, Stage 2 CAPM/SML/GRS implementation, pipeline integration and English documentation. The team remains responsible for interpretation and source limitations. This is a course research project, not investment advice.
