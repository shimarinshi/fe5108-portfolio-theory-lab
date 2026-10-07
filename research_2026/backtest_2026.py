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
    maps={t:cap.loc[t,'source_ticker'] for t in weights.index};maps.update(RYI='RYZ',HLX='HOS')
    for ticker in weights.index:
        if ticker=='CSGS':
            raw=json.loads((CACHE/'CSGS_prices.json').read_text())['body']
            assert not raw.get('next_url')
            b=pd.DataFrame(raw['results'])
            b.index=pd.to_datetime(b.t,unit='ms',utc=True).dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d')
            b=b.rename(columns={'o':'open','c':'close'})[['open','close']]
            assert b.index[0]==START and b.index[-1]=='2026-05-13'
            before=dates[dates<'2026-05-14'];assert list(b.index)==list(before)
            price=b.close.reindex(dates)
            # Documented mandatory $80.70 settlement: cash receivable, not a stale price fill.
            price.loc['2026-05-14':]=80.70
            div=pd.Series(0.,index=dates)
            dr=json.loads((CACHE/'CSGS_dividends.json').read_text())['body'];assert not dr.get('next_url')
            for event in dr['results']:
                if START<event['ex_dividend_date']<'2026-05-14':div.loc[event['ex_dividend_date']]+=event['cash_amount']
            entry=b.loc[START,'open']
        else:
            b=yahoo(maps[ticker]);assert list(b.index)==list(dates), ticker
            price=b.close;div=b.dividend;entry=b.loc[START,'open']
        assert entry>0 and price.notna().all()
        # Fixed signed shares: dividends are accrued cash (short positions owe them).
        legs[ticker]=(price+div.cumsum())/entry
        cashflows[ticker]=div.cumsum()/entry;entries[ticker]=entry
        data.append(pd.DataFrame({'date':dates,'formation_ticker':ticker,'source_symbol':maps[ticker],
            'price_or_cash_settlement':price.values,'cumulative_dividend_receivable_per_share':div.cumsum().values,'entry_open':entry,
            'position_type':['cash_settlement' if ticker=='CSGS' and dt>='2026-05-14' else 'equity' for dt in dates]}))
    wealth=pd.DataFrame(legs,index=dates)
    paths=pd.DataFrame(index=dates)
    paths['Tangency (gross of costs)']=wealth@weights.tangency_108m
    paths['Value weighted']=wealth@weights.value_weight_2025_12_31
    paths['Same 24 stocks, equal weight']=wealth.mean(axis=1)
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
        if t=='CSGS':v.loc['2026-05-14':]=0
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
    ax.set_title('Frozen 2025 portfolios: buy at Jan 2, 2026 open; hold through Oct 6 close',loc='left',pad=16)
    ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False)
    fig.text(.07,.025,'Cash dividends included, not reinvested. Tangency excludes borrowing/trading costs and margin constraints. RF ends Aug 31.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'2026_performance.png',dpi=190);plt.close(fig)
    sec={'CSGS':'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2026-319','RYI':'https://www.sec.gov/Archives/edgar/data/1481582/000119312526051335/d29973dex991.htm','HLX':'https://www.sec.gov/Archives/edgar/data/866829/000119312526378529/d102206d8k.htm'}
    lines=['# 2026 retrospective out-of-estimation-sample tracking','',
        'Entry: January 2, 2026 official daily opening prices (January 1 holiday). End: October 6, 2026 close. Weights are frozen from the 108-month Stage 1 fit ending December 2025. No 2026 observations enter that fit. Fractional signed shares are permitted; no discretionary rebalancing. Dividends accrue as cash receivables on ex-dates, with zero interest and no reinvestment; short positions owe the same distributions. An ex-dividend date coinciding with entry does not earn a dividend.',
        '', '## Results','','| Portfolio / benchmark | Through | Return | Maximum drawdown |\n|---|---|---:|---:|\n'+'\n'.join(f'| {z.series} | {z.end_date} | {100*z.total_return:.2f}% | {100*z.max_drawdown:.2f}% |' for z in summary.itertuples()),'','![Cumulative returns](results/2026_performance.png)','',
        'Main index comparisons use investable ETFs with distributions, not price-only indices. ONEQ tracks the Nasdaq Composite, QQQ the Nasdaq-100, DIA the Dow and SPY the S&P 500. ETF fees are embedded in observed prices. SGOV is a short-Treasury ETF proxy, not a guaranteed risk-free deposit. Official Ken French RF is compounded only through its last available observation, August 31; it is not extrapolated. The first RF day is the daily reference return, not a precisely time-matched intraday cash-account return.',
        '', '## Mandatory corporate actions','',
        '- RYI becomes RYZ: existing Ryerson shares continue; the 1.7105 merger exchange ratio applies to Olympic shareholders, not our Ryerson holdings. Yahoo RYZ carries the predecessor history.',
        '- HLX becomes HOS on September 2: old Helix shares convert 1:1. The 10.27167 ratio in the filing applies to legacy Hornbeck shares, not ours. Yahoo HOS carries predecessor history.',
        '- CSGS last trades May 13 and converts to $80.70 cash on May 14. The settlement claim is recognized on closing and then held as non-interest-bearing cash; actual receipt delays are not modeled. The short position pays the consideration and terminates. No fabricated post-delisting stock prices.',
        *[f'- {t} primary source: {url}' for t,url in sec.items()],
        '', '## Findings','', 'The value-weighted basket returned 7.89%, close to the Dow ETF at 7.92%, below the Nasdaq Composite ETF at 18.50% and Nasdaq-100 ETF at 22.88%. The same basket equal-weighted returned 9.50%. The tangency allocation returned 2.04% before costs, with a 58.76% maximum peak-to-trough drawdown. Its largest negative ending-return contributions were HIW (-26.78 percentage points), VECO (-18.07) and BLMN (-12.53); positive contributions included URI (+22.88) and OSBC (+17.42). Thus this period gives no evidence that the optimized allocation improved realized performance. It does not by itself establish whether text clustering improves stock selection.', '', 'Price cross-check: nine names including all names with daily moves above 20% were compared with Massive across 191 sessions. The maximum closing-price difference across those comparisons was 0.241%; the large jumps are therefore not explained by a Yahoo-only price discrepancy. Minor vendor differences remain; they were not silently overwritten. See results/independent_price_checks.csv. Sources may share upstream exchange data, so this is corroboration rather than independent ground truth.', '', '## Starting-capital downside versus peak-to-trough drawdown','', 'The value-weighted basket briefly fell below its initial capital: minimum cumulative return -0.67%, with 8 negative closing observations. The Dow ETF reached -5.95%, with 25 negative closing observations. Thus the basket experienced a shallower and shorter loss relative to the entry capital in this observed period, while ending with a similar return. This is a favorable descriptive result. It is different from maximum drawdown, which measures losses from a running peak: value -10.00% versus Dow -9.74%. The chart does not show that the basket never lost money, and these results do not establish causal superiority of text clustering or future capital protection.', '', '## Interpretation limits','',
        'This is retrospectively constructed out-of-estimation-sample performance, not a preregistered or strictly point-in-time strategy. Selection and method decisions were finalized in October 2026; Stage 1 capitalization has timing caveats, including subsequently corroborated shares. No claim is made that this exact portfolio was demonstrably available on December 31, 2025. The 2024 text universe and complete-history filters also induce selection effects.',
        'A single selected basket versus broad indices cannot isolate the causal benefit of text clustering. The equal-weight same-basket diagnostic separates allocation choice from the chosen stocks only; it does not supply a random or sector-matched control universe. Large gross exposure confounds raw-return comparisons. Show drawdowns and contribution attribution alongside returns; do not interpret a win as proof of classification quality.',
        'Tangency is an idealized signed-share ledger. It ignores borrow availability, stock-loan fees, taxes, execution slippage, margin calls and liquidation. Short-sale proceeds finance the long legs, and no interest/rebate is modeled. Borrow-fee scenarios apply hypothetical constant annual fees to lagged marked short notionals using calendar days and exclude entry-day intraday fees. They are not actual after-cost returns. If net equity reaches zero, subsequent frictionless values are not an investable survival path.',
        '', '## Reproduction and data','',
        'Run `python backtest_2026.py` from this directory. No network or credentials are needed after cache creation. Yahoo daily chart responses provide split-adjusted OHLC and dividend events; no split events occur in this interval. Values use closes plus cash dividends, not adjusted closes plus dividends (which would double-count). CSGS data comes from cached Massive unadjusted bars and dividend responses. Cached sources retain raw numeric values. Main plots are arithmetic cumulative returns with a true entry-time baseline.',
        'Source requests: Yahoo `/v8/finance/chart/{symbol}?period1=1767139200&period2=1791417600&interval=1d&events=div,splits`; Massive request URLs are archived without authentication. Ken French: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip . Retrieved October 7, 2026.']
    (ROOT/'README.md').write_text('\n\n'.join(lines))
    manifest={'start':START,'end':END,'rf_end':rf.index[-1],'stocks':24,'sessions':len(dates),'minimum_tangency_wealth':float(paths.iloc[:,0].min()),'split_events':0,'checks':'Complete calendars; no forward filling; sign-aware cash distributions; weight attribution reconciliation; 1.0 entry wealth.',
        'sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in CACHE.glob('*') if f.is_file()}}
    (OUT/'verification.json').write_text(json.dumps(manifest,indent=2));print(summary.to_string(index=False));print(sensitivity.to_string(index=False))

if __name__=='__main__':run()
