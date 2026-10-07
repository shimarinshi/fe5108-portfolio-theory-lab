import unittest
import numpy as np
from scripts.monthly import compound

class MonthlyTests(unittest.TestCase):
    def test_compounding_not_sum(self):
        self.assertAlmostEqual(compound([.1,-.1]),-.01)
    def test_missing_rejected(self):
        with self.assertRaises(ValueError):compound([.1,np.nan])
    def test_total_loss(self):
        self.assertEqual(compound([.1,-1]),-1)
    def test_invalid_return(self):
        with self.assertRaises(ValueError):compound([-1.01])
