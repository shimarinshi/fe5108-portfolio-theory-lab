# Data sources, scope and processing

## Daily stock returns

The local `tbic_returns/` directory is an independent copy of the processed TBIC annual security-return panels. It contains nine year-end formation cohorts, **2016 through 2024**, each with a pre-formation `history` window and the following calendar year's `evaluation` window.

| Item | Scope |
|---|---|
| Dates appearing in tables | 2016-09-30 through 2025-12-31 |
| First finite daily return | 2016-10-03; the initial 2016-09-30 row has no valid return |
| Full project window | 2017-01 through 2025-12: 108 months |
| Distinct identities across all overlapping panels | 4,493 security IDs; 4,332 CIKs |
| Selected assets | 24 securities, with all required daily returns observed in all 108 months |
| Observation type | Simple daily total returns, in decimals; 0.01 means 1% |

These are not 4,493 continuously observed stocks and not a complete historical US equity database. Cohorts are based on historical **iShares Russell 3000 ETF (IWV) holdings**, an accepted proxy rather than a certified historical Russell 3000 membership list. The selected 24-stock universe is narrower still.

[Coverage counts and source-file hashes](../artifacts/inputs/daily_source_coverage.csv) document the copied panels without publishing their return observations.

## Upstream sources

- **Massive**: daily prices, split events, cash distributions and security-reference information.
- **SEC EDGAR**: issuer CIK, filing identity, filing timestamps and annual-report sections. CIK is a company identifier; `security_id` tracks the selected security.
- **Historical IWV holdings**: annual sample membership, not a claim of perfect historical index replication.
- **SEC SIC -> FF48 / FF12**: dated standard-industry benchmark used in TBIC. The current comparisons are not a validated historical GICS study.

## Processing already performed upstream

1. **Security identity.** Dated ticker/FIGI/CIK relationships distinguish ticker reuse and same-security renames. A company may have multiple share classes; the original representative-class decision used pre-formation liquidity, not the present project's text-centrality rule.
2. **Splits and dividends.** Validate raw prices, split-adjusted prices and event/share bases. A vendor's split-adjusted close does not by itself include dividends. For ordinary sessions, same-basis adjusted close and cash dividends on the ex-date produce `r_t = (P_t + D_t) / P_(t-1) - 1`. The `return` column is the main total-return measure; `price_return` omits ordinary cash dividends.
3. **Terminal events.** Verified cash or stock consideration can enter a terminal payoff return. The old security then stops; returns are not automatically continued into the acquirer. Unresolved payoffs remain uncertain or missing.
4. **Quality controls.** Identity conflicts, unsupported currencies/distribution bases, missing prices and unresolved actions can cause quarantines or missing returns. A valid row does not certify every date in that security's history.
5. **Missing observations.** No zero-filling, carried prices, or treating a multi-session gap return as a one-day return.
6. **Study-specific admission.** Earlier TBIC flags include liquidity/history requirements and text/industry availability. They are not a performance filter and are not automatically all applied to this stock pool. Losing or failed stocks were not simply deleted for poor performance.

The data copy preserves processed results and provenance, not every upstream source file and ingestion program. This repository can reproduce the documented downstream checkpoint; it cannot rebuild the entire provider data lake from GitHub alone.

## Avoid duplicated history

For the 2017-2025 project window, use **only each annual cohort's `evaluation` rows** and join by stable security identity. Simply concatenating all history and evaluation windows would count the same security-date repeatedly. The earlier audit found no duplicate security-date rows in the concatenated evaluation panels.

Eligibility is strict: every panel trading date in a month must have a finite return. All 108 months must pass. This depends on the supplied universe and panel coverage; an absent observation does not necessarily imply that the company had not yet listed.

## Monthly risk-free rate: present locally

Local path: `tbic_returns/supplements_monthly/risk_free_monthly.csv`.

- 111 unique months: October 2016 through December 2025.
- Source: monthly F-F Research Data Factors, `RF`, from the [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html).
- `rf_monthly_decimal = rf_monthly_percent / 100`. **Do not divide by 12 again.**
- Join by return month only after daily stock returns have been compounded to monthly frequency.
- Underlying source is Ibbotson Associates through May 2024 and ICE BofA US 1-Month Treasury Bill Index from June 2024, as documented in the retained supplement.
- This is a current download of historical observations, not a preserved real-time data vintage.

## Historical monthly market capitalization: not accepted yet

The existing Massive historical-reference pilot returned repeated weighted share counts across different historical dates for AAPL, MSFT and NVDA. Independent raw-price probes showed that the market-cap field used those repeated counts. That field is **not accepted** as a historical weight input. The flagged AAPL file is a diagnostic, not usable weights; AAPL is not part of the selected 24-stock pool.

A possible reconstruction is historical shares outstanding times the contemporaneous unadjusted price, but security/share-class versus issuer-level scope, split consistency, observation dates and information availability must first be verified. No current capitalization should be backfilled into past months, and no missing capitalization should be replaced by zero.

## Git boundary

`.gitignore` excludes `tbic_returns/`, `tbic_stock_pool/`, raw/processed market data, environment files and caches. The tracked `artifacts/` directory contains only explicitly selected derived research artifacts, not the market observations. Private visibility does not replace provider data-retention and redistribution terms.
