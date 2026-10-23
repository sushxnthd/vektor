#!/usr/bin/env python3
"""Independent fail-closed audit of six-case detailed-route and OpenRCX evidence."""
import json
import math
from pathlib import Path
import re
import sys

VARIANTS = ('original', 'optimized', 'pairwise')
SCENARIOS = ('nominal', 'high')


def extract_metric(log, stage):
    pattern = r'(?ms)^V296_STAGE_BEGIN ' + re.escape(stage) + r'\r?\n(.*?)^V296_STAGE_END ' + re.escape(stage) + r'\r?$'
    match = re.search(pattern, log)
    if not match:
        raise ValueError('Missing stage ' + stage)
    body = match.group(1)
    met = re.search(r'(?m)^V296_METRIC stage=' + re.escape(stage) + r' area_um2=([\d.eE+\-]+) slew=(\d+) cap=(\d+)\r?$', body)
    slack = re.search(r'(?mi)^worst slack(?:\s+max)?\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*$', body)
    if not met or not slack:
        raise ValueError('Missing metric or setup slack: ' + stage)
    result = {'area_um2': float(met.group(1)), 'setup_ns': float(slack.group(1)),
              'slew': int(met.group(2)), 'cap': int(met.group(3))}
    if not all(math.isfinite(result[k]) for k in ('area_um2', 'setup_ns')) or result['area_um2'] <= 0:
        raise ValueError('Nonfinite or invalid area/slack')
    return result


def audit(root):
    results = {}
    for scenario in SCENARIOS:
        results[scenario] = {}
        for variant in VARIANTS:
            stem = f'{variant}.{scenario}'
            log = (root / f'{stem}.log').read_text()
            for token in ('V296_THIRD_PHYSICAL_DONE', 'V296_DETAIL_BEGIN',
                          'V296_DETAILED_PHYSICAL_DONE', 'V296_EXTRACTED_MIN_SLACK_BEGIN',
                          'V296_EXTRACTED_MIN_SLACK_END', 'V296_DETAIL_DRC_COUNT ',
                          'V296_DETAIL_IS_ROUTED 1', 'V296_DETAIL_RC_MULTIPLIER '):
                if token not in log:
                    raise ValueError(f'{stem}: missing {token}')
            expected_rc = '1.0' if scenario == 'nominal' else '2.0'
            if f'V296_DETAIL_RC_MULTIPLIER {expected_rc}' not in log:
                raise ValueError(f'{stem}: wrong extracted RC multiplier')
            drc = re.search(r'(?m)^V296_DETAIL_DRC_COUNT (\d+)\r?$', log)
            if not drc:
                raise ValueError(f'{stem}: no DRC count')
            for suffix in ('.detail.def', '.detail.spef', '.detail.drc.rpt', '.third.def'):
                file = root / (stem + suffix)
                if not file.is_file():
                    raise ValueError(f'{stem}: missing {suffix}')
                if suffix in ('.detail.def', '.detail.spef', '.third.def') and file.stat().st_size <= 0:
                    raise ValueError(f'{stem}: empty {suffix}')
            spef = (root / (stem + '.detail.spef')).read_text()
            if '*D_NET' not in spef or '*SPEF' not in spef:
                raise ValueError(f'{stem}: malformed/empty SPEF')
            hold = re.search(r'(?ms)^V296_EXTRACTED_MIN_SLACK_BEGIN\r?\n(.*?)^V296_EXTRACTED_MIN_SLACK_END', log)
            if not hold:
                raise ValueError(f'{stem}: no extracted hold block')
            hold_num = re.search(r'(?mi)^worst slack(?:\s+min)?\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*$', hold.group(1))
            if not hold_num:
                raise ValueError(f'{stem}: no finite hold slack')
            row = extract_metric(log, 'extracted_detail')
            row['hold_ns'] = float(hold_num.group(1))
            row['drc'] = int(drc.group(1))
            if not math.isfinite(row['hold_ns']):
                raise ValueError(f'{stem}: invalid hold slack')
            results[scenario][variant] = row
    all_clean = all_timed = all_smaller = all_faster = True
    predictions = True
    comparisons = {}
    for scenario in SCENARIOS:
        rows = results[scenario]
        c = rows['pairwise']
        controls = [rows['original'], rows['optimized']]
        best_area = min(x['area_um2'] for x in controls)
        best_slack = max(x['setup_ns'] for x in controls)
        saving = 100 * (best_area - c['area_um2']) / best_area
        lead = c['setup_ns'] - best_slack
        all_clean &= all(x['slew'] == 0 and x['cap'] == 0 and x['drc'] == 0 for x in rows.values())
        all_timed &= all(x['setup_ns'] >= 0 and x['hold_ns'] >= 0 for x in rows.values())
        all_smaller &= c['area_um2'] < best_area
        all_faster &= c['setup_ns'] > best_slack
        predictions &= saving >= 10 and lead >= 0.20
        comparisons[scenario] = {'area_saving_pct': saving, 'setup_lead_ns': lead, 'variants': rows}
    decision = ('DETAILED_EXTRACTED_PROVISIONAL_PASS' if all_clean and all_timed and all_smaller and all_faster
                else 'DETAILED_RETIRE_V296' if not (all_smaller and all_faster)
                else 'DETAILED_PHYSICAL_GATE_FAIL')
    return {'decision': decision, 'quantitative_prediction_supported': predictions,
            'all_clean': all_clean, 'all_timed': all_timed, 'all_smaller': all_smaller,
            'all_faster': all_faster, 'comparisons': comparisons, 'holdouts': 'SEALED',
            'limitations': 'Ideal-clock pre-CTS hold only; no signoff, power, equal-tile-area baseline or GPU throughput.'}


def self_test():
    sample = ('V296_STAGE_BEGIN extracted_detail\nV296_METRIC stage=extracted_detail '
              'area_um2=5000 slew=0 cap=0\nworst slack max 0.123\n'
              'V296_STAGE_END extracted_detail\n')
    assert extract_metric(sample, 'extracted_detail')['setup_ns'] == 0.123
    for bad in (sample.replace('cap=0', 'cap=oops'), sample.replace('worst slack max 0.123', 'worst slack max nan'),
                sample.replace('V296_STAGE_END extracted_detail', 'V296_STAGE_END routed_third')):
        try:
            extract_metric(bad, 'extracted_detail')
        except ValueError:
            continue
        raise AssertionError('Accepted malformed detailed-route metrics')
    print('V296_DETAIL_AUDIT_SELFTEST_PASS')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--self-test':
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 2:
        raise SystemExit('Usage: audit_detailed_route.py ROOT | --self-test')
    root = Path(sys.argv[1]); root.mkdir(parents=True, exist_ok=True)
    try:
        result = audit(root)
    except (OSError, ValueError) as exc:
        result = {'decision': 'DETAILED_INCOMPLETE_EVIDENCE', 'holdouts': 'SEALED', 'error': str(exc)}
    (root / 'detail_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if result['decision'] != 'DETAILED_EXTRACTED_PROVISIONAL_PASS':
        raise SystemExit(3)
