import unittest
import numpy as np
import pandas as pd
from scripts.research import centrality_scores, select_representatives

class SelectionTests(unittest.TestCase):
    def test_self_is_excluded(self):
        scores=centrality_scores([[1,0],[1,0],[0,1]])
        np.testing.assert_allclose(scores,[.5,.5,1.])

    def test_rank_before_eligibility_and_strict_cutoff(self):
        d=pd.DataFrame({'cluster_label':[0,0,1,1], 'centrality_rank':[1,4,1,5],
                        'cik':['a','b','c','d'],'eligible_108':[False,True,False,True]})
        selected=select_representatives(d)
        self.assertEqual(selected.cik.tolist(),['b','d'])
        self.assertEqual(selected.retained.tolist(),[True,False])

    def test_zero_vector_is_rejected(self):
        with self.assertRaises(ValueError):centrality_scores([[0,0],[1,0]])

if __name__=='__main__':unittest.main()
