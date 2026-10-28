#!/usr/bin/env python3
"""SHA-pinned original routed ZIP stage forensics; no timing pass inferred."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path

ARTIFACTS = {
    'D4_serial': ('bc0186f9e5efb507d642db5de0d94f0d11b3393f554fdd280f6fa05b5820e702', 12800782354),
    'D8_serial': ('bc7fa45750d38121e9512557f0cda41ae7e219ac498a4ad361d97499daf07b16', 12804941948),
}
MARKER = re.compile(r'^(V296_(?:CTS45|HOLD25|STAGE|METRIC|DEFERRED|TILE)[^\r\n]*)$', re.M)
STAGE = re.compile(r'^V296_METRIC stage=(\S+) area_um2=([\d.]+) slew=(\d+) cap=(\d+)', re.M)

def parse(log):
    markers=MARKER.findall(log)
    stages=[{'stage':m.group(1),'area_um2':float(m.group(2)),
             'slew':int(m.group(3)),'cap':int(m.group(4))} for m in STAGE.finditer(log)]
    checks=['V296_CTS45_FOURTH_DONE','V296_CTS45_FIFTH_DONE',
            'V296_CTS45_CTS_BEGIN','V296_CTS45_CTS_END',
            'V296_CTS45_DETAIL_BEGIN','V296_CTS45_DONE']
    return {'marker_count':len(markers),'last_markers':markers[-30:],
            'last_stage':stages[-1] if stages else None,
            'stages':stages,
            'checkpoints':{x:x in log for x in checks},
            'last_log_lines':log.splitlines()[-12:]}

def audit(paths):
    rows={}
    for label,path in paths.items():
        raw=Path(path).read_bytes(); digest=hashlib.sha256(raw).hexdigest()
        if digest != ARTIFACTS[label][0]: raise ValueError(label+' ZIP SHA mismatch')
        with zipfile.ZipFile(path) as z:
            log=z.read('serial_onehot.high.log').decode('utf-8','replace')
            exittext=z.read('serial_onehot.deferred_routed.exit.txt').decode().strip()
        expected='EXIT_CODE=0' if label=='D4_serial' else 'EXIT_CODE=124'
        if exittext != expected: raise ValueError(label+' unexpected exit '+exittext)
        rows[label]={'original_artifact_id':ARTIFACTS[label][1],
                     'original_zip_sha256':digest,'original_exit':exittext,**parse(log)}
    d8=rows['D8_serial']; d4=rows['D4_serial']
    d8_check=d8['checkpoints']
    if d8_check['V296_CTS45_DONE']:
        classification='POST_ROUTE_RUNNER_TIMEOUT_OR_AFTER_MARKER'
    elif d8_check['V296_CTS45_DETAIL_BEGIN']:
        classification='DURING_DETAILED_ROUTE_OR_LATER_UNMARKED_STEP'
    elif d8_check['V296_CTS45_CTS_END']:
        classification='AFTER_CTS_BEFORE_DETAIL_MARKER'
    elif d8_check['V296_CTS45_CTS_BEGIN']:
        classification='DURING_CTS_OR_UNMARKED_STEP'
    elif d8_check['V296_CTS45_FIFTH_DONE']:
        classification='AFTER_SERIAL_FIFTH_BEFORE_CTS'
    else:
        classification='BEFORE_SERIAL_FIFTH_COMPLETION_OR_UNMARKED'
    return {'source_run':40646515864,'source_commit':'84245c21f485c191aea7d352652c0ef036d6d047',
            'comparison':rows,'D8_timeout_stage_classification':classification,
            'evidence_tier':'ORIGINAL_SHA_PINNED_LOG_FORENSICS_NOT_PHYSICAL_PASS',
            'matched_feasibility':False,'gpu_speedup_established':False}

def selftest():
    x=parse('V296_CTS45_FIFTH_DONE\nV296_METRIC stage=cts area_um2=123 slew=0 cap=0\n')
    assert x['last_stage']['stage']=='cts'
    assert x['checkpoints']['V296_CTS45_FIFTH_DONE']
    assert not x['checkpoints']['V296_CTS45_CTS_END']
    print('V296_D8_TIMEOUT_STAGE_SELFTEST_PASS')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true')
    p.add_argument('--d4',type=Path);p.add_argument('--d8',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.self_test:selftest()
    if a.d4 or a.d8:
        if not a.d4 or not a.d8: p.error('Both original ZIPs required')
        result=audit({'D4_serial':a.d4,'D8_serial':a.d8})
        body=json.dumps(result,indent=2,sort_keys=True)+'\n'
        if a.out:a.out.write_text(body)
        print(body)
    elif not a.self_test:p.error('Choose --self-test or both ZIPs')
