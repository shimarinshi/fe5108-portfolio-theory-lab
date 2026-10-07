"""Static Stage 1 exhibits. Run from the repository; no network or credentials."""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def run():
    out = ROOT/'artifacts/stage1'
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT/'artifacts/input/year_end_market_cap_2025.csv'
    cap = pd.read_csv(source).set_index('formation_ticker')
    returns_path = ROOT/'artifacts/monthly/monthly_total_returns.csv'
    rf_path = ROOT/'artifacts/monthly/risk_free_monthly.csv'
    r = pd.read_csv(returns_path, index_col='month')
    rf = pd.read_csv(rf_path, index_col='month').rf_monthly_decimal.reindex(r.index)
    assert r.shape == (108,30) and not r.isna().any().any() and not rf.isna().any()
    assert r.index.is_unique and r.index.is_monotonic_increasing
    cap = cap.loc[r.columns]
    assert cap.month_end_trading_date.eq('2025-12-31').all()
    assert cap.market_cap_usd_raw.gt(0).all()
    value = cap.market_cap_usd_raw / cap.market_cap_usd_raw.sum()
    excess = r.sub(rf,axis=0)
    summary = pd.DataFrame({'observations':r.count(), 'mean_monthly_return':r.mean(),
        'mean_monthly_excess_return':excess.mean(), 'monthly_volatility':r.std(ddof=1),
        'annualized_arithmetic_mean':12*r.mean(), 'annualized_volatility':np.sqrt(12)*r.std(ddof=1),
        'min_monthly_return':r.min(), 'max_monthly_return':r.max(),
        'market_cap_usd_raw':cap.market_cap_usd_raw,'value_weight':value})
    summary.index.name='ticker';summary.to_csv(out/'summary_statistics.csv')
    weights=pd.DataFrame({'value_weight_2025_12_31':value})
    metrics=[]
    for n in [108,96,84]:
        x=r.tail(n); mu=x.mean(); me=mu-rf.loc[x.index].mean(); cov=x.cov()
        eigen=np.linalg.eigvalsh(cov)
        assert eigen.min()>0
        z=np.linalg.solve(cov,me)
        assert z.sum()>0, 'Positive-return tangency normalization must be reviewed'
        w=pd.Series(z/z.sum(),index=x.columns)
        assert np.isclose(w.sum(),1) and np.isclose(value.sum(),1)
        assert np.allclose(cov@w, me/z.sum(),atol=1e-12)
        weights[f'tangency_{n}m']=w
        cov.to_csv(out/f'covariance_monthly_{n}m.csv')
        pd.DataFrame({'mean_monthly_return':mu,'mean_monthly_excess_return':me}).to_csv(out/f'means_{n}m.csv',index_label='ticker')
        for label,ww in [('tangency',w),('value',value)]:
            metrics.append({'window_months':n,'start':x.index[0],'end':x.index[-1],'portfolio':label,
                'annualized_mean_excess':float(12*ww@me),'annualized_volatility':float(np.sqrt(12*ww@cov@ww)),
                'fitted_annualized_sharpe':float(np.sqrt(12)*(ww@me)/np.sqrt(ww@cov@ww)),
                'gross_exposure':float(abs(ww).sum()),'net_exposure':float(ww.sum()),
                'min_weight':float(ww.min()),'max_weight':float(ww.max()),
                'covariance_condition_number':float(np.linalg.cond(cov)),
                'l1_weight_change_vs_108m':float(abs(ww-weights.tangency_108m).sum()) if label=='tangency' else 0})
    weights.index.name='ticker';weights.to_csv(out/'portfolio_weights.csv')
    pd.DataFrame(metrics).to_csv(out/'portfolio_diagnostics.csv',index=False)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(12,7));y=np.arange(len(r.columns))
    ax.barh(y-.18,100*weights.tangency_108m,.36,label='Tangency: Jan 2017–Dec 2025',color='#2859a6')
    ax.barh(y+.18,100*value,.36,label='Value: Dec 31, 2025',color='#d88731')
    ax.set_yticks(y,weights.index);ax.invert_yaxis();ax.axvline(0,color='#555',lw=.7)
    ax.set_xlabel('Portfolio weight (%)');ax.set_title('Stage 1: estimated tangency versus endpoint value weights')
    ax.legend(loc='lower right');fig.tight_layout();fig.savefig(out/'weights_comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,7))
    for j,n in enumerate([108,96,84]):ax.barh(y+(j-1)*.25,100*weights[f'tangency_{n}m'],.25,label=f'{n} months')
    ax.set_yticks(y,weights.index);ax.invert_yaxis();ax.axvline(0,color='#555',lw=.7)
    ax.set_xlabel('Tangency weight (%)');ax.set_title('Same endpoint and universe; removing early observations changes the allocation')
    ax.legend();fig.tight_layout();fig.savefig(out/'subsample_weights.png',dpi=180);plt.close(fig)
    verification={'assets':len(r.columns),'months':108,'cutoff':'2025-12-31','missing_returns':0,
        'checks':'Positive definite covariance, linear-system residual, weights sum to one; complete aligned monthly inputs.',
        'sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,returns_path,rf_path]},
        'note':'Static retrospective estimates; fitted Sharpe is not out-of-sample performance. Covariance uses total returns, sample ddof=1; mean excess subtracts mean monthly RF.'}
    (out/'verification.json').write_text(json.dumps(verification,indent=2))
    main=metrics[0];v=metrics[1]
    report=f'''# Stage 1 — Portfolio choice

The 30-asset universe has 108 complete monthly total-return observations from January 2017 through December 2025. The comparison uses one fixed capitalization snapshot dated December 31, 2025, not monthly rebalancing.

## Method

Estimate the arithmetic monthly mean vector and unbiased sample covariance of total returns (ddof=1). Subtract the sample mean monthly risk-free rate to obtain the mean excess-return vector. Solve Sigma z = mu_e and normalize w = z / sum(z). Short positions are permitted in the textbook baseline. Market-value weights equal each company's original Massive capitalization divided by the total of the same 30 companies. Company-level capitalization includes convertible ordinary classes where applicable; it is not a float-adjusted index.

## Required exhibits

- 1a: `summary_statistics.csv`, including monthly means, volatilities and observation counts. Returns and weights in CSVs are decimals, not percentages. Arithmetic annualization is 12 times the monthly mean; volatility uses square root of 12.
- 1b: `weights_comparison.png` and `portfolio_weights.csv`. **Takeaway:** the estimated tangency portfolio has gross exposure of {main['gross_exposure']:.2f} times net capital, whereas the value portfolio is long-only.
- 1c: `subsample_weights.png` and `portfolio_diagnostics.csv`. **Takeaway:** keeping the same 30 assets and December 2025 endpoint, removing 12 or 24 early months materially changes the tangency weights; the value-weight benchmark remains fixed. The 84-month window is a supplemental sensitivity check, not the main sample satisfying the course's 96-observation minimum.

## Interpretation

The full-sample tangency allocation ranges from {main['min_weight']:.1%} to {main['max_weight']:.1%}. Its fitted annualized Sharpe is {main['fitted_annualized_sharpe']:.3f}, versus {v['fitted_annualized_sharpe']:.3f} for the value allocation under the same estimated moments. This is an in-sample optimization outcome, not a prediction or independent performance test. The optimization selects weights using the same observations used to report its objective, so the advantage is optimistic.

Mean estimates are noisy, and inversion of covariance can amplify their errors, especially along low-variance directions. Sample changes can reflect both estimation error and changing economic regimes; the sensitivity exercise does not uniquely identify the cause. Extreme gross exposure makes the textbook solution difficult to implement once financing, short availability and costs are considered. Weight disagreement alone neither rejects CAPM nor proves insufficient diversification: this selected basket is not the theoretical all-asset market portfolio.

## Capitalization audit and limitations

See `market_cap_audit.md`. The December 2025 endpoint snapshot is separate from the December 2024 capitalization used for selection. All 30 endpoint caps are positive, match the expected issuer CIK, and reconcile to raw close times vendor weighted shares. These are identity and internal arithmetic checks, not independent validation of share counts or point-in-time publication. Original supplier values and sanitized responses are retained.

The 2024 text universe and its capitalization ranks are applied retrospectively to 2017–2025 with full-history eligibility filtering. This creates selection/survivorship and look-ahead concerns for a historical trading strategy. Seven classes use the largest available company among members with 108 complete monthly returns, not their absolute largest company. The choice to adopt capitalization selection followed retrospective research comparisons; no out-of-sample superiority is claimed.

## Reproduction

Run `python run_all.py --stage1` from the repository with the existing requirements installed. Existing monthly inputs and the year-end snapshot are reused; no credentials or network are required. Inputs and original market-cap values are not overwritten. This implementation covers the three specified Stage 1 exhibits; constrained or shrinkage portfolios can be added as a further implementation study.
'''
    from scripts.stage1_reporting import expand_report
    report = expand_report(report, out, weights)
    (out/'README.md').write_text(report)
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':run()
