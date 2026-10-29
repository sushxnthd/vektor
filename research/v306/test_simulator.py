"""Independent subset oracle and invariant checks for V306."""
import itertools
import unittest
from simulator import legal_subsets, next_head, pilot, program, select, simulate, ISSUE


def oracle(head, queues):
    n = len(queues)
    feasible = set()
    for k in range(ISSUE + 1):
        for ws in itertools.combinations(range(n), k):
            if any(head[w] >= len(queues[w]) for w in ws):
                continue
            occupied = []
            for w in ws:
                m = queues[w][head[w]]
                occupied.extend(b for b in range(8) if (m >> b) & 1)
            if len(occupied) == len(set(occupied)):
                feasible.add(sum(1 << w for w in ws))
    return feasible


class BankLookaheadTests(unittest.TestCase):
    def test_exhaustive_reference_oracle(self):
        pairs = (0b00000011, 0b00001100, 0b00110000, 0b11000000)
        count = 0
        for xs in itertools.product(pairs, repeat=4):
            q = tuple((x, (x << 2 | x >> 6) & 255) for x in xs)
            for h in itertools.product((0,1,2), repeat=4):
                self.assertEqual(set(legal_subsets(h,q)), oracle(h,q))
                count += 1
        self.assertEqual(count, 20736)

    def test_conservation_and_bank_port(self):
        for regime in ('W1', 'N1'):
            for seed in (21,22,23,24):
                q = program(seed,regime)
                for policy in ('priority','max_now','future_tie','lookahead'):
                    r = simulate(q,policy)
                    self.assertEqual(r.issued, 5*48)
                    self.assertGreaterEqual(r.cycles, 80)
                    self.assertEqual(r.idle_slots, r.cycles*ISSUE-r.issued)

    def test_determinism(self):
        self.assertEqual(pilot((21,22)),pilot((21,22)))

    def test_strong_control_has_same_lookahead_visibility(self):
        q = program(29,'W1')
        h=(0,)*5
        self.assertIn(select(h,q,'future_tie'),oracle(h,q))
        self.assertIn(select(h,q,'lookahead'),oracle(h,q))

if __name__ == '__main__':
    unittest.main()
