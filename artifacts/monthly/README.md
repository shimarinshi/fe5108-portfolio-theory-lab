# Monthly stock and risk-free returns

The fixed 24-stock universe, January 2017-December 2025: **108 months, 2,592 asset-month observations**, no missing returns. Daily returns are not uploaded.

- `monthly_total_returns.csv`: 108 rows, 24 ticker columns plus month. Simple total returns in decimals.
- `monthly_excess_returns.csv`: stock total return minus the same month's RF, in decimals.
- `monthly_returns_long.csv`: stable security ID, formation ticker, CIK, trading-day count, first/last trading dates, total return, RF, and excess return.
- `risk_free_monthly.csv`: Kenneth French monthly RF, both original percent and decimal units, with underlying-source annotation. Do not divide monthly RF by 12.
- `verification.json`: dimensions, input hashes, finite-observation checks and independent full-window compounding check.

Stock return formula: `product(1 + daily_total_return) - 1`. Only annual evaluation windows are used, not duplicated history windows. A month is accepted only when every date in the supplied panel's market calendar has a finite observation. Values below -100% are rejected; missing observations are never skipped or zero-filled. Calendar completeness is relative to the supplied panels.

RF source: [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html), monthly F-F Research Data Factors, column RF. The locally cached RF input contains 111 months; this output uses the matching 108. No current-value backfilling is used. Provider total returns are inherited from the upstream processing documented in `docs/01-data.md`.

Reproduction: `python scripts/monthly.py --daily-root ./tbic_returns`. The raw files must be supplied locally. `python run_all.py --daily-root ./tbic_returns --monthly` reproduces the selection and monthly checkpoints together.

Retain January 2017 in the return dataset. If December 2016 capitalization is unavailable, a later analysis using prior-month weights can start February 2017 and use 107 months. Missing market caps for other dates still require resolution; dropping one initial month does not fix unreliable historical share counts. No market-cap weights or portfolio estimates are claimed here.
