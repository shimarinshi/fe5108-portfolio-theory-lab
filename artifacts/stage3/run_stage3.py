"""FE5108 Track A Stage 3: explain the same 30 stocks with published FF3 factors.

This is an in-sample asset-pricing regression, not a trading backtest.  It
reads the group's cached inputs, leaves the repository untouched, and writes
the three required Stage 3 exhibits into --out.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm


# 1. 固定与 Stage 2 相同的股票回归区间；因子原文件可以有更多月份。
MONTHS = pd.period_range("2017-01", "2025-12", freq="M", name="month")


def read_monthly(path: Path, date_column: str) -> pd.DataFrame:
    """按月份键对齐，并拒绝重复月份、缺失月份和错误日期。"""
    frame = pd.read_csv(path)
    if date_column not in frame:
        raise ValueError(f"{path}: missing date column {date_column}")
    dates = pd.to_datetime(frame.pop(date_column), errors="raise").dt.to_period("M")
    if dates.isna().any():
        raise ValueError(f"{path}: null month")
    frame.index = pd.PeriodIndex(dates, name="month")
    if not frame.index.is_unique:
        raise ValueError(f"{path}: duplicate month")
    missing = MONTHS.difference(frame.index)
    if len(missing):
        raise ValueError(f"{path}: missing months {missing.tolist()}")
    return frame.loc[MONTHS].copy()


def load_inputs(repo: Path):
    """2. 读取 30 股收益、RF 和外部已发布因子，审计口径及样本一致性。"""
    paths = {
        "universe": repo / "artifacts/results/selected_universe.csv",
        "total": repo / "artifacts/monthly/monthly_total_returns.csv",
        "excess": repo / "artifacts/monthly/monthly_excess_returns.csv",
        "rf": repo / "artifacts/monthly/risk_free_monthly.csv",
        "ff3": repo / "artifacts/inputs/ff3_monthly.csv",
        "stage2": repo / "artifacts/stage2/capm_results.csv",
        "grs": repo / "artifacts/stage2/grs_results.csv",
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)

    universe = pd.read_csv(paths["universe"])
    tickers = universe["ticker"].tolist()
    if len(tickers) != 30 or len(set(tickers)) != 30:
        raise ValueError("Expected exactly 30 distinct Stage 1 stocks")
    names = universe.set_index("ticker").loc[tickers, "company_name"]

    total = read_monthly(paths["total"], "month")
    excess = read_monthly(paths["excess"], "month")
    for label, stock_frame in (("total", total), ("excess", excess)):
        if set(stock_frame.columns) != set(tickers):
            raise ValueError(f"{label}: stock columns differ from selected universe")
    total = total[tickers].apply(pd.to_numeric, errors="raise")
    excess = excess[tickers].apply(pd.to_numeric, errors="raise")

    rf = pd.to_numeric(
        read_monthly(paths["rf"], "month")["rf_monthly_decimal"], errors="raise"
    )
    ff3 = read_monthly(paths["ff3"], "Date")[
        ["Mkt-RF", "SMB", "HML", "RF"]
    ].apply(pd.to_numeric, errors="raise")
    for label, values in (("total", total), ("excess", excess), ("rf", rf), ("ff3", ff3)):
        if not np.isfinite(np.asarray(values, dtype=float)).all():
            raise ValueError(f"{label}: missing or nonfinite values")

    # 股票超额收益已经扣过 RF；Mkt-RF 也已经是超额收益，不能再扣一次。
    np.testing.assert_allclose(excess.to_numpy(), total.sub(rf, axis=0).to_numpy(),
                               rtol=0, atol=1e-10, err_msg="stock excess-return units differ")
    np.testing.assert_allclose(ff3["RF"], rf, rtol=0, atol=1e-12,
                               err_msg="factor RF differs from stock RF")

    stage2 = pd.read_csv(paths["stage2"], index_col="ticker")
    if len(stage2) != 30 or set(stage2.index) != set(tickers):
        raise ValueError("Stage 2 results do not cover the same 30 stocks")
    stage2 = stage2.loc[tickers]
    if not stage2["n_obs"].eq(len(MONTHS)).all():
        raise ValueError("Stage 2 sample length differs")
    grs = pd.read_csv(paths["grs"])
    if len(grs) != 1 or int(grs.loc[0, "months"]) != 108 or int(grs.loc[0, "assets"]) != 30:
        raise ValueError("Stage 2 GRS result uses a different sample")
    return paths, tickers, names, excess, ff3, stage2, float(grs.loc[0, "p_value"])


def fit_models(tickers, names, excess, ff3, stage2):
    """3. 每只股票分别拟合 CAPM 与 CAPM+SMB+HML；比较同一样本的 alpha。"""
    capm_x = sm.add_constant(ff3[["Mkt-RF"]], has_constant="add")
    ff3_x = sm.add_constant(ff3[["Mkt-RF", "SMB", "HML"]], has_constant="add")
    if np.linalg.matrix_rank(ff3_x.to_numpy()) != 4:
        raise ValueError("Market, SMB and HML are linearly dependent")

    rows = []
    for ticker in tickers:
        y = excess[ticker]
        capm = sm.OLS(y, capm_x, missing="raise").fit(use_t=True)
        expanded = sm.OLS(y, ff3_x, missing="raise").fit(use_t=True)
        hac = expanded.get_robustcov_results(
            cov_type="HAC", maxlags=3, kernel="bartlett", use_correction=True, use_t=True
        )
        np.testing.assert_allclose(
            [capm.params["const"], capm.tvalues["const"], capm.rsquared],
            stage2.loc[ticker, ["alpha_monthly", "alpha_t_ols", "r_squared"]].to_numpy(float),
            rtol=0, atol=1e-10, err_msg=f"CAPM baseline changed: {ticker}",
        )
        _, factor_p, _ = expanded.compare_f_test(capm)
        rows.append({
            "ticker": ticker, "company_name": names.loc[ticker], "n_months": int(expanded.nobs),
            "capm_alpha_monthly": capm.params["const"],
            "capm_alpha_t": capm.tvalues["const"], "capm_alpha_p": capm.pvalues["const"],
            "ff3_alpha_monthly": expanded.params["const"],
            "ff3_alpha_t": expanded.tvalues["const"], "ff3_alpha_p": expanded.pvalues["const"],
            "ff3_alpha_t_hac3": hac.tvalues[0], "ff3_alpha_p_hac3": hac.pvalues[0],
            "beta_market": expanded.params["Mkt-RF"],
            "beta_smb": expanded.params["SMB"], "beta_hml": expanded.params["HML"],
            "smb_p": expanded.pvalues["SMB"], "hml_p": expanded.pvalues["HML"],
            "joint_smb_hml_p": factor_p,
            "capm_adjusted_r2": capm.rsquared_adj,
            "ff3_adjusted_r2": expanded.rsquared_adj,
        })
    result = pd.DataFrame(rows).set_index("ticker")
    if len(result) != 30 or not result.n_months.eq(108).all():
        raise ValueError("Regressions did not retain the full common sample")
    return result


def write_exhibits(out: Path, result: pd.DataFrame, grs_p: float):
    """4. 生成手册所需 3a 因子说明、3b 对比表/图、3c 异常判断。"""
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "all_30_model_results.csv", index_label="ticker")

    (out / "exhibit_3a_factor_construction.md").write_text(
        """# Exhibit 3a — Factor construction and source

