# Factor definitions and sources

**Market excess return.** The existing Stage 2 market proxy is the monthly return on the broad US equity market minus the one-month risk-free rate. Each stock's dependent variable is its monthly total return minus the same RF. The cached factor file is already in decimal monthly returns; no second RF subtraction or percent conversion is performed.

**SMB (size).** The published Fama–French three-factor SMB is the average monthly return on the three small size/book-to-market portfolios minus the average on the three big portfolios. The portfolios are formed using prior accounting and market-cap data; SMB is a portfolio *return spread*, not the market cap of any of our 30 stocks. A stock's SMB loading measures its return co-movement with that spread.

**HML (value).** The published HML is the average monthly return on the small- and big-stock high book-to-market portfolios minus the average on the corresponding low book-to-market portfolios. It is likewise a return spread, not an individual stock's book-to-market ratio. A stock's HML loading measures its co-movement with the value spread.

**Data provenance.** All three factor-return columns are read from the group's instructor-supplied `artifacts/inputs/ff3_monthly.csv`, which the group README identifies as cached Ken French US factors. We use published factors; we do not reconstruct SMB/HML from the 30 test stocks. Construction reference: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html. The regression window is January 2017–December 2025, 108 months.
