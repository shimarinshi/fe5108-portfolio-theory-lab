# Portfolio Theory in Practice

**FE5108 group project: portfolio choice, CAPM, factor models and investment judgment.**

The main project now uses **30 US stocks**, one per end-2024 text class, selected by **largest December 31, 2024 company market capitalization among members with 108 complete monthly return observations**. This replaces centrality-based stock selection. Stage 1 uses the frozen universe, monthly data, mean vectors, covariance matrices, weights and separate subsample tables. Stage 2 is complete: CAPM regressions, the empirical and theoretical Security Market Lines, and the GRS joint alpha test.

## Research design

1. Reuse the existing four-section TF-IDF/SVD → UMAP3 → Leiden classification at end-2024 (representative seed 20260831; 30 classes).
2. Rank each class by historical December 31, 2024 market capitalization. Select its largest member with complete January 2017–December 2025 daily-return coverage. No centrality-rank cutoff is applied.
3. Freeze all 30 securities and compound daily total returns to 108 monthly observations.
4. Estimate monthly arithmetic means, sample covariance and unconstrained tangency weights over 108, 96 and 84 months. Compare with fixed **December 31, 2025** capitalization weights in the same universe.
5. Estimate Stage 2 CAPM regressions on the same 30 stocks and 108 months, using Kenneth French `Mkt-RF` as the market proxy. Compare the empirical SML with theory and assess all alphas jointly with GRS.
6. Extend the analysis with additional factors and a different market proxy in Stages 3 and 4. The distance-matrix allocation experiments are separate research, not the Stage 1 weighting formula.

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
| `capm_results.csv`, `exhibit_2a.csv` | Full CAPM results and Exhibit 2a |
| `capm_residuals.csv`, `capm_fitted_values.csv` | Residuals and fitted values for all stocks |
| `data_audit_examples.csv`, `capm_checks.json` | Audit examples and regression method record |
| `sml_scatter.png`, `sml_points.csv`, `sml_lines.csv` | Exhibit 2b and the data used to draw it |
| `sml_summary.csv`, `sml_checks.json` | Theoretical versus fitted intercept and slope, and method record |
| `grs_results.csv`, `grs_residual_covariance.csv`, `grs_checks.json` | Joint alpha test, residual covariance and method record |

Analytical returns and alphas remain monthly decimals in CSVs, except the explicitly named `alpha_monthly_percent` column in `exhibit_2a.csv`. The SML figure formats returns as percentages. Its fitted line is an equally weighted cross-sectional OLS of mean stock excess returns on estimated betas; the theoretical line passes through the origin with slope equal to mean market excess return.

The classical GRS test uses residual covariance `E.T @ E / T` and market variance with `ddof=0`. For `T=108`, `N=30` and one factor, the reference distribution is `F(30, 77)`. The [GRS paper](https://www2.itc.kansai-u.ac.jp/~koji_ota/GRS_test/GibbonsRossShanken_1989_Econometrica.pdf) gives the finite-sample test under conditionally joint-normal residuals with constant nonsingular covariance and independence across time. The joint test uses classical covariance rather than the HAC covariance from the individual regressions.

The fitted SML has a monthly intercept of 0.2108% and slope of 1.2396%, compared with a theoretical slope of 1.0771%; its cross-sectional R-squared is 0.3164. GRS is 1.1465 with p-value 0.3099, so the joint zero-alpha null is not rejected at 5%. These results do not establish that the CAPM holds. The SML slope and intercept comparisons are descriptive; no formal significance claim is made for their differences. A different market proxy remains part of Stage 4.

## Reproduce

From the repository root, install the dependencies and regenerate the completed stages:

```bash
python3 -m pip install -r requirements.txt
python3 run_all.py --stage1 --stage2
```

`--stage2` automatically runs Stage 1 first, so `python3 run_all.py --stage2` produces the same research, Stage 1 and Stage 2 artifacts. Existing commands remain available:

```bash
python3 run_all.py
python3 run_all.py --stage1
python3 -m unittest discover -s tests -v
```

The default command rebuilds selection and classification-evidence figures. `--stage1` adds portfolio-choice exhibits; `--stage2` adds CAPM, SML and GRS. `--stage4` adds the MSCI World market-proxy analysis and comparisons with Stage 2. Outputs are overwritten with the results of the current run. Figures are saved to disk with a noninteractive backend. The existing unit-test suite covers research and Stage 1 components; Stage 2 also retains data and result diagnostics in its execution path.

The pipeline runs offline from the versioned cached inputs. It does not refit upstream text models or recreate vendor daily panels. To rebuild monthly returns from local daily data before running both stages:

```bash
python3 run_all.py --daily-root ./tbic_returns --monthly --stage1 --stage2
```

The daily `tbic_returns` inputs must be supplied locally for this command; they are excluded from Git. The cached monthly inputs suffice to regenerate the Stage 1 and Stage 2 exhibits. The historical-cap inputs are frozen, not downloaded by the main program. [Provenance](artifacts/inputs/provenance.json) and generated verification files record hashes. Hashes detect changed inputs and do not independently certify vendor accuracy.

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

## Project status

| Stage | Status |
|---|---|
| Data and universe | Complete: 30 capitalization-selected representatives |
| Stage 1 | Complete: moments, static weights and subsample sensitivity |
| Stage 2: CAPM | Complete: CAPM table, SML and GRS; integrated into the entry point |
| Stage 3: factors | Planned; supply at least two additional factors |
| Stage 4: investment judgment | Complete: investment recommendation, market-proxy comparison and limitations |

[Next-stage contracts](docs/04-next-steps.md) · [Team contributions](docs/contributions.md).

## Attribution

Upstream text and return research: TBIC / Tuoyuan. Market data: Massive; filings: SEC EDGAR; historical universe proxy: iShares IWV; standard industry control: SIC-based FF48; RF: Kenneth French Data Library. OpenAI Codex assisted with code, auditing, Stage 2 CAPM/SML/GRS implementation, pipeline integration and English documentation. The team remains responsible for interpretation and source limitations. This is a course research project, not investment advice.
