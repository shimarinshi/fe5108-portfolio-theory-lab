# Monthly stock and risk-free returns

The fixed 30-stock universe, January 2017-December 2025: **108 months, 3,240 asset-month observations**, no missing returns. Daily returns are not uploaded.

- `monthly_total_returns.csv`: 108 rows, 30 ticker columns plus month. Simple total returns in decimals.
- `monthly_excess_returns.csv`: stock total return minus the same month's RF, in decimals.
- `monthly_returns_long.csv`: stable security ID, formation ticker, CIK, trading-day count, first/last trading dates, total return, RF, and excess return.
- `risk_free_monthly.csv`: Kenneth French monthly RF, both original percent and decimal units, with underlying-source annotation. Do not divide monthly RF by 12.
- `verification.json`: dimensions, input hashes, finite-observation checks and independent full-window compounding check.

Stock return formula: `product(1 + daily_total_return) - 1`. Only annual evaluation windows are used, not duplicated history windows. A month is accepted only when every date in the supplied panel's market calendar has a finite observation. Values below -100% are rejected; missing observations are never skipped or zero-filled. Calendar completeness is relative to the supplied panels.

RF source: [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html), monthly F-F Research Data Factors, column RF. The locally cached RF input contains 111 months; this output uses the matching 108. No current-value backfilling is used. Provider total returns are inherited from the upstream processing documented in `docs/01-data.md`.

Reproduction: `python scripts/monthly.py --daily-root ./tbic_returns`. The raw files must be supplied locally. `python run_all.py --daily-root ./tbic_returns --monthly` reproduces the selection and monthly checkpoints together.


Stage 1 uses one static December 31, 2025 capitalization snapshot. All 30 columns were rebuilt from original daily panels after the capitalization-selection change.

## Dow Jones Industrial Average monthly benchmark

`dow_jones_monthly.csv` contains **108 matching months (2017-01 to 2025-12)** for the actual DJIA price index, Yahoo symbol `^DJI`. Includes current/previous month-end trading dates and index levels, monthly price return, matching monthly RF and excess price return. All returns are decimals.

Formula: `price_return_decimal = index_close / previous_month_end_index_close - 1`. The 2016-12 month-end level supplies the January 2017 base. Month-end dates match the existing stock panel; no missing monthly values. This is a **price index excluding dividends**, not a total-return index and not the DIA ETF used in exploratory tracking. Stock total returns and this price benchmark therefore differ in dividend treatment. `excess_price_return_decimal` subtracts RF but does not add dividends.

Source: [Yahoo Finance DJIA historical data](https://finance.yahoo.com/quote/%5EDJI/history/), daily closes aggregated using America/New_York trading dates. The 109 month-end input levels and retrieval metadata are in `../inputs/dow_jones_month_end_levels.csv` and its `.source.json` sidecar. Raw daily data remain local. Offline reproduction: `python scripts/dow_monthly.py`.

## MSCI World monthly benchmark

`msci_world_monthly.csv` contains the same **108 months (2017-01 to 2025-12)**. It follows the Dow file's structure: current/previous month-end index dates and levels, monthly return, matching RF, excess return, and an explicit series identifier. Return columns are named `net_total_return_decimal` and `excess_net_total_return_decimal` to distinguish them from the Dow price-only series. `index_code=990100`, currency USD, variant NETR: **MSCI World Standard (Large+Mid Cap), net total return**, including dividend reinvestment after MSCI's assumed dividend withholding taxes. This is the actual index, not an ETF; net does not mean net of fund management fees or an investor's actual taxes.

Official source: [MSCI historical index data export](https://app2.msci.com/products/index-data-search/). Input levels and full request/retrieval metadata are in `../inputs/msci_world_month_end_levels.csv` and its `.source.json` sidecar. The export identifies `Index Level: Net`, `Currency: USD`, `WORLD Standard (Large+Mid Cap)`. Official observation dates are preserved as `month_end_index_date`; international index dates are not forced onto the US exchange calendar. Index levels retain the export's three decimal places; returns are decimals calculated as `current_level / previous_level - 1`.

The 2016-12 level supplies January 2017's base. All 108 months are complete, cumulative compounding reconciles to the endpoint level ratio, and all nine calendar-year returns agree with the rounded [MSCI World USD Net annual table](https://www.msci.com/indexes/index/990100/msci-world-index). Offline reproduction: `python scripts/msci_world_monthly.py`. MSCI retains ownership of its index data; this repository is a private academic project.
