import unittest
import numpy as np
import pandas as pd
from scripts.research import centrality_scores, select_representatives

class SelectionTests(unittest.TestCase):
    def test_self_is_excluded(self):
        scores=centrality_scores([[1,0],[1,0],[0,1]])
        np.testing.assert_allclose(scores,[.5,.5,1.])

    def test_largest_eligible_cap_without_centrality_cutoff(self):
        d=pd.DataFrame({'cluster_label':[0,0,0,1,1], 'centrality_rank':[1,99,2,1,2],
                        'market_cap_usd_raw':[100,90,80,200,10], 'identity_match':[True,True,True,False,True],
                        'cik':['a','b','c','d','e'],'eligible_108':[False,True,True,True,True]})
        selected=select_representatives(d)
        self.assertEqual(selected.cik.tolist(),['b','e'])
        self.assertTrue(selected.retained.all())

    def test_zero_vector_is_rejected(self):
        with self.assertRaises(ValueError):centrality_scores([[0,0],[1,0]])

if __name__=='__main__':unittest.main()
