"""Offline covariance-only Ledoit-Wolf sensitivity for the frozen 30-stock experiment."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd,sklearn
from sklearn.covariance import LedoitWolf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
O=Path(__file__).resolve().parent;BASE=O.parent;P=BASE.parent
r=pd.read_csv(P/'artifacts/monthly/monthly_total_returns.csv',index_col='month')
rf=pd.read_csv(P/'artifacts/monthly/risk_free_monthly.csv',index_col='month').rf_monthly_decimal.reindex(r.index)
old=pd.read_csv(P/'artifacts/stage1/portfolio_weights.csv',index_col=0).reindex(r.columns)
assert r.shape==(108,30) and r.index[-1]=='2025-12' and r.notna().all().all() and rf.notna().all()
mu=r.mean()-rf.mean();sample=r.cov();fit=LedoitWolf().fit(r.to_numpy());lw=pd.DataFrame(fit.covariance_,index=r.columns,columns=r.columns)
emp=np.cov(r.to_numpy(),rowvar=False,ddof=0);target=np.trace(emp)/30*np.eye(30)
assert np.allclose(lw,(1-fit.shrinkage_)*emp+fit.shrinkage_*target)
def weights(cov):
 z=np.linalg.solve(cov,mu);assert z.sum()>0
 w=pd.Series(z/z.sum(),index=r.columns);assert np.isclose(w.sum(),1)
 assert np.allclose(cov@w,mu/z.sum());return w
w0=weights(sample);w1=weights(lw);assert np.allclose(w0,old.tangency_108m)
W=pd.DataFrame({'Sample tangency':w0,'Ledoit-Wolf tangency':w1,'Value weighted':old.value_weight_2025_12_31});W.index.name='ticker';W.to_csv(O/'weights.csv')
lw.to_csv(O/'covariance_lw_monthly.csv');pd.DataFrame({'mean_monthly_excess':mu}).to_csv(O/'mean_excess_unchanged.csv',index_label='ticker')
stock=pd.read_csv(BASE/'results/individual_stock_wealth.csv',index_col='date').reindex(columns=r.columns);stock.index=pd.to_datetime(stock.index)+pd.Timedelta(hours=16)
paths=pd.read_csv(BASE/'results/wealth_paths.csv',index_col=0,parse_dates=True)
for name in W:
 paths[name]=stock@W[name];paths.loc[paths.index[0],name]=1
assert np.allclose(paths['Sample tangency'],paths['Tangency (gross of costs)'])
paths=paths.drop(columns=['Tangency (gross of costs)']);paths.to_csv(O/'wealth_paths.csv')
d=[]
for name in W:
 w=W[name];c=lw if name=='Ledoit-Wolf tangency' else sample
 d.append({'portfolio':name,'gross_exposure':abs(w).sum(),'long_exposure':w.clip(lower=0).sum(),'short_exposure':-w.clip(upper=0).sum(),'min_weight':w.min(),'max_weight':w.max(),'n_short':int((w<0).sum()),'covariance_condition_number':np.linalg.cond(c),'normalization_denominator':np.linalg.solve(c,mu).sum() if name!='Value weighted' else np.nan,'fitted_sharpe_common_sample_cov':np.sqrt(12)*(w@mu)/np.sqrt(w@sample@w)})
diag=pd.DataFrame(d).set_index('portfolio');diag.to_csv(O/'weight_diagnostics.csv')
metrics=[]
for name in paths:
 v=paths[name].dropna();metrics.append({'portfolio':name,'end_date':str(v.index[-1].date()),'return':v.iloc[-1]-1,'max_drawdown':(v/v.cummax()-1).min(),'minimum_wealth':v.min()})
met=pd.DataFrame(metrics).set_index('portfolio');met.to_csv(O/'performance.csv')
con=pd.DataFrame({'stock_return':stock.iloc[-1]-1})
for name in W:con[name+' contribution']=W[name]*con.stock_return;assert np.isclose(con[name+' contribution'].sum(),met.loc[name,'return'])
con.to_csv(O/'contributions.csv',index_label='ticker')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(12,6.8))
shown=['Sample tangency','Ledoit-Wolf tangency','Value weighted','Nasdaq Composite ETF (ONEQ)','Nasdaq-100 ETF (QQQ)','Dow ETF (DIA)','S&P 500 ETF (SPY)','T-bill ETF proxy (SGOV)']
for name,color in zip(shown,['#ba4d58','#146c62','#2675b5','#a690c5','#db9941','#795340','#97a6b1','#777777']):ax.plot(paths.index,paths[name]-1,label=f'{name} ({met.loc[name,"return"]:+.1%})',color=color,lw=2.4 if name in W else 1.1)
ax.axhline(0,color='#555',lw=.7);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.18);ax.set_ylabel('Return on initial capital')
fig.suptitle('2026 | Covariance shrinkage on the same frozen 30-stock portfolio',x=.08,ha='left',fontsize=16)
fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.073,.93),ncol=2,frameon=False,fontsize=9)
fig.text(.08,.025,'Jan 2 open – Oct 6 close. Fixed signed shares; cash dividends retained. Before borrow/financing fees, trading costs and taxes.\nOnly covariance estimator changes; same Jan 2017–Dec 2025 means and same 2024-text stock selection.',fontsize=9)
fig.subplots_adjust(left=.08,right=.98,bottom=.14,top=.71);fig.savefig(O/'performance_comparison_30stocks.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,9));y=np.arange(30)
for k,(name,color) in enumerate(zip(W.columns,['#ba4d58','#146c62','#2675b5'])):ax.barh(y+(k-1)*.25,W[name],height=.24,label=name,color=color)
ax.set_yticks(y,W.index);ax.invert_yaxis();ax.xaxis.set_major_formatter(PercentFormatter(1));ax.axvline(0,color='#555',lw=.7);ax.legend();ax.set_title('Same inputs, sample versus Ledoit-Wolf covariance');fig.tight_layout();fig.savefig(O/'weight_comparison_30stocks.png',dpi=160);plt.close(fig)
def table(cols,rows):return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
text=f"""# Ledoit–Wolf: new 30-stock universe

