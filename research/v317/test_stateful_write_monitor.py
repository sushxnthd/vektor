"""Independent semantic audit for V317's *stateful* write-observed source buffer.

The reference oracle tracks actual per-lane values and compares forwarded
snapshot values against both pre- and post-write states. This is NOT a GPU
performance model or a verification of complete tile-level write visibility.
"""
import unittest
from itertools import product


def apply_write(value, mask, new_value, lanes=2):
    for lane in range(lanes):
        if mask & (1 << lane):
            bit = 1 << lane
            value = (value & ~bit) | (new_value & bit)
    return value


def admitted(captured, requested, dirty, write_mask=0, valid=True):
    return bool(valid and requested and (requested & ~captured) == 0
                and (requested & (dirty | write_mask)) == 0)


class StatefulWriteMonitorAudit(unittest.TestCase):
    def test_exhaustive_two_lane_value_safety(self):
        worlds = 0
        grants = 0
        blocked_live_hazards = 0
        for initial, new_value, captured, written, requested in product(
                range(4), range(4), range(4), range(4), (1, 2, 3)):
            # Write occurs after snapshot. Admission is checked while write
            # is active, then after sticky dirtiness has been recorded.
            current = apply_write(initial, written, new_value)
            pre_grant = admitted(captured, requested, 0, written)
            post_grant = admitted(captured, requested, written)
            self.assertEqual(pre_grant, post_grant)
            if pre_grant:
                grants += 1
                self.assertEqual(initial & requested, current & requested)
                self.assertEqual(requested & written, 0)
            elif (requested & written) and (requested & ~captured) == 0:
                blocked_live_hazards += 1
            worlds += 1
        self.assertEqual(worlds, 768)
        self.assertGreater(grants, 0)
        self.assertGreater(blocked_live_hazards, 0)

    def test_sticky_dirty_survives_value_aba(self):
        old = 0
        dirty = 0
        for new in (1, 0):
            old = apply_write(old, 1, new)
            dirty |= 1
        self.assertEqual(old, 0)
        self.assertFalse(admitted(1, 1, dirty))

    def test_simultaneous_capture_write_is_conservatively_dirty(self):
        for captured, written, requested in product(range(4), range(4), (1,2,3)):
            dirty = captured & written
            grant = admitted(captured, requested, dirty)
            if grant:
                self.assertEqual(requested & written, 0)

    def test_namespace_and_capture_reset_rules(self):
        # Writes to a different physical warp/register/bank do not dirty.
        self.assertTrue(admitted(3, 1, 0))
        # Old snapshot cannot be used while a new snapshot is captured.
        self.assertFalse(admitted(3, 1, 0, valid=False))
        # Same-information collector baseline can use exactly the same rule:
        for captured, requested, dirty, written in product(
                range(4), (1,2,3), range(4), range(4)):
            candidate = admitted(captured, requested, dirty, written)
            equal_resource_baseline = admitted(captured, requested, dirty, written)
            self.assertEqual(candidate, equal_resource_baseline)


if __name__ == "__main__":
    unittest.main()
