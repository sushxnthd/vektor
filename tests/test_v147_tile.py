"""V147 reproducible Wave32 FP32 tile-model holdout; simulator CI runs pytest."""
import ctypes
import importlib.util
import json
import pathlib
import random
import struct
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
DIR=ROOT/'research/v147'
def test_v147_holdout_cycles_and_fp32():
    records=json.loads(subprocess.check_output([sys.executable,str(DIR/'fma_tile_model.py'),'--holdout'],text=True,timeout=60))
    frozen=json.loads((DIR/'frozen_cycles.json').read_text())
    assert len(records)==120
    assert all(x['retired']==x['count'] and x['fp32_mismatches']==0 for x in records)
    assert sum(x['fp32_lanes'] for x in records)==432604
    for kind,values in frozen['holdout'].items():
        got=[x['cycles'] for x in records if x['kind']==kind]
        assert got==values,(kind,got,values)
    def speedup(kind):
        base=[x['cycles'] for x in records if x['kind']==kind and x['ports']==2 and x['bank_map']=='low']
        alt=[x['cycles'] for x in records if x['kind']==kind and x['ports']==2 and x['bank_map']=='xor']
        return sum(x/y for x,y in zip(base,alt))/len(base)
    assert speedup('bankhot_indep')>=1.10
    assert .95<=speedup('bankhot')<1.05
    assert all(speedup(k)>=.98 for k in ('chain','independent','divergent','mixed'))
    assert all(sum((reg&15)==b for reg in range(64))==4 and sum(((reg^(reg>>4))&15)==b for reg in range(64))==4 for b in range(16))

def test_v147_fma_against_native():
    spec=importlib.util.spec_from_file_location('fma147',DIR/'fma_oracle.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    libm=ctypes.CDLL('libm.so.6')
    libm.fmaf.argtypes=[ctypes.c_float]*3
    libm.fmaf.restype=ctypes.c_float
    def f(x):return struct.unpack('<f',struct.pack('<I',x))[0]
    def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
    rng=random.Random(147)
    for _ in range(2048):
        a,b,c=(rng.getrandbits(32) for _ in range(3))
        got=module.fma_bits(a,b,c)[0]
        expected=bits(libm.fmaf(f(a),f(b),f(c)))
        if expected&0x7f800000==0x7f800000 and expected&0x7fffff:expected=0x7fc00000
        assert got==expected,(hex(a),hex(b),hex(c),hex(got),hex(expected))
