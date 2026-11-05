#!/usr/bin/env python3
"""V309 QV100-SASS DRAM-latency counterfactual. Simulator sensitivity only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from legacy_qv100_runtime import simulate
from qv100_runtime_counter_audit import audit

BASE = 100
VARIANTS = (200, 400)
ACTIVE = re.compile(r'(?m)^([ \t]*-dram_latency[ \t]+)([0-9]+)([ \t]*(?:#.*)?)$')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def perturb(blob, value):
    if value not in VARIANTS:
        raise ValueError('unfrozen DRAM latency')
    source = blob.decode('utf-8')
    found = list(ACTIVE.finditer(source))
    if len(found) != 1 or int(found[0].group(2)) != BASE:
        raise ValueError('missing, duplicate or changed pinned DRAM latency')
    m = found[0]
    modified = source[:m.start(2)] + str(value) + source[m.end(2):]
    if modified[:m.start(2)] != source[:m.start(2)] or modified[m.start(2)+len(str(value)):] != source[m.end(2):]:
        raise ValueError('non-latency config mutation')
    return modified.encode('utf-8')

def prepare(config, folder):
    source = Path(config).read_bytes()
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for value in VARIANTS:
        filename = 'dram-%d.config' % value
        target = folder / filename
        if target.exists():
            raise ValueError('refusing to overwrite frozen config')
        data = perturb(source, value)
        target.write_bytes(data)
        rows.append({'dram_latency': value, 'filename': filename, 'sha256': sha(data)})
    manifest = {'source_config_sha256': sha(source), 'baseline_dram_latency': BASE,
                'variants': rows, 'changed_option_only': '-dram_latency',
                'preregistered_prediction': 'raising DRAM latency should not reduce total cycles; a nonpositive cycle response falsifies latency dominance on this workload',
                'physical_speedup_claim_allowed': False}
    (folder / 'latency-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    return manifest

def verify(folder, source=None):
    folder = Path(folder)
    manifest = json.loads((folder / 'latency-manifest.json').read_text())
    if manifest['baseline_dram_latency'] != BASE or [r['dram_latency'] for r in manifest['variants']] != list(VARIANTS):
        raise ValueError('frozen experiment identity changed')
    if source is not None and sha(source) != manifest['source_config_sha256']:
        raise ValueError('baseline config changed')
    for row in manifest['variants']:
        if row['filename'] != 'dram-%d.config' % row['dram_latency']:
            raise ValueError('unexpected config filename')
        data = (folder / row['filename']).read_bytes()
        if sha(data) != row['sha256']:
            raise ValueError('variant changed after freeze')
        if source is not None and data != perturb(source, row['dram_latency']):
            raise ValueError('unapproved config mutation')
    return manifest

def execute(binary, trace, gpgpu, trace_config, selection, folder, evidence):
    manifest = verify(folder, Path(gpgpu).read_bytes())
    results = []
    for row in manifest['variants']:
        latency = row['dram_latency']
        result = simulate(binary, trace, Path(folder) / row['filename'], trace_config,
                          Path(evidence) / ('dram-%d' % latency), selection)
        results.append({'dram_latency': latency, 'status': result['status']})
    if any(r['status'] != 'PASS_RUNTIME' for r in results):
        raise ValueError('one or more perturbed simulations failed')
    return results

def summarize(base, variants):
    cycles = base['total_sim_cycles']
    insns = base['total_sim_instructions']
    launches = base['expected_launches']
    if min(cycles, insns, launches) <= 0:
        raise ValueError('invalid baseline')
    rows = []
    for latency, result in variants:
        if result['total_sim_instructions'] != insns or result['expected_launches'] != launches:
            raise ValueError('unmatched workload instructions or launches')
        c = result['total_sim_cycles']
        rows.append({'dram_latency': latency, 'sim_cycles': c,
                     'cycle_delta': c-cycles, 'cycle_delta_percent': 100*(c/cycles-1),
                     'L1D_misses_sim_counter': result['cumulative_counter_totals']['L1D_total_cache_misses'],
                     'L2_misses_sim_counter': result['cumulative_counter_totals']['L2_total_cache_misses']})
    return {'status': 'PASS_INDEPENDENT_SENSITIVITY_AUDIT',
            'baseline_sim_cycles': cycles, 'baseline_sim_instructions': insns,
            'baseline_L2_misses_sim_counter': base['cumulative_counter_totals']['L2_total_cache_misses'],
            'variants': rows, 'predicted_positive_latency_response': all(r['cycle_delta'] > 0 for r in rows),
            'strictly_monotone_cycles': all(rows[i]['sim_cycles'] > (cycles if i == 0 else rows[i-1]['sim_cycles']) for i in range(len(rows))),
            'hardware_calibrated': False, 'physical_speedup_demonstrated': False,
            'claim_boundary': 'one original trace-driven workload; only simulator DRAM-latency perturbation, no hardware calibration, no architectural speedup'}

def inspect(folder, evidence, selection):
    manifest = verify(folder)
    evidence = Path(evidence)
    def load(path):
        return audit((path/'repeat-1.log').read_bytes(), (path/'repeat-2.log').read_bytes(), selection['kernel_launches'])
    base = load(evidence)
    variants = [(r['dram_latency'], load(evidence / ('dram-%d' % r['dram_latency']))) for r in manifest['variants']]
    result = summarize(base, variants)
    result['raw_log_sha256'] = {'baseline': base['raw_log_sha256'],
                                **{str(k):v['raw_log_sha256'] for k,v in variants}}
    result['frozen_prediction'] = manifest['preregistered_prediction']
    result['manifest_sha256'] = sha((Path(folder)/'latency-manifest.json').read_bytes())
    return result

def selftest():
    source = b'# -dram_latency 900\n-dram_latency 100\n-gpgpu_cache:dl2 S:32:128:24\n'
    for value in VARIANTS:
        assert perturb(source,value) == source.replace(b'-dram_latency 100', ('-dram_latency %d'%value).encode())
    for bad in [source+b'-dram_latency 100\n',source.replace(b'100',b'101'),
                b'# -dram_latency 100\n',source.replace(b'100',b'100x')]:
        try: perturb(bad,200)
        except ValueError: pass
        else: raise AssertionError('bad configuration accepted')
    def result(c, i=100, n=2):
        return {'total_sim_cycles':c,'total_sim_instructions':i,'expected_launches':n,
                'cumulative_counter_totals':{'L1D_total_cache_misses':10,'L2_total_cache_misses':5}}
    assert summarize(result(100),[(200,result(110)),(400,result(130))])['strictly_monotone_cycles']
    assert not summarize(result(100),[(200,result(99)),(400,result(105))])['predicted_positive_latency_response']
    for bad in [result(110,99),result(110,100,3)]:
        try: summarize(result(100),[(200,bad)])
        except ValueError: pass
        else: raise AssertionError('unmatched workload accepted')
    return {'status':'PASS','positive_controls':4,'negative_controls':6}

def main():
    p=argparse.ArgumentParser()
    for flag in ('selftest','run','audit'): p.add_argument('--'+flag,action='store_true')
    for name in ('prepare','folder','binary','trace','gpgpu','trace-config','selection','evidence','out'):
        p.add_argument('--'+name)
    a=p.parse_args()
    if a.selftest: result=selftest()
    elif a.prepare: result=prepare(a.prepare,a.folder)
    elif a.run: result=execute(a.binary,a.trace,a.gpgpu,a.trace_config,json.loads(Path(a.selection).read_text()),a.folder,a.evidence)
    elif a.audit:
        result=inspect(a.folder,a.evidence,json.loads(Path(a.selection).read_text()))
        Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: p.error('choose --selftest, --prepare, --run, or --audit')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
