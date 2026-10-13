"""Exact frozen wildcard cycle checks; no scientific novelty claim."""
import json
import pathlib
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_v147_wildcard():
    results=json.loads(subprocess.check_output([sys.executable,str(ROOT/'research/v147/run_wildcard.py')],text=True,timeout=60))
    frozen=json.loads((ROOT/'research/v147/frozen_cycles.json').read_text())['wildcard']
    assert len(results)==36
    for kind,expected in frozen['cycles_by_kind_latency_stall_low_xor'].items():
        actual=[x['cycles'] for x in results if x['kind']==kind]
        assert [actual[i:i+2] for i in range(0,len(actual),2)]==expected
    assert all(x['retired']==128 and x['fp32_mismatches']==0 for x in results)
