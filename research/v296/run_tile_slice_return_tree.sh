#!/usr/bin/env bash
# Matched V296 balanced-return RF slice post-CTS physical falsification.
set -euo pipefail
: "${V296_OPENROAD_BIN:?Pinned OpenROAD required}"
: "${V296_TILE_VARIANT:?Must select preregistered contestant}"
variant="$V296_TILE_VARIANT"
case "$variant" in
  pairwise) param=1; extra=0 ;;
  serial_onehot) param=0; extra=1 ;;
  *) echo "INVALID_TILE_VARIANT"; exit 2 ;;
esac
root=build/v296/tile_slice
mkdir -p "$root"
python3 research/v296/tile_slice_flow.py --build
lib=build/v296/nangate.lib
lef=build/v296/platform
for f in "$lib" "$lef/NangateOpenCellLibrary.tech.lef" \
  "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl" \
  "$lef/rcx_patterns.rules"; do test -s "$f"; done
"$V296_OPENROAD_BIN" -version > "$root/$variant.openroad.version"
sha256sum "$lib" "$lef/"* research/v296/v296_tile_slice_return_tree.sv \
  research/v296/v296_issue_core.sv research/v295/v295_issue_core.sv \
  "$root/"*.tcl > "$root/$variant.inputs.sha256"
src="rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv research/v295/v295_issue_core.sv research/v296/v296_tile_slice_return_tree.sv"
yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; \
  read_verilog -sv $src; hierarchy -top v296_tile_slice_return_tree -chparam PAIRWISE $param; \
  synth -top v296_tile_slice_return_tree -flatten; dfflibmap -liberty $lib; \
  abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; \
  clean; check -assert; write_verilog -noattr -noexpr $root/$variant.v; \
  stat -liberty $lib" > "$root/$variant.synth.log" 2>&1
test -s "$root/$variant.v"
rc=0
V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
V296_TRACKS="$lef/make_tracks.tcl" V296_RCX_RULES="$lef/rcx_patterns.rules" \
V296_NETLIST="$root/$variant.v" V296_TOP="v296_tile_slice_return_tree" V296_RC_SCALE=2.0 \
V296_DETAIL_RC_MULTIPLIER=2.0 V296_PLACE_DENSITY=0.45 \
V296_VARIANT="$variant" V296_CONTROL_EXTRA="$extra" \
V296_OUT="$root/$variant.high" \
"$V296_OPENROAD_BIN" -exit "$root/cts45_tile.tcl" > "$root/$variant.high.log" 2>&1 || rc=$?
audit_rc=0
python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?
if [ "$rc" -ne 0 ]; then echo "TILE_SLICE_PHYSICAL_TOOL_FAIL variant=$variant exit=$rc"; exit 4; fi
if [ "$audit_rc" -ne 0 ]; then echo "TILE_SLICE_INCOMPLETE variant=$variant"; exit 3; fi
echo "TILE_SLICE_POSTCTS_EXTRACTED_COMPLETE $variant"
