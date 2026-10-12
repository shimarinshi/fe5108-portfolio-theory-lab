"""Reproduce aligned MSCI World USD net total returns from official month-end levels."""
from pathlib import Path
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent.parent

def main():
 e=pd.read_csv(P/'artifacts/inputs/msci_world_month_end_levels.csv').set_index('month')
 assert e.index.is_unique and e.index.tolist()==pd.period_range('2016-12','2025-12',freq='M').astype(str).tolist()
 assert e.index_close.gt(0).all() and e.notna().all().all()
 assert (pd.to_datetime(e.month_end_index_date).dt.strftime('%Y-%m').values==e.index).all()
 e['previous_month_end_index_date']=e.month_end_index_date.shift();e['previous_month_end_index_close']=e.index_close.shift()
 e['net_total_return_decimal']=e.index_close/e.previous_month_end_index_close-1
 target=pd.read_csv(P/'artifacts/monthly/monthly_total_returns.csv').month;r=e.loc[target].copy()
 rf=pd.read_csv(P/'artifacts/monthly/risk_free_monthly.csv').set_index('month').rf_monthly_decimal
 r['rf_monthly_decimal']=rf.reindex(r.index);r['excess_net_total_return_decimal']=r.net_total_return_decimal-r.rf_monthly_decimal
 r['index_code']='990100';r['currency']='USD';r['return_type']='net_total_return'
 assert len(r)==108 and r.notna().all().all()
 assert np.isclose((1+r.net_total_return_decimal).prod(),e.index_close.iloc[-1]/e.index_close.iloc[0])
 # Official MSCI World USD NET calendar-year table, percent, rounded to two decimals.
 official={2017:22.40,2018:-8.71,2019:27.67,2020:15.90,2021:21.82,2022:-18.14,2023:23.79,2024:18.67,2025:21.09}
 annual=(1+r.net_total_return_decimal).groupby(r.index.str[:4]).prod()-1
 for year,value in annual.items():assert abs(value*100-official[int(year)])<.011,(year,value)
 r.to_csv(P/'artifacts/monthly/msci_world_monthly.csv',index_label='month')
 print('PASS: 108 aligned months; no missing values; full-window and all nine official annual returns reconcile.')
 print(annual.to_string())
if __name__=='__main__':main()
