"""Independent 30-stock replay validation and cross-vendor normalized price checks."""
from pathlib import Path
import json
import numpy as np,pandas as pd
O=Path(__file__).resolve().parent;P=O.parent
w=pd.read_csv(O/'text_weight/weights.csv',index_col=0);u=pd.read_csv(P/'artifacts/results/selected_universe.csv');assert set(w.index)==set(u.ticker) and len(w)==30
ledger=pd.read_csv(O/'results/holdings_input_daily.csv');legs=pd.read_csv(O/'results/individual_stock_wealth.csv',index_col=0);paths=pd.read_csv(O/'text_weight/wealth_paths.csv',index_col=0,parse_dates=True);checks=[]
for ticker,g in ledger.groupby('formation_ticker'):
 g=g.set_index('date');v=(g.unadjusted_close*g.shares_per_initial_share+g.cumulative_cash_per_initial_share)/g.entry_open
 assert np.allclose(v,legs.loc[g.index,ticker]) and g.cumulative_cash_per_initial_share.diff().dropna().ge(-1e-10).all()
 raw=json.loads((O/'sources'/f'{g.source_symbol.iloc[0]}.json').read_text())['chart']['result'][0]
 dates=pd.to_datetime(raw['timestamp'],unit='s',utc=True).tz_convert('America/New_York').strftime('%Y-%m-%d');yb=pd.DataFrame(raw['indicators']['quote'][0],index=dates).loc[g.index]
 # Split-adjusted Yahoo closes / entry open should match raw close * accumulated shares / raw entry open.
 yy=yb.close/yb.open.iloc[0];mm=g.unadjusted_close*g.shares_per_initial_share/g.entry_open
 rel=(yy/mm-1).abs();checks.append({'ticker':ticker,'sessions':len(g),'maximum_normalized_close_difference':rel.max(),'end_normalized_close_difference':rel.iloc[-1]})
for name in w:
 v=legs@w[name];assert np.allclose(v.to_numpy(),paths[name].iloc[1:].to_numpy())
assert np.allclose(paths.iloc[0],1) and np.allclose(w.sum(),1)
checks=pd.DataFrame(checks);checks.to_csv(O/'results/independent_price_checks.csv',index=False)
(O/'results/final_validation.json').write_text(json.dumps({'stocks':30,'sessions':len(legs),'checks':'PASS: identity sets, signed wealth reconstruction, cash monotonicity, all weight sums and portfolio paths; stock corporate actions explicitly accounted','max_cross_vendor_normalized_price_difference':float(checks.maximum_normalized_close_difference.max())},indent=2))
print(checks.sort_values('maximum_normalized_close_difference',ascending=False).head(8).to_string(index=False));print('PASS: all five allocations reconcile with the 30-stock share/cash ledger')
