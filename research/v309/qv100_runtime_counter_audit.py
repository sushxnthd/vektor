#!/usr/bin/env python3
"""Independent V309 QV100-SASS per-kernel counter audit.

Reads raw unmodified simulator logs, never invents hardware counters or speedups.
Only named cumulative simulator counters are differenced between kernel records.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

PER_KERNEL = ('gpu_sim_cycle', 'gpu_sim_insn')
CUMULATIVE = ('gpu_tot_sim_cycle', 'gpu_tot_sim_insn',
              'L1D_total_cache_misses', 'L2_total_cache_misses',
              'gpgpu_n_mem_read_global', 'gpgpu_n_mem_write_global')
FIELDS = PER_KERNEL + CUMULATIVE


def sha(data):
    return hashlib.sha256(data).hexdigest()


def extract(log):
    if 'GPGPU-Sim: *** exit detected ***' not in log:
        raise ValueError('missing simulator completion marker')
    starts = list(re.finditer(r'(?m)^kernel_name\s*=\s*(\S+)\s*$', log))
    if not starts:
        raise ValueError('no kernel records')
    rows = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(log)
        block = log[match.end():end]
        record = {'kernel_name': match.group(1)}
        for key in ('kernel_launch_uid',) + FIELDS:
            found = re.findall(r'(?m)^\s*' + re.escape(key) + r'\s*=\s*(\d+)\s*$', block)
            if len(found) != 1:
                raise ValueError('missing/duplicate counter: %s, record %d, found %d' %
                                 (key, index + 1, len(found)))
            record[key] = int(found[0])
        if record['kernel_launch_uid'] != index + 1:
            raise ValueError('launch UID not sequential')
        if any(record[k] <= 0 for k in PER_KERNEL):
            raise ValueError('nonpositive per-kernel cycle/instruction count')
        rows.append(record)
    prior = {k: 0 for k in CUMULATIVE}
    for row in rows:
        delta = {}
        for key in CUMULATIVE:
            value = row[key] - prior[key]
            if value < 0:
                raise ValueError('cumulative counter regressed: ' + key)
            delta[key] = value
            prior[key] = row[key]
        if delta['gpu_tot_sim_cycle'] != row['gpu_sim_cycle']:
            raise ValueError('kernel cycles disagree with cumulative cycle delta')
        if delta['gpu_tot_sim_insn'] != row['gpu_sim_insn']:
            raise ValueError('kernel instructions disagree with cumulative instruction delta')
        row['increments'] = delta
    return rows


def audit(a_bytes, b_bytes, expected_launches):
    a, b = extract(a_bytes.decode('utf-8', 'replace')), extract(b_bytes.decode('utf-8', 'replace'))
    if len(a) != expected_launches or len(b) != expected_launches:
        raise ValueError('launch count differs from preregistered manifest')
    if a != b:
        raise ValueError('repeat kernel/counter vectors disagree')
    totals = a[-1]
    if totals['gpu_tot_sim_cycle'] <= 0 or totals['gpu_tot_sim_insn'] <= 0:
        raise ValueError('zero aggregate cycles or instructions')
    return {
        'status': 'PASS_INDEPENDENT_SIMULATOR_COUNTER_REPLAY',
        'evidence_tier': 'pinned_accel_sim_QV100_SASS_only_not_hardware',
        'raw_log_sha256': [sha(a_bytes), sha(b_bytes)],
        'raw_log_identical': a_bytes == b_bytes,
        'semantic_kernel_counters_identical': True,
        'expected_launches': expected_launches,
        'kernel_records': a,
        'total_sim_cycles': totals['gpu_tot_sim_cycle'],
        'total_sim_instructions': totals['gpu_tot_sim_insn'],
        'cumulative_counter_totals': {k: totals[k] for k in CUMULATIVE},
        'hardware_validated': False,
        'architecture_speedup_permitted': False,
    }



def validate_selection(selection):
    """Accept only preregistered original-source selection ranks, never hardware claims."""
    status = selection.get('status')
    if status == 'SELECTED_INPUT_ONLY':
        if selection.get('selection_rank_one_based', 1) != 1:
            raise ValueError('rank-one manifest has conflicting rank')
    elif status == 'SECOND_WORKLOAD_SELECTED_INPUT_ONLY':
        if (selection.get('selection_rank_one_based') != 2 or
                selection.get('complete_candidate_count', 0) < 2 or
                not selection.get('first_workload_list') or
                selection.get('first_workload_list') == selection.get('selected_list')):
            raise ValueError('rank-two manifest has invalid prospective selection')
    else:
        raise ValueError('not an original selected input manifest')
    if (not isinstance(selection.get('selected_list'), str) or
            not selection['selected_list'].endswith('/kernelslist.g') or
            type(selection.get('kernel_launches')) is not int or
            selection['kernel_launches'] <= 0 or
            selection.get('hardware_validated') is not False or
            selection.get('architecture_speedup_permitted') is not False):
        raise ValueError('selection identity, launch count or evidence tier invalid')
    return selection['kernel_launches']


def fixture(rows, marker=True):
    parts = []
    for row in rows:
        parts.append('kernel_name = %s\n' % row['kernel_name'])
        for key in ('kernel_launch_uid',) + FIELDS:
            parts.append('%s = %d\n' % (key, row[key]))
    if marker:
        parts.append('GPGPU-Sim: *** exit detected ***\n')
    return ''.join(parts).encode()


def selftest():
    a = {'kernel_name': 'k', 'kernel_launch_uid': 1, 'gpu_sim_cycle': 7,
         'gpu_sim_insn': 14, 'gpu_tot_sim_cycle': 7, 'gpu_tot_sim_insn': 14,
         'L1D_total_cache_misses': 3, 'L2_total_cache_misses': 2,
         'gpgpu_n_mem_read_global': 5, 'gpgpu_n_mem_write_global': 1}
    b = dict(a, kernel_launch_uid=2, gpu_sim_cycle=8, gpu_sim_insn=16,
             gpu_tot_sim_cycle=15, gpu_tot_sim_insn=30,
             L1D_total_cache_misses=5, L2_total_cache_misses=2,
             gpgpu_n_mem_read_global=8, gpgpu_n_mem_write_global=2)
    raw = fixture([a, b])
    result = audit(raw, raw + b'elapsed_seconds = 2\n', 2)
    assert result['kernel_records'][1]['increments']['L1D_total_cache_misses'] == 2
    assert not result['raw_log_identical']
    bad = [
        (raw, fixture([a, dict(b, gpu_sim_cycle=9)]), 2),
        (fixture([a, dict(b, gpu_tot_sim_cycle=14)]), raw, 2),
        (fixture([a, dict(b, L2_total_cache_misses=1)]), raw, 2),
        (fixture([a, dict(b, kernel_launch_uid=1)]), raw, 2),
        (fixture([a, b], marker=False), raw, 2),
        (raw, raw, 3),
        (fixture([a, b]).replace(b'gpu_sim_cycle = 7\n', b''), raw, 2),
        (fixture([a, b]).replace(b'gpu_sim_cycle = 7\n', b'gpu_sim_cycle = 7\ngpu_sim_cycle = 7\n'), raw, 2),
    ]
    for x, y, n in bad:
        try:
            audit(x, y, n)
        except ValueError:
            continue
        raise AssertionError('adversarial control accepted')
    # The rank-two manifest was previously rejected despite successful simulation.
    first = {'status': 'SELECTED_INPUT_ONLY', 'selected_list': 'x/kernelslist.g',
             'kernel_launches': 2, 'hardware_validated': False,
             'architecture_speedup_permitted': False}
    second = dict(first, status='SECOND_WORKLOAD_SELECTED_INPUT_ONLY',
                  selection_rank_one_based=2, complete_candidate_count=11,
                  first_workload_list='a/kernelslist.g')
    assert validate_selection(first) == 2
    assert validate_selection(second) == 2
    manifest_bad = [
        dict(second, selection_rank_one_based=1),
        dict(second, complete_candidate_count=1),
        dict(second, first_workload_list=second['selected_list']),
        dict(second, hardware_validated=True),
        dict(second, kernel_launches=0),
        dict(second, selected_list='forged'),
        dict(first, status='UNVERIFIED_INPUT'),
        dict(first, selection_rank_one_based=2),
    ]
    for manifest in manifest_bad:
        try:
            validate_selection(manifest)
        except ValueError:
            continue
        raise AssertionError('forged selection manifest accepted')
    return {'status': 'PASS', 'positive_controls': 4,
            'negative_controls': len(bad) + len(manifest_bad)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--selftest', action='store_true')
    p.add_argument('--repeat1')
    p.add_argument('--repeat2')
    p.add_argument('--selection')
    p.add_argument('--out')
    a = p.parse_args()
    if a.selftest:
        result = selftest()
    else:
        if not all([a.repeat1, a.repeat2, a.selection, a.out]):
            p.error('provide two raw repeat logs, original selection.json and --out')
        selection = json.loads(Path(a.selection).read_text())
        expected_launches = validate_selection(selection)
        result = audit(Path(a.repeat1).read_bytes(), Path(a.repeat2).read_bytes(),
                       expected_launches)
        result['selected_list'] = selection['selected_list']
        Path(a.out).write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
