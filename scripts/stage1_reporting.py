"""Readable, reproducible Markdown tables for Stage 1."""
import numpy as np
import pandas as pd

def table(frame, formatter):
    lines=['| Stock | '+' | '.join(frame.columns)+' |','|---|'+'---:|'*len(frame.columns)]
    for name,row in frame.iterrows():
        lines.append('| '+str(name)+' | '+' | '.join(formatter(v) for v in row)+' |')
    return '\n'.join(lines)

def expand_report(report,out,weights):
    sections=['## Mean vectors and covariance matrices\n\nAll estimation uses monthly decimal returns. The arithmetic mean is mu_i = sum(r_it)/T; mean excess return is mu_e,i = mu_i - mean(r_f). Sample covariance is Sigma_ij = sum[(r_it-mu_i)(r_jt-mu_j)]/(T-1). The covariance uses total stock returns. No geometric averaging is used. Displayed mean returns are percentages; downloadable CSVs retain decimals. Covariance entries are decimal-return squared, not correlations.\n']
    for n in [108,96,84]:
        means=pd.read_csv(out/f'means_{n}m.csv',index_col=0)
        means.columns=['Mean monthly return','Mean monthly excess return']
        cov=pd.read_csv(out/f'covariance_monthly_{n}m.csv',index_col=0)
        sections.append(f'### {n}-month estimated moments\n\n[Download mean vector](means_{n}m.csv) · [Download full 30 × 30 covariance matrix](covariance_monthly_{n}m.csv)\n\n'+table(means,lambda x:f'{100*x:.4f}%'))
        sections.append('\n<details>\n<summary>Complete covariance matrix (30 rows × 30 columns; horizontally scrollable)</summary>\n\n'+table(cov,lambda x:f'{x:.6g}')+'\n\n</details>\n')
    summary=pd.read_csv(out/'summary_statistics.csv',index_col=0)
    summary=summary[['mean_monthly_return','monthly_volatility','min_monthly_return','max_monthly_return']]
    summary.columns=['Monthly mean','Monthly volatility','Minimum month','Maximum month']
    sections.append('## Full-sample summary statistics\n\nEvery stock has 108 observations. [Download complete statistics](summary_statistics.csv).\n\n'+table(summary,lambda x:f'{100*x:.2f}%'))
    for n,start in [(108,'January 2017'),(96,'January 2018'),(84,'January 2019')]:
        frame=weights[[f'tangency_{n}m','value_weight_2025_12_31']].copy()
        frame.columns=['Tangency weight','Value weight (2025-12-31)']
        frame.to_csv(out/f'weights_{n}m.csv',index_label='ticker')
        sections.append(f'## {"Portfolio weights — Full sample" if n==108 else "Portfolio weights — Subsample"}: {n} months\n\n{start}–December 2025. Both columns sum to 100% before rounding. A negative weight is a short position; the value-weight column is identical across windows. [Download this table](weights_{n}m.csv).\n\n'+table(frame,lambda x:f'{100*x:.2f}%'))
        if n==108:sections.append(f'\n![Tangency versus value weights](weights_comparison.png)\n\n*Tangency gross exposure: {abs(weights.tangency_108m).sum():.2%}; value portfolio: 100% long-only.*\n')
    a=weights.tangency_108m
    rows=[]
    for n in [96,84]:
        b=weights[f'tangency_{n}m'];delta=abs(a-b)
        rows.append({'window_months':n,'weight_pearson_correlation_vs_108m':a.corr(b),'same_sign_count':int((np.sign(a)==np.sign(b)).sum()),'mean_absolute_change_pp':100*delta.mean(),'maximum_absolute_change_pp':100*delta.max(),'gross_exposure':abs(b).sum()})
    pd.DataFrame(rows).to_csv(out/'subsample_stability.csv',index=False)
    sections.append('## How stable are the subsamples?\n\nCompare the same stocks and endpoint after removing early observations. Relative to 108 months:\n')
    for row in rows:
        sections.append(f"- **{row['window_months']} months:** cross-stock weight correlation {row['weight_pearson_correlation_vs_108m']:.3f}; {row['same_sign_count']}/30 positions retain their sign; average absolute change {row['mean_absolute_change_pp']:.2f} percentage points; largest change {row['maximum_absolute_change_pp']:.2f} percentage points.")
    sections.append('\nThese highly overlapping windows are not independent validation samples. Weight correlation and leverage changes describe sensitivity to the estimation window. The 84-month result is supplementary; the 108- and 96-month windows meet the course minimum.\n\n![Subsample comparison](subsample_weights.png)\n')
    start=report.index('## Analysis outputs');end=report.index('## Interpretation')
    report=report[:start]+'\n\n'.join(sections)+'\n\n'+report[end:]
    report=report.replace('See `market_cap_audit.md`','See [the capitalization audit](market_cap_audit.md)')
    return report
