"""Frozen-2025 allocations, Jan 2 2026 open to Oct 6 close; cached data only."""
from pathlib import Path
import json, hashlib, io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
CACHE=ROOT/'sources'
OUT=ROOT/'results'
START='2026-01-02';END='2026-10-06'

def yahoo(symbol):
    raw=json.loads((CACHE/(symbol.replace('^','INDEX_')+'.json')).read_text())['chart']['result'][0]
    dates=pd.to_datetime(raw['timestamp'],unit='s',utc=True).tz_convert('America/New_York').strftime('%Y-%m-%d')
    bars=pd.DataFrame(raw['indicators']['quote'][0],index=dates).sort_index()
    assert not bars.index.duplicated().any()
    assert not raw.get('events',{}).get('splits'), 'Split needs explicit ledger handling'
    bars=bars.loc[START:END].copy()
    bars['dividend']=0.
    for event in raw.get('events',{}).get('dividends',{}).values():
        dt=pd.Timestamp(event['date'],unit='s',tz='UTC').tz_convert('America/New_York').strftime('%Y-%m-%d')
        # Buying at the open on an ex-date does not earn that day's dividend.
        if START<dt<=END:
            assert dt in bars.index
            bars.loc[dt,'dividend']+=event['amount']
    assert bars[['open','close']].notna().all().all()
    return bars