Same 108 monthly returns, unchanged excess-mean vector, Jan 2 open to Oct 6 close. Only covariance estimation changes relative to sample tangency. Scikit-learn scaled-identity shrinkage: Sigma=(1-alpha) S_MLE+alpha trace(S_MLE)/N I. Estimated alpha={fit.shrinkage_:.6f}. Weights normalize solve(Sigma,mean_excess); no clipping, mean shrinkage or leverage cap. Uniform covariance divisor scaling cancels in normalized weights.

"""
text+=table(['Portfolio','Gross exposure','Min weight','Max weight'],[[n,f'{x.gross_exposure:.3f}x',f'{x.min_weight:.2%}',f'{x.max_weight:.2%}'] for n,x in diag.iterrows()])
text+='\n## Performance\n\n'+table(['Portfolio','Through','Return','Max drawdown'],[[n,x.end_date,f'{x["return"]:+.2%}',f'{x.max_drawdown:.2%}'] for n,x in met.iterrows()])
text+='\n![Performance](performance_comparison_30stocks.png)\n\n![Weights](weight_comparison_30stocks.png)\n\n'+table(['Ticker']+list(W.columns),[[t]+[f'{v:.2%}' for v in row] for t,row in W.iterrows()])
text+='\nThis is a retrospective covariance sensitivity, not a risk-matched or preregistered test. All stock corporate-action accounting and limitations are inherited from [the main tracking ledger](../README.md). Costs and financing are excluded. Run `python compare.py`; all weights, covariance, means, contributions, daily paths and checks are saved here. No network needed.\n'
(O/'README.md').write_text(text)
inputs=[P/'artifacts/monthly/monthly_total_returns.csv',P/'artifacts/monthly/risk_free_monthly.csv',P/'artifacts/stage1/portfolio_weights.csv',BASE/'results/individual_stock_wealth.csv',BASE/'results/wealth_paths.csv']
(O/'verification.json').write_text(json.dumps({'alpha':float(fit.shrinkage_),'sklearn_version':sklearn.__version__,'checks':'original weights/wealth reproduced; shrinkage identity; positive covariance; weights sum one; contributions reconcile','inputs':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs}},indent=2))
print('alpha',fit.shrinkage_);print(diag.to_string());print(met.loc[list(W.columns)].to_string())
