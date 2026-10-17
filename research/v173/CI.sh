#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v173
# Re-execute V156, preserving the historical failed logs in GitHub Actions history.
bash research/v156/CI.sh > build/v173/v156_replay.log 2>&1 || { tail -n 100 build/v173/v156_replay.log; exit 1; }
LIB=build/v155/NangateOpenCellLibrary_typical.lib
test "$(git hash-object "$LIB")" = 90e4afb274cfc6514c587c434c77903d554117d1
for delay in 0.05 0.5 1 2 3 4 5; do
  for mode in control cutset; do
    if [ "$mode" = control ]; then TOP=vektor_wave32_buffered_baseline; else TOP=vektor_wave32_cutset_pipe; fi
    export VEKTOR_NETLIST="build/v156/${mode}_mapped.v"
    export VEKTOR_TOP="$TOP"
    export VEKTOR_LIB="$LIB"
    export VEKTOR_INPUT_DELAY_NS="$delay"
    log="build/v173/${mode}_input_${delay}.log"
    timeout 300s sta -exit research/v173/timing_sweep.tcl > "$log" 2>&1 || { tail -n 70 "$log"; exit 1; }
    if grep -Eq '^Error:|^Warning:.*(unconstrained|not found)' "$log"; then tail -n 70 "$log"; exit 1; fi
    grep -q '^Startpoint:' "$log"
    grep -q '^Endpoint:' "$log"
    grep -q '^worst slack' "$log"
  done
done
python3 research/v173/parse_sweep.py build/v173 build/v155/summary.json > build/v173/sweep_summary.json
python3 -m unittest discover -s research/v173 -p 'test_*.py' -v > build/v173/tests.log 2>&1
cat build/v173/sweep_summary.json
