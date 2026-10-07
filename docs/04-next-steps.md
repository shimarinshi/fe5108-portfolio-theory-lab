# Next steps and data contracts

## Immediate sequence

1. **Compound the fixed 24 securities to monthly total returns**, January 2017-December 2025: `R_i,m = product_d(1 + r_i,d) - 1`. Do not sum or average daily returns. Preserve security IDs; validate complete month coverage before multiplying.
2. **Join monthly RF** from the existing local file by month. Use `rf_monthly_decimal` directly, with stock returns also expressed as decimals. The expected matrix is 108 months by 24 assets, plus one common RF column.
3. **Obtain and validate historical monthly market capitalization** for these specific securities. Define share-class versus issuer-level scope consistently. Do not substitute ETF position values, dollar trading volume or present-day market caps.
4. **Compute Stage 1**: summary statistics, mean vector, covariance, unconstrained tangency weights and comparable value weights; repeat estimation on a subsample. Do not automatically trim extreme weights that are part of the estimation-error finding.

Monthlyization and Stage 1 estimation are not yet executed by this checkpoint's `run_all.py`. Once implemented, extend that entry point rather than creating disconnected manual steps.

## Value weights and timing

For a monthly value-weighted return series, set the weight for month `t` using **the previous month-end** capitalization within this same 24-stock universe:

`w_i,t = cap_i,t-1 / sum_j(cap_j,t-1)`.

Thus January 2017 requires **December 2016 month-end** capitalization. To compute January 2017-December 2025 returns, obtain at least December 2016-November 2025 lagged observations; include December 2025 too if showing end-sample weights. Do not use the same month's closing market cap as an ex-ante beginning-of-month weight.

The Stage 1 weight chart needs one clearly specified comparison date or summary convention, because full-sample tangency weights are a single vector while monthly value weights vary. A full-sample estimated tangency vector is an in-sample descriptive object, not an ex-ante trading strategy. Specify and label the comparison before reporting it.

## Tangency weights

Estimate monthly mean excess returns using `mean(R_i,t - RF_t)`, and use a consistently defined covariance of risky returns. The usual unconstrained normalized expression is `w = solve(Sigma, mu_excess) / sum(solve(Sigma, mu_excess))`. Use a linear solve, check conditioning and the normalization denominator, and explain ill-conditioning or an ill-behaved solution rather than silently modifying it. Estimate on a common set of dates; keep units and annualization consistent.

## Inputs for later stages

| Stage | Additional input / choice |
|---|---|
| Stage 2 | Monthly market proxy and synchronized RF, regression conventions |
| Stage 3 | At least two additional monthly factors; document construction and provenance |
| Stage 4 | Alternative market proxy, robustness comparison and two-page judgment memo |

Monthly returns + RF + validated capitalization are sufficient to begin the requested Stage 1 work. They do not yet supply all market/factor inputs for the entire project. The current historical-capitalization anomaly is the principal unresolved input issue.
