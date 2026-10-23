#!/usr/bin/env bash
# Reproduce only V296/high RC in the original live OpenROAD state; no repairs after route.
set -euo pipefail
: "${V296_OPENROAD_BIN:?Set V296_OPENROAD_BIN to pinned OpenROAD}"
root=build/v296/live_endpoint
mkdir -p "$root"
lib=build/v296/nangate.lib
lef=build/v296/platform
for f in "$lib" "$lef/NangateOpenCellLibrary.tech.lef" "$lef/NangateOpenCellLibrary.macro.mod.lef" "$lef/make_tracks.tcl" "$lef/rcx_patterns.rules"; do test -s "$f"; done
"$V296_OPENROAD_BIN" -version > "$root/openroad.version"
sha256sum "$lib" "$lef/"* > "$root/technology.sha256"
yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog -sv rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv; synth -top v296_issue_core -flatten; dfflibmap -liberty $lib; abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; clean; check -assert; write_verilog -noattr -noexpr $root/pairwise.v; stat -liberty $lib" > "$root/pairwise.synth.log" 2>&1
test -s "$root/pairwise.v"
V296_LIB="$lib" V296_TECH_LEF="$lef/NangateOpenCellLibrary.tech.lef" \
  V296_CELL_LEF="$lef/NangateOpenCellLibrary.macro.mod.lef" \
  V296_TRACKS="$lef/make_tracks.tcl" V296_RCX_RULES="$lef/rcx_patterns.rules" \
  V296_NETLIST="$root/pairwise.v" V296_TOP=v296_issue_core V296_RC_SCALE=2.0 \
  V296_DETAIL_RC_MULTIPLIER=2.0 V296_OUT="$root/pairwise.high" \
  "$V296_OPENROAD_BIN" -exit research/v296/high_rc_live_endpoint.tcl \
  > "$root/replay.log" 2>&1 || {
    echo "V296_LIVE_ENDPOINT_TOOL_FAILURE"
    tail -n 60 "$root/replay.log"
    exit 4
  }
grep -q '^V296_DETAILED_PHYSICAL_DONE$' "$root/replay.log"
grep -q '^V296_DETAIL_DRC_COUNT 0$' "$root/replay.log"
grep -q '^V296_DETAIL_IS_ROUTED 1$' "$root/replay.log"
python3 research/v296/audit_slew_forensics.py "$root" "$root/replay.log"
