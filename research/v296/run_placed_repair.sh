#!/usr/bin/env bash
# Re-synthesize from identical RTL, then place/repair/route-estimate each matched design.
# Fails closed: physical experiment is incomplete until every variant/RC case is present.
set -euo pipefail
: "${V296_OPENROAD_BIN:?Provide a pinned OpenROAD executable}"
root=build/v296/placed
mkdir -p "$root"
lib=build/v296/nangate.lib
lef=build/v296/platform
test -s "$lib"
for f in "$lef/NangateOpenCellLibrary.tech.lef" "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl"; do test -s "$f"; done
"$V296_OPENROAD_BIN" -version > "$root/openroad.version"
sha256sum "$lib" "$lef/"* > "$root/technology.sha256"
for variant in original optimized pairwise; do
  case "$variant" in
    original) top=vektor_issue_control; src="rtl/vtile/steal_warp_scheduler.sv rtl/vtile/rf_bank_arbiter.sv rtl/vtile/issue_control.sv"; pre="" ;;
    optimized) top=v295_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv"; pre="hierarchy -top v295_issue_core -chparam PREDECODE 0;" ;;
    pairwise) top=v296_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv"; pre="" ;;
  esac
  yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog -sv $src; $pre synth -top $top -flatten; dfflibmap -liberty $lib; abc -liberty $lib; clean; check -assert; write_verilog -noattr -noexpr $root/$variant.v; stat -liberty $lib" > "$root/$variant.synth.log" 2>&1
  test -s "$root/$variant.v"
  for scenario in low nominal high; do
    case "$scenario" in low) rc=0.5 ;; nominal) rc=1.0 ;; high) rc=2.0 ;; esac
    script=research/v296/placed_repair.tcl
    if [[ "$scenario" == nominal ]]; then script=research/v296/fixed_topology_sweep.tcl; fi
    V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
      V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
      V296_TRACKS="$lef/make_tracks.tcl" V296_NETLIST="$root/$variant.v" \
      V296_TOP="$top" V296_VARIANT="$variant" V296_RC_SCALE="$rc" \
      V296_OUT="$root/$variant.$scenario" \
      "$V296_OPENROAD_BIN" -exit "$script" \
      > "$root/$variant.$scenario.log" 2>&1
    grep -q 'V296_PHYSICAL_DONE' "$root/$variant.$scenario.log" || { echo "Incomplete physical gate: $variant/$scenario"; exit 4; }
  done
done
python3 research/v296/audit_fixed_topology.py "$root" || fixed_status=$?
python3 research/v296/audit_placed_repair.py "$root" || physical_status=$?
if [[ ${fixed_status:-0} -ne 0 || ${physical_status:-0} -ne 0 ]]; then exit 3; fi
