# Next-stage data contracts

Stage 1 is complete on the frozen 30-stock universe. Monthly total/excess returns and RF have 108 common months, January 2017–December 2025. Values are decimals. Use stable security IDs in long-form data and the recorded formation tickers in wide matrices.

The value-weight comparison uses only December 31, 2025 company market caps; Stage 1 does not require a monthly cap series. Tangency weights use monthly sample total-return covariance and mean stock returns minus the sample mean RF. The 108-, 96- and 84-month windows share the endpoint; 84 months is a supplemental sensitivity below the course's 96-observation main-sample minimum.

For CAPM, agree on and document the market proxy. If using a portfolio constructed from these stocks, explicitly define its weighting/rebalancing and its limitations as a market proxy. If using an external market series, obtain aligned monthly total returns and the same RF convention. Factor analysis needs at least two additional aligned factor series. Those inputs are not supplied by Stage 1 alone.

A future monthly rebalanced capitalization strategy would require prior-month-end caps, including December 2016 for January 2017. It is separate from the current static portfolio comparison. Full-sample fitted weights and retrospective universe selection are not a forward-investable historical backtest.

## Implemented stage dependencies

Stages 2–4 now use the shared cached monthly data. Stage 3 uses published SMB and HML from `artifacts/inputs/ff3_monthly.csv` alongside Mkt-RF; no additional downloads are required. `run_all.py --stage3` runs Stage 1, Stage 2 and then Stage 3. Stage 4 independently depends on Stage 1 and Stage 2; `run_all.py --stage3 --stage4` runs all four in order. Standalone Stage 3 requires existing Stage 2 CAPM and GRS outputs and checks that its CAPM baseline agrees.
