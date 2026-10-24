#!/usr/bin/env bash
# Preregistered fixed 40%-margin post-CTS repair, matched contestants.
set -euo pipefail
: "${V296_OPENROAD_BIN:?Pinned OpenROAD binary required}"
: "${V296_CTS45_VARIANT:?Contestant required}"
variant="$V296_CTS45_VARIANT"
case "$variant" in
  pairwise) top=v296_issue_core; src='rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv'; pre=''; extra=0 ;;
  serial_onehot) top=v295_issue_core; src='rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv'; pre='hierarchy -top v295_issue_core -chparam PREDECODE 0;'; extra=1 ;;
  *) echo INVALID_VARIANT; exit 2 ;;
esac
root=build/v296/cts45_slew40
mkdir -p "$root"
lib=build/v296/nangate.lib
lef=build/v296/platform
for f in "$lib" "$lef/NangateOpenCellLibrary.tech.lef" "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl" "$lef/rcx_patterns.rules"; do test -s "$f"; done
"$V296_OPENROAD_BIN" -version > "$root/$variant.openroad.version"
sha256sum "$lib" "$lef/"* research/v296/cts45_slew40.tcl research/v296/cap_margin_third.tcl research/v296/cap_margin_repair.tcl > "$root/$variant.inputs.sha256"
yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog -sv $src; $pre synth -top $top -flatten; dfflibmap -liberty $lib; abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; clean; check -assert; write_verilog -noattr -noexpr $root/$variant.v; stat -liberty $lib" > "$root/$variant.synth.log" 2>&1
test -s "$root/$variant.v"
rc=0
V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
V296_TRACKS="$lef/make_tracks.tcl" V296_RCX_RULES="$lef/rcx_patterns.rules" \
V296_NETLIST="$root/$variant.v" V296_TOP="$top" V296_RC_SCALE=2.0 \
V296_DETAIL_RC_MULTIPLIER=2.0 V296_PLACE_DENSITY=0.45 \
V296_VARIANT="$variant" V296_CONTROL_EXTRA="$extra" \
V296_OUT="$root/$variant.high" \
"$V296_OPENROAD_BIN" -exit research/v296/cts45_slew40.tcl > "$root/$variant.high.log" 2>&1 || rc=$?
audit_rc=0
python3 research/v296/audit_cts45_slew40.py --single "$root" "$variant" || audit_rc=$?
if [ "$rc" -ne 0 ]; then echo "CTS45_TOOL_INCOMPLETE $variant exit=$rc"; exit 4; fi
if [ "$audit_rc" -ne 0 ]; then echo "CTS45_AUDIT_INCOMPLETE $variant"; exit 3; fi
echo "CTS45_SLEW40_COMPLETE_PROPAGATED_CLOCK_EXTRACTED $variant"
