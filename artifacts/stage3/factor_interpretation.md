# Factor interpretation — Which CAPM alpha screens remain?

Both models use the same 30 stocks and 108 months. The |OLS t(alpha)| > 2 rule is a descriptive stock-level screen, not a declaration of mispricing.
Stage 2's joint GRS test has p = 0.310; it does not reject all-zero CAPM alphas at 5%. Individual screens therefore require caution.

| Stock | CAPM alpha (%/month), t | FF3 alpha (%/month), t | SMB beta | HML beta | Joint SMB/HML p | Verdict |
|---|---:|---:|---:|---:|---:|---|
| MSFT | 1.032, 2.50 | 0.693, 2.07 | -0.473 | -0.545 | 2.937e-11 | smaller alpha; screen remains |
| WMT | 1.008, 2.07 | 0.737, 1.56 | -0.528 | -0.141 | 0.004552 | smaller alpha; screen no longer crossed |

Absolute alpha falls for 13/30 stocks; mean absolute alpha changes from 0.594% to 0.574% per month.
The joint p-value tests whether SMB and HML loadings are both zero in each stock's time-series regression; it does not test whether its alpha is zero.
A t-statistic crossing the threshold can reflect a changed standard error. A higher in-sample R-squared or significant factor loading is not by itself proof that an abnormal return has been explained. The universe was selected retrospectively; the market and published factors are proxies. This is not a trading backtest.
