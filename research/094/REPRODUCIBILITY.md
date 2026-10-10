# Vektor-094 reproduction
Python 3.10+, C++17 g++, Icarus Verilog and Yosys (free) for RTL.

From repository root:

```sh
cd research/094
python3 -m unittest -v test_final_return.py
python3 replicate.py
python3 sweep.py
python3 holdout_c.py
cd ../..
```

RTL smoke tests and generic Yosys synthesis run in .github/workflows/vektor094.yml. GitHub Actions job logs contain actual synthesis counts. The sweep scripts generate raw JSON from fixed seeds; no proprietary data or API keys. Source contract: exactly one FINAL per transaction, no duplicated FINAL, and cold-reset flush. Tests do not establish unbounded formal proof, GPU throughput or physical timing/power.
