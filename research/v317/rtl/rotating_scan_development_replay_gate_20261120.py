#!/usr/bin/env python3
"""Independent reproducibility gate for frozen V317 development result.

Only development seeds are used. Never run the reserved --holdout option.
The source-under-test is imported from the checked-out repository.
"""
import importlib.util
import math
from pathlib import Path

path=Path(__file__).with_name("rotating_scan_prospective_20261120.py")
spec=importlib.util.spec_from_file_location("v317_candidate",path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
seeds=range(20261121,20261125)
result=mod.evaluate(seeds)
assert result["n"]==60
assert len(result["rows"])==60
assert all(row["seed"] in seeds for row in result["rows"])
assert all(row["compact"]["offered"]==row["rotating"]["offered"] for row in result["rows"])
assert all(row["compact"]["admitted"]+row["compact"]["dropped"]==row["compact"]["offered"] for row in result["rows"])
assert all(row["rotating"]["admitted"]+row["rotating"]["dropped"]==row["rotating"]["offered"] for row in result["rows"])
assert all(row["compact"]["completed"]+row["compact"]["remaining"]==row["compact"]["admitted"] for row in result["rows"])
assert all(row["rotating"]["completed"]+row["rotating"]["remaining"]==row["rotating"]["admitted"] for row in result["rows"])
expected=(0.999934767939798,0.9983679686649983,1.001493103284827)
observed=(result["geomean"],result["min_ratio"],result["max_ratio"])
for actual,reference in zip(observed,expected):
    assert math.isclose(actual,reference,rel_tol=1e-11,abs_tol=1e-11),(actual,reference)
assert result["max_ratio"]<1.02
print("V317 DEVELOPMENT REPLAY PASS: n=60; geometric mean, minimum and maximum match frozen report")
print("geomean=%.15f min=%.15f max=%.15f"%observed)
print("HOLDOUT UNOPENED; candidate remains NO-GO")
