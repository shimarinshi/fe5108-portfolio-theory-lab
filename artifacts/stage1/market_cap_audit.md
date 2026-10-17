# December 31, 2025 capitalization audit

The endpoint snapshot covers the 30-stock universe. It is used only for static Stage 1 value weights, not to choose the stocks. The selection uses the separate December 31, 2024 table.

For every endpoint row, the requested date is 2025-12-31, the vendor CIK matches the selected issuer, market_cap is positive, and raw market_cap equals the observed unadjusted close times weighted_shares_outstanding within floating-point tolerance. Sanitized raw ticker-overview responses are archived in ../input/year_end_sources/. Selected raw closes are in ../input/year_end_prices_2025.csv. No estimates replace these endpoint raw caps.

These checks establish identity and vendor internal arithmetic, not independent correctness of every historical share count. share_class_shares_outstanding is class-level outstanding shares, not float; weighted shares may incorporate equivalent other classes. A difference is a review signal, not automatically an error. Historical SEC-field query dates may correspond to reporting periods rather than publication dates. None of these inputs certifies strict point-in-time availability or an independently audited capitalization estimate.
