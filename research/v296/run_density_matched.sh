#!/usr/bin/env bash
# Matched-floorplan density falsification. Not detailed-route, SPEF, CTS or signoff.
set -euo pipefail
: "${V296_OPENROAD_BIN:?}"
: "${V296_GATE_VARIANT:?}"
: "${V296_GATE_DENSITY:?}"
case "$V296_GATE_DENSITY" in
  d045) density=0.45 ;;
  d065) density=0.65 ;;
  *) echo "INVALID_DENSITY"; exit 2 ;;
esac
variant="$V296_GATE_VARIANT"
case "$variant" in
  original) top=vektor_issue_control; src="rtl/vtile/steal_warp_scheduler.sv rtl/vtile/rf_bank_arbiter.sv rtl/vtile/issue_control.sv"; pre=""; extra=1 ;;
  serial_onehot) top=v295_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv"; pre="hierarchy -top v295_issue_core -chparam PREDECODE 0;"; extra=1 ;;
  pairwise) top=v296_issue_core; src="rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv"; pre=""; extra=0 ;;
  *) echo "INVALID_VARIANT"; exit 2 ;;
esac
root=build/v296/density_gate
stem="$variant.$V296_GATE_DENSITY"
mkdir -p "$root"
lib=build/v296/nangate.lib
lef=build/v296/platform
for f in "$lib" "$lef/NangateOpenCellLibrary.tech.lef" "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl" "$lef/rcx_patterns.rules"; do test -s "$f"; done
"$V296_OPENROAD_BIN" -version > "$root/$stem.openroad.version"
sha256sum "$lib" "$lef/"* research/v296/control_advantaged_pareto.tcl research/v296/cap_margin_repair.tcl research/v296/cap_margin_third.tcl > "$root/$stem.inputs.sha256"
yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog -sv $src; $pre synth -top $top -flatten; dfflibmap -liberty $lib; abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; clean; check -assert; write_verilog -noattr -noexpr $root/$stem.v; stat -liberty $lib" > "$root/$stem.synth.log" 2>&1
test -s "$root/$stem.v"
rc=0
V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
V296_TRACKS="$lef/make_tracks.tcl" V296_RCX_RULES="$lef/rcx_patterns.rules" \
V296_NETLIST="$root/$stem.v" V296_TOP="$top" V296_RC_SCALE=2.0 \
V296_DETAIL_RC_MULTIPLIER=2.0 V296_PLACE_DENSITY="$density" \
V296_VARIANT="$variant" V296_CONTROL_EXTRA="$extra" V296_GLOBAL_GATE_ONLY=1 \
V296_OUT="$root/$stem.high" \
"$V296_OPENROAD_BIN" -exit research/v296/control_advantaged_pareto.tcl \
> "$root/$stem.high.log" 2>&1 || rc=$?
python3 research/v296/audit_density_matched.py --single "$root" "$variant" "$V296_GATE_DENSITY" || exit 3
if [ "$rc" -ne 0 ]; then exit 4; fi
echo "V296_DENSITY_COMPLETE_GLOBAL_ONLY_NOT_SIGNOFF $stem"