def run():
    OUT.mkdir(exist_ok=True)
    weights=pd.read_csv(PROJECT/'artifacts/stage1/portfolio_weights.csv',index_col=0)
    cap=pd.read_csv(PROJECT/'artifacts/input/year_end_market_cap_2025.csv').set_index('formation_ticker')
    dates=yahoo('SPY').index
    assert dates[0]==START and dates[-1]==END
    legs={};entries={};cashflows={};data=[]
    maps={t:cap.loc[t,'source_ticker'] for t in weights.index}
    actions=[]
    def results(symbol,kind):
        rec=json.loads((CACHE/f'massive_{symbol}_{kind}.json').read_text())
        return [x for page in rec['pages'] for x in page.get('results',[])]
    for ticker in weights.index:
        symbol=maps[ticker];bars=pd.DataFrame(results(symbol,'prices'))
        bars.index=pd.to_datetime(bars.t,unit='ms',utc=True).dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d')
        assert list(bars.index)==list(dates),ticker
        entry=float(bars.loc[START,'o']);assert entry>0
        splits={};divs={}
        for e in results(symbol,'splits'):
            dt=e['execution_date'];factor=e['split_to']/e['split_from'];splits[dt]=splits.get(dt,1)*factor
            actions.append({'ticker':ticker,'date':dt,'type':'split_or_stock_distribution','factor_or_cash':factor})
        for e in results(symbol,'dividends'):
            dt=e['ex_dividend_date']
            if START<dt<=END:
                assert dt in dates;divs[dt]=divs.get(dt,0)+e['cash_amount']
                actions.append({'ticker':ticker,'date':dt,'type':'cash_dividend_per_share','factor_or_cash':e['cash_amount']})
        shares=1.;cash=0.;v=[];cf=[];records=[]
        for dt in dates:
            if dt>START:shares*=splits.get(dt,1.)
            cash+=shares*divs.get(dt,0.)
            price=float(bars.loc[dt,'c']);assert price>0
            v.append((shares*price+cash)/entry);cf.append(cash/entry)
            records.append({'date':dt,'formation_ticker':ticker,'source_symbol':symbol,'unadjusted_close':price,'shares_per_initial_share':shares,'cumulative_cash_per_initial_share':cash,'entry_open':entry})
        legs[ticker]=pd.Series(v,index=dates);cashflows[ticker]=pd.Series(cf,index=dates);entries[ticker]=entry;data.append(pd.DataFrame(records))
    pd.DataFrame(actions).to_csv(OUT/'corporate_actions.csv',index=False)
    wealth=pd.DataFrame(legs,index=dates)
    paths=pd.DataFrame(index=dates)
    paths['Tangency (gross of costs)']=wealth@weights.tangency_108m
    paths['Value weighted']=wealth@weights.value_weight_2025_12_31
    paths['Same 30 stocks, equal weight']=wealth.mean(axis=1)
    benchmarks={'ONEQ':'Nasdaq Composite ETF (ONEQ)','QQQ':'Nasdaq-100 ETF (QQQ)','DIA':'Dow ETF (DIA)','SPY':'S&P 500 ETF (SPY)','SGOV':'T-bill ETF proxy (SGOV)'}
    for t,label in benchmarks.items():
        b=yahoo(t);assert list(b.index)==list(dates)
        paths[label]=(b.close+b.dividend.cumsum())/b.loc[START,'open']
    rows=[line for line in (CACHE/'ff_daily.csv').read_text().splitlines() if line[:8].isdigit()]
    ff=pd.read_csv(io.StringIO('\n'.join(rows)),header=None,names=['date','mkt','smb','hml','rf'])
    ff.index=pd.to_datetime(ff.date.astype(str),format='%Y%m%d').dt.strftime('%Y-%m-%d')
    rf=ff.loc[START:END,'rf']/100
    assert list(rf.index)==list(dates[:len(rf)])
    paths['Official RF (through '+rf.index[-1]+')']=(1+rf).cumprod().reindex(dates)
    # Add a true zero-return baseline at Jan 2 open, separate from the first closing observation.
    times=pd.to_datetime(paths.index)+pd.Timedelta(hours=16)
    paths.index=times
    paths.loc[pd.Timestamp(START+' 09:30')]=1.
    paths=paths.sort_index();paths.index.name='new_york_time'
    assert np.allclose(paths.iloc[0],1)
    assert paths.drop(columns=paths.columns[-1]).notna().all().all()
    paths.to_csv(OUT/'wealth_paths.csv')
    pd.concat(data,ignore_index=True).to_csv(OUT/'holdings_input_daily.csv',index=False)
    wealth.to_csv(OUT/'individual_stock_wealth.csv',index_label='date')
    summary=[]
    for label,col in paths.items():
        x=col.dropna();summary.append({'series':label,'end_date':str(x.index[-1].date()),'total_return':x.iloc[-1]-1,'max_drawdown':(x/x.cummax()-1).min(),'ending_value_per_100':100*x.iloc[-1], 'minimum_return_since_entry':x.min()-1, 'negative_close_count':int((x.iloc[1:]<1).sum())})
    summary=pd.DataFrame(summary);summary.to_csv(OUT/'performance_summary.csv',index=False)
    contribution=pd.DataFrame({'entry_open':pd.Series(entries),'stock_return_including_cash_dividends':wealth.iloc[-1]-1,
        'tangency_weight':weights.tangency_108m,'value_weight':weights.value_weight_2025_12_31})
    contribution['tangency_return_contribution']=contribution.tangency_weight*contribution.stock_return_including_cash_dividends
    contribution['value_return_contribution']=contribution.value_weight*contribution.stock_return_including_cash_dividends
    assert np.isclose(contribution.tangency_return_contribution.sum(),paths['Tangency (gross of costs)'].iloc[-1]-1)
    contribution.to_csv(OUT/'stock_contributions.csv',index_label='ticker')
    # Borrow-cost sensitivity is a scenario, not an observed borrowing rate.
    equity_values=pd.DataFrame(index=dates)
    for t in weights.index:
        v=wealth[t]-cashflows[t]
        equity_values[t]=v
    short_notional=equity_values@(-weights.tangency_108m.clip(upper=0))
    dt=pd.to_datetime(dates);calendar_days=np.r_[0,np.diff(dt).astype('timedelta64[D]').astype(float)]
    integral=float((short_notional.shift(1).fillna(short_notional.iloc[0])*calendar_days/365).sum())
    sensitivity=pd.DataFrame([{'assumed_annual_borrow_fee':f,'approx_return_after_borrow_fee':paths['Tangency (gross of costs)'].iloc[-1]-1-f*integral} for f in [0,.01,.03,.05]])
    sensitivity.to_csv(OUT/'borrow_fee_scenarios.csv',index=False)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    colors=['#b32437','#155e9a','#558b59','#7a4fb0','#e58a23','#6d493b','#548da8','#888888','#333333']
    fig,ax=plt.subplots(figsize=(13,7))
    for i,label in enumerate(paths):ax.plot(paths.index,100*(paths[label]-1),label=label,color=colors[i],lw=2.5 if i<2 else 1.6,ls='--' if i in [2,7,8] else '-')
    ax.axhline(0,color='black',lw=.7);ax.grid(alpha=.18);ax.set_ylabel('Cumulative return (%)')
    ax.set_title('30 capitalization-selected stocks: Jan 2, 2026 open through Oct 6 close',loc='left',pad=16)
    ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False)
    fig.text(.07,.025,'Cash dividends included, not reinvested. Tangency excludes borrowing/trading costs and margin constraints. RF ends Aug 31.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'2026_performance_30stocks.png',dpi=190);plt.close(fig)
    def table(cols, rows):
        return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
    report = """# 2026 tracking: 30-stock capitalization-selected universe

The universe consists of 30 stocks: one largest end-2024 company by vendor market cap among members with 108 complete monthly returns in each text class. Seven classes substitute the largest complete-history member. See [selection](../docs/03-universe-selection.md).

Entry is Jan 2, 2026 open; endpoint is Oct 6 close. Sample tangency and value weights are the Stage 1 weights, estimated through Dec 2025. This does not introduce 2026 returns into that estimation, but selection/method choices were made retrospectively in October 2026.

## Performance

"""
    report += table(['Portfolio','Through','Return','Max drawdown'],[[z.series,z.end_date,f'{z.total_return:+.2%}',f'{z.max_drawdown:.2%}'] for z in summary.itertuples()])
    report += """
![Comparison](results/2026_performance_30stocks.png)

[Ledoit–Wolf covariance comparison](ledoit_wolf/README.md) · [Text distance allocation comparisons](text_weight/README.md).

## Accounting and sources

All 30 stock legs use cached Massive unadjusted OHLC, dated split/stock-distribution factors and cash dividends. Split execution multiplies shares; ex-date cash is the then-current share quantity times cash_amount. Entry-day splits are already reflected in entry price and entry-day dividends are excluded. Cash is retained without interest or reinvestment; shorts owe cash distributions. Corporate actions and daily share/cash ledgers are exported. `validate.py` independently reconstructs all five allocations and compares split-normalized Massive and Yahoo prices for all 30 names; see results/independent_price_checks.csv. This is cross-vendor corroboration, not independent exchange-level ground truth. No missing prices are filled; every stock must cover the common calendar. SF and SCCO have stock-count-changing events; no no-split assumption is made.

ETF benchmark curves retain the existing Yahoo split-adjusted price and matching cash-dividend convention and their original cached observations. There are no split events in those benchmark caches. Official French RF stops Aug 31, 2026; SGOV is a separate full-period T-bill ETF proxy. RF is not extrapolated. Daily RF is a reference convention, not an exact opening-to-closing cash-account return.

## Interpretation limits

This is retrospective out-of-estimation-sample tracking, not a preregistered or certified point-in-time strategy. Historical capitalization, 2024 grouping applied to earlier returns and complete-history screening retain their selection/timing limitations. Stock-versus-index comparisons do not isolate classification skill. Tangency is an idealized leveraged long/short ledger with no borrow availability, financing cost, trading cost, taxes or margin liquidation. Cash earns no interest. Borrow-fee scenarios are assumptions, not actual achieved net returns. No strategy is risk matched to another.

## Reproduce

Run `python backtest_2026.py`, then `python ledoit_wolf/compare.py` and `python text_weight/compare.py`. Dependencies: NumPy, pandas, scikit-learn, SciPy and Matplotlib. All calculation scripts are offline after cache creation. `fetch_sources.py` downloads only missing stock receipts and verifies Singapore egress before reading local credentials. Sanitized responses contain no authentication. Raw prices and corporate-action data remain subject to vendor limitations; this is not an independent audit of every record.
"""
    (ROOT/'README.md').write_text(report)
    manifest={'start':START,'end':END,'rf_end':rf.index[-1],'stocks':30,'sessions':len(dates),'minimum_tangency_wealth':float(paths.iloc[:,0].min()),'split_events':sum(x['type']=='split_or_stock_distribution' for x in actions),'checks':'Complete calendars; no forward filling; sign-aware cash distributions; weight attribution reconciliation; 1.0 entry wealth.',
        'sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in CACHE.glob('*') if f.is_file()}}
    (OUT/'verification.json').write_text(json.dumps(manifest,indent=2));print(summary.to_string(index=False));print(sensitivity.to_string(index=False))

if __name__=='__main__':run()
