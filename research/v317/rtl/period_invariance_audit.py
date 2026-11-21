#!/usr/bin/env python3
"""Independent conservative falsification of reported clock-period improvements.

A clock period change with byte-identical netlist, SDC, parasitics and STA
report cannot be accepted as independent physical evidence. This is a
necessary consistency test, NOT sufficient timing certification.
"""
PHYSICAL_KEYS = ('netlist_sha256', 'constraints_sha256', 'parasitics_sha256', 'sta_report_sha256')

def audit(candidate, baseline):
    identical = all(candidate.get(k) == baseline.get(k) and candidate.get(k) is not None
                    for k in PHYSICAL_KEYS)
    period_changed = candidate.get('period_ns') != baseline.get('period_ns')
    if identical and period_changed:
        return {'accepted': False, 'reason': 'period_changed_with_identical_physical_evidence'}
    return {'accepted': False, 'reason': 'unverified_period_requires_independent_sta_extraction'}

def self_test():
    b = {k: 'a' * 64 for k in PHYSICAL_KEYS}
    b['period_ns'] = 3.0
    c = dict(b, period_ns=2.0)
    assert audit(c, b)['reason'] == 'period_changed_with_identical_physical_evidence'
    c['sta_report_sha256'] = 'b' * 64
    assert audit(c, b)['reason'] == 'unverified_period_requires_independent_sta_extraction'
    c['period_ns'] = 3.0
    assert audit(c, b)['accepted'] is False
    print('PASS: three synthetic period provenance controls; no physical signoff')

if __name__ == '__main__':
    self_test()
