# Stage 3 FF3 adversarial review

Scope: the FE5108 handout's Stage 3 FF3 core only. Mom, RMW, and CMA extensions are not included.

| Check | Finding |
|---|---|
| At least two factors beyond the market | SMB and HML enter each FF3 regression alongside `Mkt-RF`. |
| 3a, factor construction | The exhibit gives one paragraph each for market, SMB, and HML, distinguishes published long–short factor returns from individual-stock characteristics, and identifies the cached instructor file and Kenneth French definition page. |
| 3b, alpha comparison | One CSV and one chart compare CAPM and FF3 alphas for all 30 stocks on the same 108 months. The chart has a takeaway caption. |
| 3c, verdict | The original CAPM-screened stocks are assessed using alpha magnitude and the FF3 t-statistic. The verdict also reports SMB/HML loadings and cautions against treating a threshold crossing as proof of explanation. |
| Alignment and units | The script requires exactly 30 distinct stocks and all 108 months, rejects missing/duplicate months and nonfinite inputs, checks `stock excess = total return − RF` and factor `RF = stock RF`, and reproduces each Stage 2 CAPM alpha, t-value, and R-squared. |
| Independent check | All 30 CAPM/FF3 alphas, t-values, SMB betas, and HML betas matched the group's separate local integrated Stage 3 implementation exactly on the inspected inputs. Input SHA-256 hashes matched the files used for the run. |

## Limits

- The published US factors are permitted for a US universe under Track A, but they are proxies and were **not** built from these 30 stocks. Factor construction reference: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html.
- The `|t| > 2` individual screens are unadjusted for 30 comparisons. Stage 2's joint GRS p-value is about 0.310, so those screens do not establish mispricing. The 30-stock universe was selected retrospectively.
- This folder is a Stage 3 supplement. The remote repository still needs Stage 3 integrated with its `run_all.py` entry point, and the whole submission still needs the final report, Stage 4, contribution statement, and AI-use acknowledgement. Cached monthly inputs are not the same as a full reconstruction from raw vendor data.
