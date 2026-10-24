#!/usr/bin/env bash
# Same frozen 65%-density control-advantaged physics; only contestant ordering
# and failure collection differ from run_control_pareto.sh.
# Preregistered: CONTROL_PARETO_65PCT_CONGESTION_FALSIFICATION_20261024.md
set -euo pipefail
: "${V296_OPENROAD_BIN:?Set V296_OPENROAD_BIN to pinned OpenROAD}"
root=build/v296/control_pareto_high
mkdir -p "$root"
lib=build/v296/nangate.lib
lef=build/v296/platform
for f in "$lib" "$lef/NangateOpenCellLibrary.tech.lef" "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl" "$lef/rcx_patterns.rules"; do test -s "$f"; done
"$V296_OPENROAD_BIN" -version > "$root/openroad.version"
sha256sum "$lib" "$lef/"* > "$root/technology.sha256"
failed=0
# Candidate-first prevents a failed control from hiding the candidate's
# own extracted physical result. It does NOT weaken the four-way audit.
for variant in pairwise serial_onehot parallel_onehot original; do
  case "$variant" in
    original) top=vektor_issue_control; src="rtl/vtile/steal_warp_scheduler.sv rtl/vtile/rf_bank_arbiter.sv rtl/vtile/issue_control.sv"; pre=""; extra=1 ;;
    serial_onehot) top=v295_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv"; pre="hierarchy -top v295_issue_core -chparam PREDECODE 0;"; extra=1 ;;
    parallel_onehot) top=v295_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv"; pre="hierarchy -top v295_issue_core -chparam PREDECODE 1;"; extra=1 ;;
    pairwise) top=v296_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv"; pre=""; extra=0 ;;
  esac
  echo "V296_PARETO_COLLECT_VARIANT $variant"
  if ! yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog -sv $src; $pre synth -top $top -flatten; dfflibmap -liberty $lib; abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; clean; check -assert; write_verilog -noattr -noexpr $root/$variant.v; stat -liberty $lib" > "$root/$variant.synth.log" 2>&1; then
    echo "V296_PARETO_SYNTH_FAILURE $variant"
    tail -n 50 "$root/$variant.synth.log"
    failed=$((failed+1))
    continue
  fi
  if ! test -s "$root/$variant.v"; then
    echo "V296_PARETO_EMPTY_NETLIST $variant"
    failed=$((failed+1))
    continue
  fi
  if V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
    V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
    V296_TRACKS="$lef/make_tracks.tcl" V296_RCX_RULES="$lef/rcx_patterns.rules" \
    V296_NETLIST="$root/$variant.v" V296_TOP="$top" V296_RC_SCALE=2.0 \
    V296_DETAIL_RC_MULTIPLIER=2.0 V296_PLACE_DENSITY=0.65 V296_VARIANT="$variant" V296_CONTROL_EXTRA="$extra" \
    V296_OUT="$root/$variant.high" \
    "$V296_OPENROAD_BIN" -exit research/v296/control_advantaged_pareto.tcl \
    > "$root/$variant.high.log" 2>&1; then
    if grep -qx 'V296_PARETO_DONE' "$root/$variant.high.log"; then
      echo "V296_PARETO_COLLECT_DONE $variant"
    else
      echo "V296_PARETO_INCOMPLETE $variant"
      tail -n 50 "$root/$variant.high.log"
      failed=$((failed+1))
    fi
  else
    echo "V296_PARETO_TOOL_FAILURE $variant"
    tail -n 65 "$root/$variant.high.log"
    failed=$((failed+1))
  fi
done
echo "V296_PARETO_COLLECT_FAILURE_COUNT $failed"
# Always invoke the existing independent checker, even on partial evidence.
# Missing physical cases remain a FAIL, never a partial PASS.
audit_rc=0
python3 research/v296/audit_control_pareto.py "$root" || audit_rc=$?
if [ "$failed" -ne 0 ]; then exit 4; fi
exit "$audit_rc"
