"""Reproduce Stage 2 CAPM, SML and GRS artifacts from the shared cached inputs.

Called by run_all.py --stage2. This module also runs directly as a script.
All output filenames, units and methods follow the final Stage 2 notebook.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
import scipy
from scipy.stats import f as f_distribution
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def read_monthly(path, date_column, expected_months):
    frame = pd.read_csv(path)
    if date_column not in frame.columns:
        raise ValueError(f"{path.name} is missing date column {date_column}")

    months = pd.to_datetime(frame.pop(date_column), errors="raise").dt.to_period("M")
    if months.isna().any():
        raise ValueError(f"{path.name} contains missing dates")
    frame.index = pd.PeriodIndex(months, name="month")
    if not frame.index.is_unique:
        raise ValueError(f"{path.name} contains duplicate months")
    frame = frame.sort_index()

    missing = expected_months.difference(frame.index)
    if len(missing):
        raise ValueError(f"{path.name} is missing sample months: {missing.tolist()}")
    return frame.loc[expected_months].copy()


def _run(root=None):
    ROOT = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[1]

    OUT_DIR = ROOT / "artifacts/stage2"

    FIG_DIR = OUT_DIR

    START_MONTH = "2017-01"

    END_MONTH = "2025-12"

    EXPECTED_MONTHS = pd.period_range(START_MONTH, END_MONTH, freq="M", name="month")

    INPUTS = {
        "universe": ROOT / "artifacts/results/selected_universe.csv",
        "total": ROOT / "artifacts/monthly/monthly_total_returns.csv",
        "excess": ROOT / "artifacts/monthly/monthly_excess_returns.csv",
        "rf": ROOT / "artifacts/monthly/risk_free_monthly.csv",
        "factors": ROOT / "artifacts/inputs/ff3_monthly.csv",
    }

    for name, path in INPUTS.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing input {name}: {path}")

    print("Repository:", ROOT)

    print(f"Sample: {START_MONTH} to {END_MONTH}, {len(EXPECTED_MONTHS)} months")

    universe = pd.read_csv(INPUTS["universe"], dtype={"cik": str, "security_id": str})

    if len(universe) != 30 or not universe["ticker"].is_unique or not universe["security_id"].is_unique:
        raise ValueError("The Stage 1 universe must contain 30 unique tickers and security IDs")

    tickers = universe["ticker"].tolist()

    stock_total = read_monthly(INPUTS["total"], "month", EXPECTED_MONTHS)

    stock_excess = read_monthly(INPUTS["excess"], "month", EXPECTED_MONTHS)

    rf_data = read_monthly(INPUTS["rf"], "month", EXPECTED_MONTHS)

    ff3 = read_monthly(INPUTS["factors"], "Date", EXPECTED_MONTHS)

    for name, frame in {"total": stock_total, "excess": stock_excess}.items():
        if set(frame.columns) != set(tickers):
            raise ValueError(f"{name} stock columns do not match the Stage 1 universe")

    stock_total = stock_total.loc[:, tickers].apply(pd.to_numeric, errors="raise")

    stock_excess = stock_excess.loc[:, tickers].apply(pd.to_numeric, errors="raise")

    ff3 = ff3.loc[:, ["Mkt-RF", "SMB", "HML", "RF", "Rm"]].apply(pd.to_numeric, errors="raise")

    rf = ff3["RF"].rename("rf")

    np.testing.assert_allclose(
        ff3["Rm"].to_numpy(),
        (ff3["Mkt-RF"] + ff3["RF"]).to_numpy(),
        rtol=0, atol=1e-12,
        err_msg="Stored FF3 Rm does not equal Mkt-RF + RF",
    )

    market_excess = ff3["Mkt-RF"].rename("market_excess")

    asset_info = universe.set_index("ticker").loc[tickers, ["company_name", "security_id", "cik", "cluster_label"]].copy()

    for name, values in {
        "stock_total": stock_total,
        "stock_excess": stock_excess,
        "rf": rf,
        "ff3": ff3,
    }.items():
        if not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError(f"{name} contains missing or infinite values")

    if (stock_total < -1).any().any():
        raise ValueError("A stock total return is below -100%")

    np.testing.assert_allclose(
        rf_data["rf_monthly_percent"].to_numpy(dtype=float) / 100,
        rf.to_numpy(), rtol=0, atol=1e-12,
        err_msg="Repository RF percentage and decimal columns are inconsistent",
    )

    np.testing.assert_allclose(
        rf_data["rf_monthly_decimal"].to_numpy(dtype=float), rf.to_numpy(), rtol=0, atol=1e-12,
        err_msg="Stage 1 RF does not match canonical FF3 RF; check sources and units",
    )

    np.testing.assert_allclose(
        stock_excess.to_numpy(), stock_total.sub(rf, axis=0).to_numpy(),
        rtol=0, atol=1e-12,
        err_msg="Stage 1 excess returns do not equal total returns minus RF",
    )

    # Stage 1 cached values are checked above; actual Stage 2 RF comes from FF3.
    stock_excess = stock_total.sub(rf, axis=0)
    capm_data = stock_excess.join(market_excess, how="left", validate="one_to_one")

    capm_data = capm_data.join(rf, how="left", validate="one_to_one")

    if not capm_data.index.equals(EXPECTED_MONTHS) or capm_data.shape != (len(EXPECTED_MONTHS), 32):
        raise ValueError("Merged sample months or column count do not match the expected input")

    if not np.isfinite(capm_data.to_numpy()).all():
        raise ValueError("Merged data contain missing or infinite values")

    if market_excess.var() <= 0:
        raise ValueError("Market excess returns must have nonzero sample variance")

    Y = capm_data.loc[:, tickers].copy()

    market = capm_data["market_excess"].copy()

    print("Stock excess returns Y:", Y.shape)

    print("Market excess returns market:", market.shape)

    print("Merged data capm_data:", capm_data.shape)

    print("Input validation passed. Returns and RF are monthly decimals.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    capm_data.to_csv(OUT_DIR / "capm_input_monthly.csv", index_label="month")

    input_checks = {
        "module": "stage2_data_preparation",
        "sample_start": START_MONTH,
        "sample_end": END_MONTH,
        "months": len(capm_data),
        "assets": len(tickers),
        "tickers": tickers,
        "units": "monthly decimals",
        "market_proxy": "Kenneth French US market excess return, Mkt-RF",
        "factor_source": "Instructor fallback data_bundle/data/ff3_monthly.csv",
        "risk_free_source": "artifacts/inputs/ff3_monthly.csv: RF",
        "stored_market_return": "FF3 Rm = Mkt-RF + RF; validated, not an extra regressor",
        "stage1_rf_role": "Consistency check only; not the Stage 2 RF calculation source",
        "rf_matches_stage1": True,
        "excess_matches_total_minus_rf": True,
        "missing_values": int(capm_data.isna().sum().sum()),
        "inputs_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in INPUTS.values()
        },
        "packages": {"numpy": np.__version__, "pandas": pd.__version__},
    }

    (OUT_DIR / "input_checks.json").write_text(
        json.dumps(input_checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Saved:", OUT_DIR / "capm_input_monthly.csv")

    print("Saved:", OUT_DIR / "input_checks.json")

    recorded_inputs = input_checks

    stage1_means = pd.read_csv(
        ROOT / "artifacts/stage1/means_108m.csv", index_col="ticker"
    ).loc[tickers]

    np.testing.assert_allclose(
        stock_total.mean().to_numpy(), stage1_means["mean_monthly_return"].to_numpy(),
        rtol=0, atol=1e-12,
    )

    np.testing.assert_allclose(
        Y.mean().to_numpy(), stage1_means["mean_monthly_excess_return"].to_numpy(),
        rtol=0, atol=1e-12,
    )

    rows = []

    for month_text in ["2017-01", "2020-03", "2025-12"]:
        month = pd.Period(month_text, freq="M")
        for ticker in ["AAPL", "MSFT", "TSLA", "VZ"]:
            total = float(stock_total.loc[month, ticker])
            risk_free = float(rf.loc[month])
            excess = float(Y.loc[month, ticker])
            rows.append({
                "month": str(month), "ticker": ticker,
                "total_return": total, "rf": risk_free,
                "stored_excess": excess, "recomputed_excess": total - risk_free,
                "difference": excess - (total - risk_free),
            })

    audit_examples = pd.DataFrame(rows)

    print("Stage 1 mean consistency checks passed. Audit differences should be near zero.")

    HAC_LAGS = 3

    X = sm.add_constant(market.rename("market_excess").to_frame(), has_constant="add")

    if np.linalg.matrix_rank(X.to_numpy()) != 2:
        raise ValueError("The design matrix is not full rank; check whether market returns are constant")

    print("X:", X.shape, "columns:", X.columns.tolist())

    print("statsmodels:", statsmodels.__version__)

    capm_models = {}

    capm_residuals = pd.DataFrame(index=Y.index, columns=tickers, dtype=float)

    capm_fitted = pd.DataFrame(index=Y.index, columns=tickers, dtype=float)

    rows = []

    for ticker in tickers:
        model = sm.OLS(Y[ticker], X, missing="raise").fit(use_t=True)
        hac = model.get_robustcov_results(
            cov_type="HAC", maxlags=HAC_LAGS, kernel="bartlett",
            use_correction=True, use_t=True,
        )
        # Restore parameter labels on the arrays returned by the robust covariance result.
        hac_se = pd.Series(hac.bse, index=X.columns)
        hac_t = pd.Series(hac.tvalues, index=X.columns)
        hac_p = pd.Series(hac.pvalues, index=X.columns)

        capm_models[ticker] = model
        capm_residuals[ticker] = model.resid
        capm_fitted[ticker] = model.fittedvalues
        rows.append({
            "ticker": ticker,
            "n_obs": int(model.nobs),
            "alpha_monthly": float(model.params["const"]),
            "beta": float(model.params["market_excess"]),
            "alpha_se_ols": float(model.bse["const"]),
            "alpha_t_ols": float(model.tvalues["const"]),
            "alpha_p_ols": float(model.pvalues["const"]),
            "beta_se_ols": float(model.bse["market_excess"]),
            "alpha_se_hac3": float(hac_se["const"]),
            "alpha_t_hac3": float(hac_t["const"]),
            "alpha_p_hac3": float(hac_p["const"]),
            "r_squared": float(model.rsquared),
            "mean_excess_monthly": float(Y[ticker].mean()),
        })

    capm_results = pd.DataFrame(rows).set_index("ticker")

    capm_results = capm_results.join(asset_info[["company_name"]], validate="one_to_one").loc[tickers]

    exhibit_2a = capm_results[[
        "company_name", "beta", "alpha_monthly", "alpha_t_ols", "alpha_t_hac3", "r_squared"
    ]].copy()

    exhibit_2a["alpha_monthly"] *= 100

    exhibit_2a = exhibit_2a.rename(columns={"alpha_monthly": "alpha_monthly_percent"})

    print(f"Completed CAPM regressions for {len(capm_results)} stocks; raw alphas remain monthly decimals.")

    np.testing.assert_allclose(Y.to_numpy(), (capm_fitted + capm_residuals).to_numpy(), rtol=0, atol=1e-12)

    np.testing.assert_allclose(capm_residuals.mean().to_numpy(), 0, rtol=0, atol=1e-12)

    np.testing.assert_allclose(X.to_numpy().T @ capm_residuals.to_numpy(), 0, rtol=0, atol=1e-10)

    np.testing.assert_allclose(
        Y.mean().to_numpy(),
        (capm_results["alpha_monthly"] + capm_results["beta"] * market.mean()).to_numpy(),
        rtol=0, atol=1e-12,
    )

    if not capm_results["n_obs"].eq(108).all():
        raise ValueError("At least one regression does not use all 108 months")

    if not np.isfinite(capm_results.select_dtypes(include="number").to_numpy()).all():
        raise ValueError("Regression results contain missing or infinite values")

    print("Result diagnostics passed: return reconstruction, residual means, residual orthogonality and the SML mean identity.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    capm_results.to_csv(OUT_DIR / "capm_results.csv", index_label="ticker")

    exhibit_2a.to_csv(OUT_DIR / "exhibit_2a.csv", index_label="ticker")

    capm_residuals.to_csv(OUT_DIR / "capm_residuals.csv", index_label="month")

    capm_fitted.to_csv(OUT_DIR / "capm_fitted_values.csv", index_label="month")

    audit_examples.to_csv(OUT_DIR / "data_audit_examples.csv", index=False)

    capm_checks = {
        "model": "Ri_minus_Rf = alpha + beta * Mkt_minus_Rf + residual",
        "sample_start": str(Y.index[0]), "sample_end": str(Y.index[-1]),
        "months": len(Y), "assets": len(tickers), "tickers": tickers,
        "alpha_units": "monthly decimals; exhibit_2a.csv uses monthly percent",
        "standard_errors_baseline": "OLS nonrobust, Student t, df = T - 2",
        "standard_errors_robustness": {
            "method": "HAC", "maxlags": HAC_LAGS, "kernel": "bartlett",
            "use_correction": True, "use_t": True,
            "note": "HAC t-distribution p-values are an approximation, not exact finite-sample inference",
        },
        "checks_passed": [
            "FF3_Rm_identity", "stage1_mean_consistency", "Y_equals_fitted_plus_residual",
            "zero_residual_mean", "residual_orthogonality", "SML_mean_identity",
        ],
        "inputs_sha256": recorded_inputs["inputs_sha256"],
        "stage1_means_sha256": hashlib.sha256(
            (ROOT / "artifacts/stage1/means_108m.csv").read_bytes()
        ).hexdigest(),
        "packages": {
            "numpy": np.__version__, "pandas": pd.__version__,
            "statsmodels": statsmodels.__version__,
        },
    }

    (OUT_DIR / "capm_checks.json").write_text(
        json.dumps(capm_checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Saved CAPM results, exhibit, residuals, fitted values, audit table and method record to:", OUT_DIR)

    market_premium = float(market.mean())

    sml_points = capm_results[[
        "company_name", "beta", "alpha_monthly", "alpha_p_hac3"
    ]].copy()

    sml_points["mean_excess_monthly"] = Y.mean().reindex(tickers)

    sml_points["theoretical_excess_monthly"] = sml_points["beta"] * market_premium

    sml_points["deviation_from_theory"] = (
        sml_points["mean_excess_monthly"] - sml_points["theoretical_excess_monthly"]
    )

    if not np.isfinite(sml_points.select_dtypes(include="number").to_numpy()).all():
        raise ValueError("SML inputs contain missing or infinite values")

    np.testing.assert_allclose(
        sml_points["deviation_from_theory"], sml_points["alpha_monthly"],
        rtol=0, atol=1e-12,
    )

    print(f"SML points: {len(sml_points)}; mean monthly market excess return: {market_premium:.4%}")

    X_sml = sm.add_constant(sml_points[["beta"]], has_constant="add")

    if np.linalg.matrix_rank(X_sml.to_numpy()) != 2:
        raise ValueError("Stock betas must vary across assets to fit the SML")

    sml_model = sm.OLS(
        sml_points["mean_excess_monthly"], X_sml, missing="raise"
    ).fit()

    gamma0 = float(sml_model.params["const"])

    gamma1 = float(sml_model.params["beta"])

    sml_points["fitted_excess_monthly"] = sml_model.fittedvalues

    sml_points["cross_sectional_residual"] = sml_model.resid

    np.testing.assert_allclose(sml_points["cross_sectional_residual"].mean(), 0, rtol=0, atol=1e-12)

    sml_summary = pd.DataFrame({
        "quantity": ["intercept", "slope"],
        "theory_monthly_decimal": [0.0, market_premium],
        "empirical_monthly_decimal": [gamma0, gamma1],
        "difference_monthly_decimal": [gamma0, gamma1 - market_premium],
    }).set_index("quantity")

    summary_display = sml_summary.mul(100).rename(columns={
        "theory_monthly_decimal": "theory_monthly_percent",
        "empirical_monthly_decimal": "empirical_monthly_percent",
        "difference_monthly_decimal": "difference_percentage_points",
    })

    print(f"Empirical SML: mean monthly excess return = {gamma0:.6f} + {gamma1:.6f} × beta")

    print(f"Theoretical SML: mean monthly excess return = {market_premium:.6f} × beta")

    print(f"Cross-sectional R-squared:{sml_model.rsquared:.4f}")

    beta_min = min(0.0, float(sml_points["beta"].min()) - 0.10)

    beta_max = max(0.0, float(sml_points["beta"].max()) + 0.15)

    beta_grid = np.linspace(beta_min, beta_max, 300)

    sml_lines = pd.DataFrame({
        "beta": beta_grid,
        "theoretical_excess_monthly": market_premium * beta_grid,
        "fitted_excess_monthly": gamma0 + gamma1 * beta_grid,
    })

    sml_fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        sml_points["beta"], sml_points["mean_excess_monthly"],
        s=48, color="#2563eb", alpha=0.85, edgecolors="white",
        linewidths=0.6, label="30 stocks", zorder=3,
    )

    ax.plot(
        beta_grid, sml_lines["theoretical_excess_monthly"],
        color="#111827", linestyle="--", linewidth=2,
        label="CAPM theoretical SML", zorder=2,
    )

    ax.plot(
        beta_grid, sml_lines["fitted_excess_monthly"],
        color="#dc2626", linewidth=2,
        label="Empirical SML: equal-weight OLS", zorder=2,
    )

    label_tickers = list(dict.fromkeys(
        sml_points["alpha_monthly"].abs().nlargest(3).index.tolist()
        + sml_points.index[sml_points["alpha_p_hac3"] < 0.05].tolist()
    ))

    for ticker in label_tickers:
        row = sml_points.loc[ticker]
        ax.annotate(
            ticker, xy=(row["beta"], row["mean_excess_monthly"]),
            xytext=(7, 8), textcoords="offset points", fontsize=9,
        )

    ax.axhline(0, color="#9ca3af", linewidth=0.7)

    ax.set_xlim(beta_min - 0.05, beta_max)

    ax.set_xlabel("Estimated CAPM beta")

    ax.set_ylabel("Average monthly excess return")

    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))

    ax.set_title("Exhibit 2b — Empirical Security Market Line")

    ax.grid(alpha=0.18)

    ax.spines[["top", "right"]].set_visible(False)

    ax.legend(loc="upper left", frameon=False)

    caption = (
        f"2017-01 to 2025-12 | 108 months | Market proxy: Kenneth French Mkt-RF\n"
        f"Fitted slope: {gamma1:.2%} vs theory: {market_premium:.2%}; "
        f"fitted intercept: {gamma0:.2%} per month."
    )

    sml_fig.subplots_adjust(bottom=0.20)

    sml_fig.text(0.12, 0.035, caption, fontsize=9, color="#374151", va="bottom")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sml_fig.savefig(OUT_DIR / "sml_scatter.png", dpi=300, bbox_inches="tight")

    plt.close(sml_fig)

    print("Saved:", OUT_DIR / "sml_scatter.png")

    sml_points.to_csv(OUT_DIR / "sml_points.csv", index_label="ticker")

    sml_summary.to_csv(OUT_DIR / "sml_summary.csv", index_label="quantity")

    sml_lines.to_csv(OUT_DIR / "sml_lines.csv", index=False)

    sml_checks = {
        "sample_start": str(Y.index[0]), "sample_end": str(Y.index[-1]),
        "months": len(Y), "assets": len(tickers), "tickers": tickers,
        "market_proxy": "Kenneth French Mkt-RF",
        "units": "monthly decimals in CSVs; percentage labels in figure",
        "empirical_method": "Equal-weight cross-sectional OLS with intercept",
        "theoretical_intercept": 0.0,
        "theoretical_slope": market_premium,
        "empirical_intercept": gamma0,
        "empirical_slope": gamma1,
        "slope_minus_theory": gamma1 - market_premium,
        "cross_sectional_r_squared": float(sml_model.rsquared),
        "observed_beta_range": [float(sml_points.beta.min()), float(sml_points.beta.max())],
        "labelled_tickers": label_tickers,
        "checks_passed": ["common_sample", "alpha_equals_theory_deviation", "zero_cross_sectional_residual_mean"],
        "interpretation": "Descriptive SML; estimated beta and cross-asset dependence prevent treating ordinary cross-sectional p-values as a formal CAPM pricing test. The intercept at beta=0 can be an extrapolation.",
        "inputs_sha256": {
            name: hashlib.sha256((OUT_DIR / name).read_bytes()).hexdigest()
            for name in ["capm_results.csv", "capm_input_monthly.csv"]
        },
        "packages": {
            "numpy": np.__version__, "pandas": pd.__version__,
            "statsmodels": statsmodels.__version__, "matplotlib": matplotlib.__version__,
        },
    }

    (OUT_DIR / "sml_checks.json").write_text(
        json.dumps(sml_checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Saved SML points, line data, slope/intercept comparison and method record to:", OUT_DIR)

    grs_T, grs_N = Y.shape

    grs_K = 1

    if grs_T <= grs_N + grs_K:
        raise ValueError("GRS requires T > N + K")

    grs_alpha = capm_results["alpha_monthly"].to_numpy(dtype=float)

    grs_E = capm_residuals.to_numpy(dtype=float)

    grs_market = market.to_numpy(dtype=float)

    print(f"GRS sample: T={grs_T}, N={grs_N}, K={grs_K}")

    print(
        "Null hypothesis: all 30 CAPM alphas equal zero; "
        f"F degrees of freedom=({grs_N}, {grs_T-grs_N-grs_K})"
    )

    GRS_LEVEL = 0.05

    grs_sigma = (grs_E.T @ grs_E) / grs_T

    grs_market_mean = float(grs_market.mean())

    grs_market_var = float(grs_market.var(ddof=0))

    if grs_market_var <= 0:
        raise ValueError("Market excess-return variance must be positive")

    try:
        np.linalg.cholesky(grs_sigma)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Residual covariance is not positive definite; the classical GRS test cannot be computed") from exc

    grs_quadratic = float(grs_alpha @ np.linalg.solve(grs_sigma, grs_alpha))

    grs_market_sharpe_sq = grs_market_mean**2 / grs_market_var

    grs_df1 = grs_N

    grs_df2 = grs_T - grs_N - grs_K

    grs_stat = (grs_df2 / grs_df1) * grs_quadratic / (1 + grs_market_sharpe_sq)

    grs_pvalue = float(f_distribution.sf(grs_stat, grs_df1, grs_df2))

    grs_critical = float(f_distribution.isf(GRS_LEVEL, grs_df1, grs_df2))

    if not np.isfinite([grs_stat, grs_pvalue, grs_critical]).all() or grs_stat < 0:
        raise ValueError("The GRS result contains an invalid value")

    grs_reject = bool(grs_pvalue < GRS_LEVEL)

    grs_results = pd.DataFrame([{
        "sample_start": str(Y.index[0]), "sample_end": str(Y.index[-1]),
        "months": grs_T, "assets": grs_N, "factors": grs_K,
        "grs_statistic": float(grs_stat), "df1": grs_df1, "df2": grs_df2,
        "p_value": grs_pvalue, "significance_level": GRS_LEVEL,
        "critical_value": grs_critical, "reject_joint_zero_alpha": grs_reject,
    }])

    print(f"GRS F({grs_df1}, {grs_df2}) = {grs_stat:.6f}")

    print(f"p-value = {grs_pvalue:.6g}; 5% critical value = {grs_critical:.6f}")

    print("Conclusion: " + (
        "Reject the joint zero-alpha null at the 5% significance level."
        if grs_reject else
        "Do not reject the joint zero-alpha null at the 5% significance level; this does not prove that the CAPM holds."
    ))

    grs_source_files = [OUT_DIR / name for name in [
        "capm_input_monthly.csv", "capm_results.csv", "capm_residuals.csv", "capm_checks.json"
    ]]

    grs_checks = {
        "test": "Classical Gibbons-Ross-Shanken joint alpha test",
        "null_hypothesis": "All 30 CAPM intercepts equal zero",
        "market_proxy": "Kenneth French Mkt-RF",
        "tickers": tickers,
        "result": grs_results.iloc[0].to_dict(),
        "residual_covariance": "E.T @ E / T",
        "market_variance": "Variance of market excess returns with ddof=0",
        "formula": "(T-N-K)/N * (alpha.T @ solve(Sigma_e, alpha)) / (1 + mean_market**2 / var_market)",
        "residual_covariance_condition_number": float(np.linalg.cond(grs_sigma)),
        "checks_passed": [
            "common_sample_and_asset_order", "valid_F_degrees_of_freedom",
            "positive_definite_residual_covariance", "finite_GRS_result",
        ],
        "assumptions": "Conditionally joint-normal residuals, constant nonsingular covariance, and independence across time",
        "inference_note": "Classical finite-sample F reference; this test does not use HAC covariance",
        "inputs_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in grs_source_files
        },
        "packages": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    grs_results.to_csv(OUT_DIR / "grs_results.csv", index=False)

    pd.DataFrame(grs_sigma, index=tickers, columns=tickers).to_csv(
        OUT_DIR / "grs_residual_covariance.csv", index_label="ticker"
    )

    (OUT_DIR / "grs_checks.json").write_text(
        json.dumps(grs_checks, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("Saved GRS results, residual covariance and method record to:", OUT_DIR)

    return {
        "capm_results": capm_results,
        "sml_summary": sml_summary,
        "grs_results": grs_results,
    }


def run(root=None):
    """Build all 16 Stage 2 artifacts; require cached Stage 1 inputs and means."""
    # Isolate plotting defaults from styles set by earlier pipeline stages.
    with matplotlib.rc_context():
        matplotlib.rcdefaults()
        return _run(root)


if __name__ == "__main__":
    run()
