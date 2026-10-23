#!/usr/bin/env bash
# Prospective three-way high-RC fourth-round electrical-repair experiment.
# See FOURTH_ROUND_HIGH_RC_PREREG_20261024.md.
set -euo pipefail
: "${V296_OPENROAD_BIN:?Set V296_OPENROAD_BIN to pinned OpenROAD}"
root=build/v296/fourth_high
mkdir -p "$root"
lib=build/v296/nangate.lib
lef=build/v296/platform
for f in "$lib" "$lef/NangateOpenCellLibrary.tech.lef" "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl" "$lef/rcx_patterns.rules"; do
  test -s "$f"
done
"$V296_OPENROAD_BIN" -version > "$root/openroad.version"
sha256sum "$lib" "$lef/"* > "$root/technology.sha256"
for variant in original optimized pairwise; do
  case "$variant" in
    original) top=vektor_issue_control; src="rtl/vtile/steal_warp_scheduler.sv rtl/vtile/rf_bank_arbiter.sv rtl/vtile/issue_control.sv"; pre="" ;;
    optimized) top=v295_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv"; pre="hierarchy -top v295_issue_core -chparam PREDECODE 0;" ;;
    pairwise) top=v296_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv"; pre="" ;;
  esac
  yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog -sv $src; $pre synth -top $top -flatten; dfflibmap -liberty $lib; abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; clean; check -assert; write_verilog -noattr -noexpr $root/$variant.v; stat -liberty $lib" > "$root/$variant.synth.log" 2>&1
  test -s "$root/$variant.v"
  V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
    V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
    V296_TRACKS="$lef/make_tracks.tcl" V296_RCX_RULES="$lef/rcx_patterns.rules" \
    V296_NETLIST="$root/$variant.v" V296_TOP="$top" V296_RC_SCALE=2.0 \
    V296_DETAIL_RC_MULTIPLIER=2.0 V296_OUT="$root/$variant.high" \
    "$V296_OPENROAD_BIN" -exit research/v296/fourth_round_high_rc.tcl \
    > "$root/$variant.high.log" 2>&1 || {
      echo "V296_FOURTH_TOOL_FAILURE $variant"
      tail -n 65 "$root/$variant.high.log"
      exit 4
    }
  grep -q '^V296_FOURTH_DONE$' "$root/$variant.high.log" || {
    echo "V296_FOURTH_INCOMPLETE $variant"
    exit 4
  }
done
python3 research/v296/audit_fourth_high_rc.py "$root"