**Market excess return.** The existing Stage 2 market proxy is the monthly return on the broad US equity market minus the one-month risk-free rate. Each stock's dependent variable is its monthly total return minus the same RF. The cached factor file is already in decimal monthly returns; no second RF subtraction or percent conversion is performed.

**SMB (size).** The published Fama–French three-factor SMB is the average monthly return on the three small size/book-to-market portfolios minus the average on the three big portfolios. The portfolios are formed using prior accounting and market-cap data; SMB is a portfolio *return spread*, not the market cap of any of our 30 stocks. A stock's SMB loading measures its return co-movement with that spread.

**HML (value).** The published HML is the average monthly return on the small- and big-stock high book-to-market portfolios minus the average on the corresponding low book-to-market portfolios. It is likewise a return spread, not an individual stock's book-to-market ratio. A stock's HML loading measures its co-movement with the value spread.

**Data provenance.** All three factor-return columns are read from the group's instructor-supplied `artifacts/inputs/ff3_monthly.csv`, which the group README identifies as cached Ken French US factors. We use published factors; we do not reconstruct SMB/HML from the 30 test stocks. Construction reference: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html. The regression window is January 2017–December 2025, 108 months.
""", encoding="utf-8")

    table = result[["company_name", "n_months", "capm_alpha_monthly", "capm_alpha_t",
                    "ff3_alpha_monthly", "ff3_alpha_t", "ff3_alpha_t_hac3",
                    "beta_smb", "beta_hml", "joint_smb_hml_p"]].copy()
    for col in ("capm_alpha_monthly", "ff3_alpha_monthly"):
        table[col.replace("monthly", "percent_per_month")] = 100 * table.pop(col)
    table.to_csv(out / "exhibit_3b_alpha_before_after.csv", index_label="ticker")

    # 30 股逐行显示；零线用于辨认 alpha 方向。图与表都是样本内估计。
    plot = table.sort_values("capm_alpha_percent_per_month")
    y = np.arange(len(plot))
    fig, ax = plt.subplots(figsize=(10, 11))
    ax.scatter(plot["capm_alpha_percent_per_month"], y - .15, label="CAPM", s=27)
    ax.scatter(plot["ff3_alpha_percent_per_month"], y + .15, label="CAPM + SMB + HML", s=27)
    ax.set(yticks=y, yticklabels=plot.index, xlabel="Monthly alpha (%)",
           title="Exhibit 3b — Same 30 stocks and 108 months")
    ax.axvline(0, color="black", linewidth=.8)
    ax.grid(axis="x", alpha=.2)
    ax.legend(loc="lower right")
    screened = result[result.capm_alpha_t.abs() > 2]
    shrunk = int((screened.ff3_alpha_monthly.abs() < screened.capm_alpha_monthly.abs()).sum())
    remaining = int((screened.ff3_alpha_t.abs() > 2).sum())
    fig.text(.10, .025,
             f"Takeaway: {shrunk}/{len(screened)} CAPM-screened alphas shrink; "
             f"{remaining} still cross |t| > 2 under FF3. "
             "Dots are in-sample estimates, not confidence intervals.", fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, 1))
    fig.savefig(out / "exhibit_3b_alpha_before_after.png", dpi=180)
    plt.close(fig)

    flagged = result[result.capm_alpha_t.abs() > 2]
    lines = [
        "# Exhibit 3c — Which Stage 2 alpha screens remain?", "",
        "Both models use the same 30 stocks and 108 months. The |OLS t(alpha)| > 2 rule is a descriptive stock-level screen, not a declaration of mispricing.",
        f"Stage 2's joint GRS test has p = {grs_p:.3f}; it does not reject all-zero CAPM alphas at 5%. Individual screens therefore require caution.", "",
        "| Stock | CAPM alpha (%/month), t | FF3 alpha (%/month), t | SMB beta | HML beta | Joint SMB/HML p | Verdict |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for ticker, row in flagged.iterrows():
        smaller = abs(row.ff3_alpha_monthly) < abs(row.capm_alpha_monthly)
        remains = abs(row.ff3_alpha_t) > 2
        verdict = ("smaller alpha; screen remains" if smaller and remains else
                   "smaller alpha; screen no longer crossed" if smaller else
                   "alpha not smaller; screen remains" if remains else
                   "alpha not smaller; screen no longer crossed")
        lines.append(
            f"| {ticker} | {100*row.capm_alpha_monthly:.3f}, {row.capm_alpha_t:.2f} | "
            f"{100*row.ff3_alpha_monthly:.3f}, {row.ff3_alpha_t:.2f} | "
            f"{row.beta_smb:.3f} | {row.beta_hml:.3f} | "
            f"{row.joint_smb_hml_p:.4g} | {verdict} |"
        )
    if flagged.empty:
        lines.append("| None | — | — | — | — | — | No Stage 2 stock crossed the screen |")
    reduced = (result.ff3_alpha_monthly.abs() < result.capm_alpha_monthly.abs()).sum()
    lines += [
        "", f"Absolute alpha falls for {reduced}/30 stocks; mean absolute alpha changes "
        f"from {100*result.capm_alpha_monthly.abs().mean():.3f}% to "
        f"{100*result.ff3_alpha_monthly.abs().mean():.3f}% per month.",
        "The joint p-value tests whether SMB and HML loadings are both zero in each "
        "stock's time-series regression; it does not test whether its alpha is zero.",
        "A t-statistic crossing the threshold can reflect a changed standard error. "
        "A higher in-sample R-squared or significant factor loading is not by itself proof "
        "that an abnormal return has been explained. The universe was selected retrospectively; "
        "the market and published factors are proxies. This is not a trading backtest.", "",
    ]
    (out / "exhibit_3c_verdict.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Unmodified group repository")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    repo, out = args.repo.expanduser().resolve(), args.out.expanduser().resolve()
    paths, tickers, names, excess, ff3, stage2, grs_p = load_inputs(repo)
    result = fit_models(tickers, names, excess, ff3, stage2)
    write_exhibits(out, result, grs_p)
    # 5. 记录样本、输入哈希和软件版本，便于他人检查是否使用相同数据。
    checks = {
        "sample": [str(MONTHS[0]), str(MONTHS[-1])], "months": len(MONTHS),
        "stocks": len(tickers), "factor_source": "instructor cached FF3 file in group repo",
        "rf_matches": True, "stock_excess_matches_total_minus_rf": True,
        "capm_stage2_reproduced": True, "stage2_grs_p": grs_p,
        "inputs_sha256": {str(path.relative_to(repo)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in paths.values()},
        "versions": {"numpy": np.__version__, "pandas": pd.__version__,
                     "statsmodels": statsmodels.__version__, "matplotlib": matplotlib.__version__},
    }
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(f"Stage 3 complete: {len(tickers)} stocks, {len(MONTHS)} months. Exhibits: {out}")


if __name__ == "__main__":
    main()
