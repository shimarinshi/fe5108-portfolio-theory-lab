"""Rebuild aligned DJIA PRICE returns from committed month-end index levels.

Optional --daily-cache reads the locally cached Yahoo chart response and refreshes
month-end levels. No network requests or credentials are needed for reproduction.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent.parent

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--daily-cache',type=Path);args=parser.parse_args()
 inp=P/'artifacts/inputs/dow_jones_month_end_levels.csv';out=P/'artifacts/monthly/dow_jones_monthly.csv'
 if args.daily_cache:
  receipt=json.loads(args.daily_cache.read_text());v=receipt['body']['chart']['result'][0];assert v['meta']['symbol']=='^DJI'
  dates=pd.to_datetime(v['timestamp'],unit='s',utc=True).tz_convert('America/New_York')
  d=pd.DataFrame({'date':dates.strftime('%Y-%m-%d'),'close':v['indicators']['quote'][0]['close']});assert d.date.is_unique and d.close.notna().all() and d.close.gt(0).all()
  d['month']=d.date.str[:7];e=d.sort_values('date').groupby('month',as_index=False).tail(1).rename(columns={'date':'month_end_trading_date','close':'index_close'})
  # Check source month-ends against the existing stock calendar for every target month.
  cal=pd.read_csv(P/'artifacts/monthly/monthly_returns_long.csv');datecols=[c for c in cal if 'last' in c and 'date' in c];assert len(datecols)==1,datecols
  expected=cal.groupby('month')[datecols[0]].max();actual=e.set_index('month').month_end_trading_date.reindex(expected.index);assert (actual==expected).all()
  e[['month','month_end_trading_date','index_close']].to_csv(inp,index=False)
  meta={'symbol':'^DJI','source':'Yahoo Finance chart daily close','source_url':receipt['url'],'retrieved_at':receipt['retrieved_at'],'daily_response_sha256':hashlib.sha256(args.daily_cache.read_bytes()).hexdigest(),'raw_daily_uploaded':False,'description':'Last observed NY trading-session close per month; 2016-12 is the return base. Price index, excludes dividends.'}
  inp.with_suffix('.source.json').write_text(json.dumps(meta,indent=2)+'\n')
 e=pd.read_csv(inp).set_index('month');target=pd.read_csv(P/'artifacts/monthly/monthly_total_returns.csv').month
 assert e.index.is_unique and e.index.tolist()==pd.period_range('2016-12','2025-12',freq='M').astype(str).tolist()
 e['previous_month_end_trading_date']=e.month_end_trading_date.shift();e['previous_month_end_index_close']=e.index_close.shift();e['price_return_decimal']=e.index_close/e.previous_month_end_index_close-1
 r=e.loc[target].copy();rf=pd.read_csv(P/'artifacts/monthly/risk_free_monthly.csv').set_index('month').rf_monthly_decimal;r['rf_monthly_decimal']=rf.reindex(r.index);r['excess_price_return_decimal']=r.price_return_decimal-r.rf_monthly_decimal;r['symbol']='^DJI';r['return_type']='price_excluding_dividends'
 assert len(r)==108 and r.notna().all().all();assert np.isclose(np.prod(1+r.price_return_decimal),e.index_close.iloc[-1]/e.index_close.iloc[0])
 r.to_csv(out,index_label='month')
 print(f'PASS: {len(r)} aligned months, no missing values, full-period compounding reconciles; price return only.')
if __name__=='__main__':main()
