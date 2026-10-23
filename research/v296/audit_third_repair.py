#!/usr/bin/env python3
"""Fail-closed six-case audit for V296 prospective symmetric third repair."""
import json
import math
from pathlib import Path
import re
import sys

VARIANTS = ('original', 'optimized', 'pairwise')
SCENARIOS = ('nominal', 'high')
STAGES = ('routed_final', 'repaired_third', 'routed_third')
REQUIRED = ('V296_CLOCK_PERIOD_NS 3.5', 'V296_CAP_MARGIN_PERCENT 20',
            'V296_SLEW_MARGIN_PERCENT 10', 'V296_MARGIN_PHYSICAL_DONE',
            'V296_THIRD_PHYSICAL_DONE', 'V296_THIRD_CAP_VIOLATORS_BEGIN',
            'V296_THIRD_CAP_VIOLATORS_END')


def stage_metrics(log, stage):
    # Anchor exact stage name: routed_third must never match routed_first.
    pat = (r'(?ms)^V296_STAGE_BEGIN ' + re.escape(stage) +
           r'\r?\n(.*?)^V296_STAGE_END ' + re.escape(stage) + r'\r?$')
    match = re.search(pat, log)
    if not match:
        raise ValueError('Missing stage: ' + stage)
    body = match.group(1)
    m = re.search(r'(?m)^V296_METRIC stage=' + re.escape(stage) +
                  r' area_um2=([0-9.eE+\-]+) slew=(\d+) cap=(\d+)\r?$', body)
    slack = re.search(r'(?mi)^worst slack(?:\s+max)?\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*$', body)
    if not m or not slack:
        raise ValueError('Missing area/slack/electrical evidence: ' + stage)
    area, setup = float(m.group(1)), float(slack.group(1))
    if not (math.isfinite(area) and area > 0 and math.isfinite(setup)):
        raise ValueError('Nonfinite or invalid metrics: ' + stage)
    return {'area_um2': area, 'slack_ns': setup,
            'slew': int(m.group(2)), 'cap': int(m.group(3))}


def audit(root):
    rows = {}
    for scenario in SCENARIOS:
        rows[scenario] = {}
        for variant in VARIANTS:
            stem = f'{variant}.{scenario}'
            log = (root / (stem + '.log')).read_text()
            for token in REQUIRED:
                if token not in log:
                    raise ValueError(f'{stem}: missing {token}')
            if 'V296_ROUTE_FAILED' in log:
                raise ValueError(f'{stem}: failed routing')
            if not (root / (stem + '.third.def')).is_file():
                raise ValueError(f'{stem}: missing third DEF')
            if not (root / (stem + '.final.def')).is_file():
                raise ValueError(f'{stem}: missing frozen second-round DEF')
            rows[scenario][variant] = {stage: stage_metrics(log, stage) for stage in STAGES}
    comp = {}
    all_clean = all_timed = all_smaller = all_faster = True
    quant_pred = True
    for scenario in SCENARIOS:
        finals = {v: rows[scenario][v]['routed_third'] for v in VARIANTS}
        cand = finals['pairwise']
        controls = [finals['original'], finals['optimized']]
        min_control_area = min(x['area_um2'] for x in controls)
        max_control_slack = max(x['slack_ns'] for x in controls)
        saving_pct = 100 * (min_control_area - cand['area_um2']) / min_control_area
        lead = cand['slack_ns'] - max_control_slack
        all_clean &= all(x['slew'] == 0 and x['cap'] == 0 for x in finals.values())
        all_timed &= all(x['slack_ns'] >= 0 for x in finals.values())
        all_smaller &= cand['area_um2'] < min_control_area
        all_faster &= cand['slack_ns'] > max_control_slack
        quant_pred &= saving_pct >= 10.0 and lead >= 0.30
        comp[scenario] = {'area_saving_pct': saving_pct, 'slack_lead_ns': lead,
                          'third': finals,
                          'second': {v: rows[scenario][v]['routed_final'] for v in VARIANTS}}
    passed = all_clean and all_timed and all_smaller and all_faster
    decision = ('THIRD_PROVISIONAL_GLOBAL_ROUTE_PASS' if passed else
                'THIRD_RETIRE_V296' if not (all_smaller and all_faster) else
                'THIRD_PHYSICAL_GATE_FAIL')
    return {'decision': decision, 'quantitative_prediction_supported': quant_pred,
            'all_clean': all_clean, 'all_timed': all_timed,
            'all_smaller': all_smaller, 'all_faster': all_faster,
            'holdouts': 'SEALED', 'clock_ns': 3.5,
            'evidence_class': 'global_route_RC_not_extracted_SPEF',
            'comparisons': comp,
            'limitations': 'No CTS, hold, detailed route, power, tile or GPU throughput.'}


def self_test():
    def sample(stage, area=5000, slack=0.2):
        return (f'V296_STAGE_BEGIN {stage}\nV296_METRIC stage={stage} '
                f'area_um2={area} slew=0 cap=0\nworst slack max {slack}\n'
                f'V296_STAGE_END {stage}\n')
    log = sample('routed_first', 9000) + sample('routed_final', 6000) + sample('routed_third')
    assert stage_metrics(log, 'routed_third')['area_um2'] == 5000
    assert stage_metrics(log, 'routed_final')['area_um2'] == 6000
    for bad in [sample('routed_third').replace('cap=0', 'cap=no'),
                sample('routed_third').replace('worst slack max 0.2', 'worst slack max nan'),
                sample('routed_third').replace('V296_STAGE_END routed_third', 'V296_STAGE_END routed_first')]:
        try:
            stage_metrics(bad, 'routed_third')
        except ValueError:
            continue
        raise AssertionError('Accepted malformed physical evidence')
    print('V296_THIRD_AUDIT_SELFTEST_PASS')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--self-test':
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 2:
        raise SystemExit('Usage: audit_third_repair.py ROOT | --self-test')
    root = Path(sys.argv[1]); root.mkdir(parents=True, exist_ok=True)
    try:
        result = audit(root)
    except (ValueError, OSError) as exc:
        result = {'decision': 'THIRD_INCOMPLETE_EVIDENCE', 'holdouts': 'SEALED', 'error': str(exc)}
    (root / 'third_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if result['decision'] != 'THIRD_PROVISIONAL_GLOBAL_ROUTE_PASS':
        raise SystemExit(3)
