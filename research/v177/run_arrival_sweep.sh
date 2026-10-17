#!/usr/bin/env bash
# V177: execute frozen V171/V176 arrival discriminator using V156's own mapped netlists.
set -euo pipefail
test -f build/v156/control_mapped.v
test -f build/v156/cutset_mapped.v
test -f build/v155/summary.json
command -v sta >/dev/null
LIB=build/v155/NangateOpenCellLibrary_typical.lib
test "$(git hash-object "$LIB")" = 90e4afb274cfc6514c587c434c77903d554117d1
mkdir -p build/v156/arrival_sweep
for delay in 0.05 0.5 1 2 3 4 5; do
  for mode in control cutset; do
    if [ "$mode" = control ]; then TOP=vektor_wave32_buffered_baseline; else TOP=vektor_wave32_cutset_pipe; fi
    export VEKTOR_NETLIST="build/v156/${mode}_mapped.v"
    export VEKTOR_TOP="$TOP" VEKTOR_LIB="$LIB" VEKTOR_INPUT_DELAY_NS="$delay"
    log="build/v156/arrival_sweep/${mode}_input_${delay}.log"
    if ! timeout 300s sta -exit research/v176/timing_sweep.tcl > "$log" 2>&1; then
      tail -n 80 "$log" >&2
      exit 1
    fi
    if grep -Eq '^(Error:|Warning:.*(unconstrained|not found))' "$log"; then
      tail -n 80 "$log" >&2
      exit 1
    fi
    grep -q '^Startpoint:' "$log"
    grep -q '^Endpoint:' "$log"
    grep -q '^worst slack' "$log"
  done
done
python3 research/v176/parse_sweep.py build/v156/arrival_sweep build/v155/summary.json > build/v156/arrival_sweep/results.json
python3 research/v177/validate_arrival_sweep.py build/v156/arrival_sweep/results.json build/v156/summary.json > build/v156/arrival_sweep/validation.json
cat build/v156/arrival_sweep/validation.json
