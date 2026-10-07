import unittest
from pathlib import Path
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parents[1]
class ArtifactConsistency(unittest.TestCase):
    def test_selection_moments_and_weights_match_new_universe(self):
        a=pd.read_csv(P/'artifacts/results/all_company_rankings_2024.csv')
        s=pd.read_csv(P/'artifacts/results/selected_universe.csv')
        expected=a[a.eligible_108&a.identity_match&a.market_cap_usd_raw.gt(0)].sort_values(['cluster_label','market_cap_usd_raw','cik'],ascending=[True,False,True]).groupby('cluster_label').head(1)
        self.assertEqual(set(s.security_id),set(expected.security_id));self.assertEqual(s.cluster_label.nunique(),30)
        r=pd.read_csv(P/'artifacts/monthly/monthly_total_returns.csv',index_col=0);rf=pd.read_csv(P/'artifacts/monthly/risk_free_monthly.csv',index_col='month').rf_monthly_decimal
        self.assertEqual(r.shape,(108,30));self.assertEqual(list(r.columns),s.ticker.tolist())
        weights=pd.read_csv(P/'artifacts/stage1/portfolio_weights.csv',index_col=0)
        for n in [108,96,84]:
            x=r.tail(n);mu=x.mean()-rf.loc[x.index].mean();cov=x.cov()
            saved=pd.read_csv(P/f'artifacts/stage1/covariance_monthly_{n}m.csv',index_col=0)
            means=pd.read_csv(P/f'artifacts/stage1/means_{n}m.csv',index_col=0)
            np.testing.assert_allclose(saved,cov,atol=1e-14)
            np.testing.assert_allclose(means.mean_monthly_excess_return,mu,atol=1e-14)
            z=np.linalg.solve(cov,mu);np.testing.assert_allclose(weights[f'tangency_{n}m'],z/z.sum(),atol=1e-12)
        cap=pd.read_csv(P/'artifacts/input/year_end_market_cap_2025.csv',dtype={'expected_cik':str,'returned_cik':str}).set_index('formation_ticker').loc[r.columns]
        self.assertTrue(cap.expected_cik.str.zfill(10).eq(cap.returned_cik.str.zfill(10)).all())
        np.testing.assert_allclose(cap.market_cap_usd_raw,cap.unadjusted_close_usd*cap.weighted_shares_outstanding)
        np.testing.assert_allclose(weights.value_weight_2025_12_31,cap.market_cap_usd_raw/cap.market_cap_usd_raw.sum())
