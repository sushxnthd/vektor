"""V317 two-port delayed-write semantic audit; not GPU timing or RTL."""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from itertools import product
import json

@dataclass(frozen=True)
class Write:
    port: int
    cycle: int  # 0 means absent
    lanes: int
    identity_hit: bool

    @property
    def active(self):
        return self.cycle > 0 and self.lanes != 0


def grant_from_monitor(captured, requested, writes, query_cycle, delivery_latency):
    if not requested or requested & ~captured:
        return False
    return not any(w.active and w.identity_hit and w.lanes & requested
                   and w.cycle + delivery_latency <= query_cycle for w in writes)


def grant_with_source_barrier(captured, requested, writes, query_cycle, delivery_latency):
    # Requires source-authoritative in-flight knowledge not available to RTL.
    if any(w.active and w.cycle + delivery_latency > query_cycle for w in writes):
        return False
    return grant_from_monitor(captured, requested, writes, query_cycle, delivery_latency)


def oracle_value_safe(captured, requested, writes):
    return bool(requested and not (requested & ~captured)
                and not any(w.active and w.identity_hit and w.lanes & requested
                            for w in writes))


def exhaustive_audit():
    summary = []
    witness = None
    for horizon in (2, 3, 4):
        for latency in (0, 1, 2):
            c = defaultdict(int)
            for cap, req, t0, t1, m0, m1, h0, h1 in product(
                    range(1, 4), range(1, 4), range(horizon + 1),
                    range(horizon + 1), range(4), range(4), (False, True), (False, True)):
                writes = (Write(0, t0, m0, h0), Write(1, t1, m1, h1))
                actual = oracle_value_safe(cap, req, writes)
                naive = grant_from_monitor(cap, req, writes, horizon, latency)
                barrier = grant_with_source_barrier(cap, req, writes, horizon, latency)
                # Separate source-level reference; does not call candidate grants.
                pending = ((t0 > 0 and m0 > 0 and t0 + latency > horizon)
                           or (t1 > 0 and m1 > 0 and t1 + latency > horizon))
                assert barrier == (actual and not pending)
                c['worlds'] += 1
                c['actual_safe'] += int(actual)
                c['naive_grants'] += int(naive)
                c['barrier_grants'] += int(barrier)
                c['naive_unsafe_grants'] += int(naive and not actual)
                c['barrier_unsafe_grants'] += int(barrier and not actual)
                c['safe_opportunities_lost_by_barrier'] += int(actual and not barrier)
                if naive and not actual and witness is None:
                    witness = {'horizon': horizon, 'latency': latency,
                               'captured': cap, 'requested': req,
                               'write0': vars(writes[0]), 'write1': vars(writes[1])}
            assert c['barrier_unsafe_grants'] == 0
            assert (c['naive_unsafe_grants'] == 0) == (latency == 0)
            summary.append({'horizon': horizon, 'latency': latency, **c})
    sensitivity = [{'per_port_write_probability': p, 'latency': d,
                    'global_quiet_window_probability': round((1-p)**(2*d), 9)}
                   for p, d in product((0.0, 0.01, 0.05, 0.1, 0.25), (0, 1, 2, 4))]
    return {'evidence_tier': 'EXHAUSTIVE_TWO_LANE_TEMPORAL_SEMANTICS_NOT_PHYSICAL',
            'total_worlds': sum(x['worlds'] for x in summary),
            'first_unsafe_witness': witness, 'summary': summary,
            'global_quiet_window_sensitivity': sensitivity,
            'source_authority_implemented': False,
            'same_information_baseline_incremental_transactions_saved': 0}

if __name__ == '__main__':
    print(json.dumps(exhaustive_audit(), indent=2, sort_keys=True))
