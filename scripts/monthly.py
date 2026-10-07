"""Compound complete daily total returns and align monthly risk-free returns."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/monthly'

def compound(values):
    x = np.asarray(values, dtype=float)
    if not len(x) or not np.isfinite(x).all() or (x < -1).any():
        raise ValueError('Invalid daily returns; missing observations cannot be skipped.')
    return float(np.prod(1 + x) - 1)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build(daily_root):
    daily_root = Path(daily_root)
    selected = pd.read_csv(ROOT/'artifacts/results/selected_universe_24.csv', dtype={'cik': str})
    assert len(selected) == 24 and selected.security_id.is_unique
    paths = sorted(daily_root.glob('data/**/returns.parquet'))
    if len(paths) != 9:
        raise ValueError('Expected nine annual daily panels.')
    parts, calendars, sources = [], [], []
    for path in paths:
        frame = pq.ParquetFile(path).read(columns=['date','security_id','window','return']).to_pandas()
        frame = frame[frame.window.eq('evaluation')].copy()
        frame['date'] = pd.to_datetime(frame.date)
        calendars.extend(frame.date.unique())
        parts.append(frame[frame.security_id.isin(selected.security_id)])
        sources.append({'file': str(path.relative_to(daily_root)), 'sha256': digest(path)})
    daily = pd.concat(parts, ignore_index=True)
    if daily.duplicated(['security_id','date']).any():
        raise ValueError('Duplicate security-date observations.')
    daily['month'] = daily.date.dt.to_period('M').astype(str)
    cal = pd.DataFrame({'date': sorted(set(calendars))})
    cal['month'] = cal.date.dt.to_period('M').astype(str)
    expected = cal.groupby('month').date.nunique()
    rows = []
    for (sid, month), group in daily.groupby(['security_id','month']):
        n = int(expected.loc[month])
        if len(group) != n or not np.isfinite(group['return']).all():
            raise ValueError(f'Incomplete daily coverage: {sid}, {month}')
        rows.append({'security_id': sid, 'month': month, 'trading_days': n,
                     'first_trading_date': group.date.min().strftime('%Y-%m-%d'),
                     'last_trading_date': group.date.max().strftime('%Y-%m-%d'),
                     'total_return': compound(group['return'])})
    monthly = pd.DataFrame(rows).merge(selected[['security_id','ticker','cik']], on='security_id', validate='many_to_one')
    months = pd.period_range('2017-01','2025-12',freq='M').astype(str).tolist()
    assert len(monthly) == 108 * 24 and set(monthly.month) == set(months)
    assert monthly.groupby('security_id').size().eq(108).all()
    rf_path = daily_root/'supplements_monthly/risk_free_monthly.csv'
    rf = pd.read_csv(rf_path)
    assert rf.month.is_unique
    assert np.allclose(rf.rf_monthly_percent / 100, rf.rf_monthly_decimal)
    monthly = monthly.merge(rf[['month','rf_monthly_decimal','rf_underlying_source']], on='month', how='left', validate='many_to_one')
    assert monthly.rf_monthly_decimal.notna().all()
    monthly['excess_return'] = monthly.total_return - monthly.rf_monthly_decimal
    monthly = monthly.sort_values(['month','ticker'])
    wide = monthly.pivot(index='month',columns='ticker',values='total_return').reindex(index=months,columns=selected.ticker)
    excess = monthly.pivot(index='month',columns='ticker',values='excess_return').reindex(index=months,columns=selected.ticker)
    # Independent telescoping check: compounded monthly and daily terminal wealth agree.
    errors=[]
    for sid, group in daily.groupby('security_id'):
        a=compound(group['return']);b=compound(monthly.loc[monthly.security_id.eq(sid),'total_return'])
        errors.append(abs(a-b));assert np.isclose(a,b,rtol=1e-11,atol=1e-11)
    OUT.mkdir(exist_ok=True)
    monthly.to_csv(OUT/'monthly_returns_long.csv',index=False)
    wide.to_csv(OUT/'monthly_total_returns.csv')
    excess.to_csv(OUT/'monthly_excess_returns.csv')
    rf[rf.month.isin(months)].sort_values('month').to_csv(OUT/'risk_free_monthly.csv',index=False)
    report={'window':['2017-01','2025-12'],'assets':24,'months':108,'asset_months':2592,
            'missing_values':0,'daily_rows_used':len(daily),'formula':'product(1 + daily total return) - 1',
            'max_terminal_compounding_error':max(errors),'daily_sources':sources,
            'rf_source_sha256':digest(rf_path),'selected_universe_sha256':digest(ROOT/'artifacts/results/selected_universe_24.csv'),
            'market_cap_weights':'Not computed. A later lagged-cap analysis may start one month later if the initial cap is unavailable.'}
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Built {wide.shape[0]} months x {wide.shape[1]} assets; no missing values; terminal compounding check passed.')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--daily-root',default=str(ROOT/'tbic_returns'))
    build(p.parse_args().daily_root)
