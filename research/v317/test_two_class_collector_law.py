"""Post-pilot preregistered two-class collector threshold law.

See FROZEN_TWO_CLASS_COLLECTOR_LAW_20261101.md, committed before opening
these count holdouts. Exact service cycles only, not GPU IPC.
"""
import unittest
from research.v317.bounded_collector_exact import solve, independent_validate


def two_class_law(a, b, k):
    if k < 1 or a < 0 or b < 0 or a+b == 0:
        raise ValueError("nonempty counts and K>=1 required")
    return (a+b, a+b if k == 1 else max(a,b))


class TwoClassCollectorLawAudit(unittest.TestCase):
    def test_unopened_frozen_holdouts(self):
        expected = {
            (4,3): {1:(7,7), 2:(7,4), 3:(7,4)},
            (5,2): {1:(7,7), 2:(7,5), 3:(7,5)},
            (1,4): {1:(5,5), 2:(5,4), 3:(5,4)},
            (0,5): {1:(5,5), 2:(5,5), 3:(5,5)},
        }
        for (a,b), by_k in expected.items():
            for k, predicted in by_k.items():
                with self.subTest(a=a,b=b,k=k):
                    self.assertEqual(two_class_law(a,b,k), predicted)
                    actual = []
                    for candidate in (False,True):
                        n,trace = solve((a,b,0),k,candidate)
                        self.assertTrue(independent_validate((a,b,0),k,candidate,trace))
                        actual.append(n)
                    self.assertEqual(tuple(actual), predicted)

    def test_exhaustive_reduced_two_class_sweep(self):
        checks = 0
        for a in range(5):
            for b in range(5):
                if not (a+b):
                    continue
                for k in (1,2,3):
                    actual = []
                    for candidate in (False,True):
                        n,trace = solve((a,b,0),k,candidate)
                        self.assertTrue(independent_validate((a,b,0),k,candidate,trace))
                        actual.append(n)
                    self.assertEqual(tuple(actual), two_class_law(a,b,k))
                    checks += 1
        self.assertEqual(checks,72)


if __name__ == "__main__":
    unittest.main()
