"""Two text weighting rules on the same new 30-stock main universe; offline."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
O=Path(__file__).resolve().parent;B=O.parent;P=B.parent
u=pd.read_csv(P/'artifacts/results/selected_universe.csv').set_index('ticker');w=pd.read_csv(B/'ledoit_wolf/weights.csv',index_col=0);u=u.loc[w.index];assert len(u)==30 and u.cluster_label.nunique()==30
allr=pd.read_csv(P/'artifacts/results/all_company_rankings_2024.csv');z=np.load(P/'artifacts/inputs/tfidf_fused_vectors_2024_seed20260831.npz');vectors=dict(zip(z['tickers'],z['vectors']));centers=[];labels=[]
for cl,g in allr.groupby('cluster_label',sort=True):
 x=np.stack([vectors[t] for t in g.ticker]);x=x/np.linalg.norm(x,axis=1)[:,None];c=x.mean(axis=0);centers.append(c/np.linalg.norm(c));labels.append(cl)
x=np.stack(centers);d=np.clip(1-x@x.T,0,2);np.fill_diagonal(d,0);h=np.median(d[np.triu_indices(30,1)]);S=np.exp(-d/h);assert np.linalg.eigvalsh(S).min()>0
inv=1/S.sum(axis=1);old=.5/30+.5*inv/inv.sum();lo=.25/30;hi=2/30
res=minimize(lambda v:v@S@v,np.ones(30)/30,jac=lambda v:2*S@v,bounds=[(lo,hi)]*30,constraints={'type':'eq','fun':lambda v:v.sum()-1,'jac':lambda v:np.ones(30)},method='SLSQP',options={'ftol':1e-12,'maxiter':2000});assert res.success
v=res.x;grad=2*S@v;free=(v>lo+1e-7)&(v<hi-1e-7);level=grad[free].mean();assert abs(v.sum()-1)<1e-8 and np.max(abs(grad[free]-level))<1e-5
assert (grad[v<=lo+1e-7]>=level-1e-5).all() and (grad[v>=hi-1e-7]<=level+1e-5).all()
w['Text: equal/inverse-similarity blend']=u.cluster_label.map(dict(zip(labels,old)))
w['Text: full matrix optimization']=u.cluster_label.map(dict(zip(labels,v)))
assert np.allclose(w.sum(),1);w.to_csv(O/'weights.csv');pd.DataFrame(d,index=labels,columns=labels).to_csv(O/'cluster_distances.csv',index_label='cluster_label')
u[['cluster_label','company_name','market_cap_rank']].join(w).to_csv(O/'cluster_mapping.csv')
stock=pd.read_csv(B/'results/individual_stock_wealth.csv',index_col=0)[w.index];stock.index=pd.to_datetime(stock.index)+pd.Timedelta(hours=16)
oldpaths=pd.read_csv(B/'ledoit_wolf/wealth_paths.csv',index_col=0,parse_dates=True);paths=oldpaths.copy()
for name in w:
 calc=stock@w[name]
 if name in paths:assert np.allclose(calc,paths.loc[calc.index,name])
 else:paths[name]=calc;paths.loc[paths.index[0],name]=1
pd.testing.assert_frame_equal(paths[oldpaths.columns],oldpaths);paths.to_csv(O/'wealth_paths.csv')
met=[]
for name in paths:
 q=paths[name].dropna();met.append({'portfolio':name,'through':str(q.index[-1].date()),'return':q.iloc[-1]-1,'max_drawdown':(q/q.cummax()-1).min()})
m=pd.DataFrame(met).set_index('portfolio');m.to_csv(O/'performance.csv');con=pd.DataFrame({'stock_return':stock.iloc[-1]-1})
for name in w:con[name]=w[name]*con.stock_return;assert np.isclose(con[name].sum(),m.loc[name,'return'])
con.to_csv(O/'contributions.csv')
shown=['Text: full matrix optimization','Text: equal/inverse-similarity blend','Value weighted','Same 30 stocks, equal weight','Sample tangency','Ledoit-Wolf tangency','Nasdaq Composite ETF (ONEQ)','Nasdaq-100 ETF (QQQ)','Dow ETF (DIA)','S&P 500 ETF (SPY)','T-bill ETF proxy (SGOV)']
for fname,zoom in [('performance_comparison.png',False),('long_only_comparison.png',True)]:
 fig,ax=plt.subplots(figsize=(13,8));colors=['#147553','#7a58a1','#c2883d','#777777','#cc5363','#467db7','#aaaa45','#d17e48','#966974','#8ca2ad','#444444']
 for name,c in zip(shown,colors):
  if zoom and name in ['Sample tangency','Ledoit-Wolf tangency']:continue
  ax.plot(paths.index,paths[name]-1,label=f'{name} ({m.loc[name,"return"]:+.2%})',color=c,lw=2.4 if name==shown[0] else 1.25)
 ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.18);ax.axhline(0,color='#777',lw=.6);ax.set_ylabel('Return on initial capital');ax.spines[['top','right']].set_visible(False)
 fig.suptitle('2026 | Same 30 capitalization-selected representatives',x=.08,ha='left',fontsize=16);fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.074,.94),ncol=2,frameon=False,fontsize=8.5)
 fig.text(.08,.025,'Jan 2 open – Oct 6 close. Same split-aware stock ledger and cash dividends for every allocation.\nRetrospective comparison; no financing, borrowing, trading costs or taxes. Benchmark data unchanged.',fontsize=9)
 fig.subplots_adjust(left=.08,right=.98,bottom=.14,top=.67);fig.savefig(O/fname,dpi=160);plt.close(fig)
def table(cols,rows):return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
text='''# Text allocations on the new 30-stock basket

Same stocks as main: largest end-2024 company cap among members with 108 complete monthly returns in each class. Recompute full-class centroids from normalized original 50D vectors (not UMAP display coordinates). One selected representative receives the entire class budget. No within-class softmax or new pruning.

Let D be pairwise cosine distance, h its off-diagonal median, and S=exp(-D/h), including diagonal 1. The earlier text rule is 0.5/K + 0.5*(1/row_sum(S))/sum(1/row_sum(S)). The full-matrix rule minimizes w^T S w with sum(w)=1 and 0.25/K <= w_i <= 2/K. K=30; bounds are 0.8333% and 6.6667%. They are explicit constraints, not return-tuned parameters. This similarity-sensitive diversity objective does not estimate return covariance or prove risk reduction.

All 30 original classes are represented; no submatrix or renormalization over only 24 classes remains. Both text allocations and the three financial allocations share the same 2026 split-aware economic paths.

## Performance

'''
text+=table(['Portfolio','Through','Return','Max drawdown'],[[n,r.through,f'{r["return"]:+.2%}',f'{r.max_drawdown:.2%}'] for n,r in m.iterrows()]);text+='\n![All comparisons](performance_comparison.png)\n\n![Long-only detail](long_only_comparison.png)\n\n## Weights\n\n'+table(['Ticker']+list(w.columns),[[t]+[f'{v:.2%}' for v in row] for t,row in w.iterrows()])
text+='\nSee [tracking accounting and limitations](../README.md). Retrospective universe/method choices, historical vendor cap uncertainty and excluded costs still apply. The same-basket comparison isolates weighting; it does not isolate classification skill. Run `python compare.py` with NumPy, pandas, SciPy and Matplotlib; all inputs are committed, no network required. Checks include convex optimum feasibility/KKT, weight sums, prior path replication and contribution reconciliation.\n'
(O/'README.md').write_text(text);(O/'verification.json').write_text(json.dumps({'checks':'PASS: 30-class input match; feasible KKT optimum; unit weights; unchanged comparator paths; contributions','bandwidth':float(h),'stocks':30},indent=2));print(m.to_string())
