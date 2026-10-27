#!/usr/bin/env python3
"""Independent SHA-pinned routed evidence and read-only hold-path replay checker."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ORIGINAL = {
    'pairwise': ('7342c8e1b16b5193279c6d2ad5d15ddb6cb849c9fc0aa06a984297efeef6404b', 0.074236, -0.012622, 12721519936),
    'serial_onehot': ('56781fca03ab151661e2c3c393639caa5e71862358fbbe50e0be1dfc278d6050', -0.751540, -0.009430, 12724948549),
}

def sha(raw): return hashlib.sha256(raw).hexdigest()

def one(path, variant):
    digest, setup, hold, aid = ORIGINAL[variant]
    if sha(path.read_bytes()) != digest: raise ValueError('Artifact SHA mismatch')
    with zipfile.ZipFile(path) as z:
        m = json.loads(z.read('fixed_word_postcts_manifest.json'))
        assert (m['rtl_top'], m['clock_ns'], m['rc_multiplier'], m['placement_density'],
                m['candidate_extra_repair'], m['serial_extra_repair'], m['holdouts']) == (
                'v296_tile_slice_fixed_word', 3.5, 2.0, .45, 0, 1, 'SEALED')
        assert m['same_rtl_for_both'] and m['strongest_serial_fifth_stage_required']
        for name, field in [('cts45_tile.tcl','unchanged_physical_tcl_sha256'),
                            ('run_fixed_word_postcts.sh','derived_runner_sha256'),
                            ('run_bank_decode_postcts.sh','source_runner_sha256')]:
            if sha(z.read(name)) != m[field]: raise ValueError('Modified Tcl/runner')
        inputs = z.read(variant+'.inputs.sha256').decode()
        assert m['source_rtl_sha256']+'  research/v296/v296_tile_slice_fixed_word.sv' in inputs
        assert len(z.read(variant+'.high.cts45.def')) > 1000
        assert len(z.read(variant+'.high.cts45.spef')) > 1000
        assert not z.read(variant+'.high.cts45.drc.rpt').strip()
        assert 'EXIT_CODE=0' in z.read(variant+'.fixed_word_postcts.exit.txt').decode()
        log = z.read(variant+'.high.log').decode(errors='replace')
        for marker in ['V296_CTS45_DONE','V296_CTS45_DRC_COUNT 0','V296_CTS45_IS_ROUTED 1',
                       'V296_CTS45_RC_MULTIPLIER 2.0','V296_CTS45_CLOCKS_PROPAGATED 1',
                       'V296_CTS45_EXTRA_REPAIR '+('0' if variant=='pairwise' else '1')]:
            if log.count(marker)!=1: raise ValueError('Physical marker missing/duplicated '+marker)
        a = json.loads(z.read(variant+'.tile.audit.json'))
        f = a['final']
        if not a['complete'] or a['feasible'] or a['variant']!=variant: raise ValueError('Wrong audit status')
        match = re.search(r'V296_CTS45_HOLD_BEGIN\s+worst slack\s+(-?[\d.]+)\s+V296_CTS45_HOLD_END',log)
        stage = re.search(r'V296_STAGE_BEGIN cts45_extracted\s+V296_METRIC stage=cts45_extracted area_um2=([\d.]+) slew=(\d+) cap=(\d+)\s+worst slack\s+(-?[\d.]+)',log)
        if not match or not stage: raise ValueError('Missing extracted measurement')
        if not (abs(f['setup_ns']-setup)<1e-6 and abs(f['hold_ns']-hold)<1e-6
                and abs(float(match[1])-hold)<1e-6 and abs(float(stage[4])-setup)<1e-6
                and abs(float(stage[1])-f['area_um2'])<1e-6
                and int(stage[2])==f['slew'] and int(stage[3])==f['cap']):
            raise ValueError('Original extracted audit/log disagreement')
        return dict(artifact_id=aid, zip_sha256=digest, area_um2=f['area_um2'],
                    setup_ns=setup, hold_ns=hold, cap=f['cap'], slew=f['slew'], drc=0,
                    feasible=False, fifth_stage_serial_repair=variant=='serial_onehot')

def paired(p, s):
    a,b=one(p,'pairwise'),one(s,'serial_onehot')
    return dict(source_run=40469489684, verdict='BOTH_INFEASIBLE_NO_MATCHED_PARETO',
                contestants={'pairwise':a,'serial_onehot':b},
                area_saving_pct=100*(b['area_um2']-a['area_um2'])/b['area_um2'],
                setup_lead_ps=1000*(a['setup_ns']-b['setup_ns']),
                hold_recovery_min_ps=1000*max(0,-a['hold_ns']),
                setup_deterioration_max_ps=1000*(a['setup_ns']-.05),
                conditional_18v16_overhead_um2_per_candidate_slice=16*b['area_um2']/18-a['area_um2'],
                holdouts='SEALED', signoff=False, gpu_speedup=False)

def replay(log, variant):
    import v296_postroute_sta_replay as base
    if log.splitlines().count('V296_REPLAY_DONE')!=1: raise ValueError('Incomplete replay')
    if log.splitlines().count('V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION')!=1:
        raise ValueError('Wrong evidence tier')
    su=base.worst(base.block(log,'SETUP_WORST'))
    ho=base.worst(base.block(log,'HOLD_WORST'))
    sp=base.paths(base.block(log,'SETUP_PATHS'))
    hp=base.paths(base.block(log,'HOLD_PATHS'))
    _,expected_s,expected_h,aid=ORIGINAL[variant]
    if any(abs(x-y)>.001 for x,y in [(su,expected_s),(ho,expected_h),
                                     (sp[0]['slack_ns'],su),(hp[0]['slack_ns'],ho)]):
        raise ValueError('Original extracted STA not reproduced within 1 ps')
    return dict(verdict='EXTRACTED_HOLD_PATH_REPRODUCED', variant=variant,
                source_run=40469489684, artifact_id=aid, setup_ns=su, hold_ns=ho,
                setup_paths=sp, hold_paths=hp, repair_proven=False, signoff=False)

def selftest():
    sample=('V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION\n'
            'V296_REPLAY_SETUP_WORST_BEGIN\nworst slack 0.074236\nV296_REPLAY_SETUP_WORST_END\n'
            'V296_REPLAY_HOLD_WORST_BEGIN\nworst slack -0.012622\nV296_REPLAY_HOLD_WORST_END\n'
            'V296_REPLAY_SETUP_PATHS_BEGIN\nStartpoint: a/Q\nEndpoint: b/D\n0.074236 slack (MET)\nV296_REPLAY_SETUP_PATHS_END\n'
            'V296_REPLAY_HOLD_PATHS_BEGIN\nStartpoint: c/Q\nEndpoint: d/D\n-0.012622 slack (VIOLATED)\nV296_REPLAY_HOLD_PATHS_END\nV296_REPLAY_DONE\n')
    assert replay(sample,'pairwise')['verdict']=='EXTRACTED_HOLD_PATH_REPRODUCED'
    for bad in [sample.replace('V296_REPLAY_DONE',''),sample.replace('Endpoint: d/D',''),
                sample.replace('worst slack -0.012622','worst slack -0.001000')]:
        try: replay(bad,'pairwise')
        except ValueError: pass
        else: raise AssertionError('Invalid reconstruction accepted')
    print('V296_FIXED_WORD_MATCHED_BOUNDARY_SELFTEST_PASS')

def main():
    ap=argparse.ArgumentParser()
    for name in ('pairwise-zip','serial-zip','output','generate-replay','audit-replay'):
        ap.add_argument('--'+name,type=Path)
    ap.add_argument('--variant',choices=tuple(ORIGINAL))
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    if args.self_test: selftest()
    if args.generate_replay:
        import v296_postroute_sta_replay as base
        assert 'repair_timing ' not in base.TCL and 'detailed_route ' not in base.TCL
        base.generate(args.generate_replay)
    if args.pairwise_zip or args.serial_zip:
        if not args.pairwise_zip or not args.serial_zip: ap.error('Both original ZIPs required')
        result=paired(args.pairwise_zip,args.serial_zip)
        out=json.dumps(result,indent=2,sort_keys=True)+'\n'
        if args.output: args.output.write_text(out)
        print(out)
    if args.audit_replay:
        if not args.variant: ap.error('Variant required')
        try: result=replay(args.audit_replay.read_text(errors='replace'),args.variant)
        except (ValueError,OSError,IndexError) as e:
            result=dict(verdict='NO_EXTRACTED_PATH_ATTRIBUTION',error=str(e),signoff=False)
        out=json.dumps(result,indent=2,sort_keys=True)+'\n'
        if args.output: args.output.write_text(out)
        print(out)
        if result['verdict']!='EXTRACTED_HOLD_PATH_REPRODUCED': raise SystemExit(3)
    if not (args.self_test or args.generate_replay or args.pairwise_zip or args.audit_replay):
        ap.error('Select a mode')
if __name__=='__main__': main()
