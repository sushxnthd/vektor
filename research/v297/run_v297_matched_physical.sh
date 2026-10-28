#!/usr/bin/env bash
# Matched physical macro: no per-policy constraint changes or adaptive repair.
set -euo pipefail
: "${V297_VARIANT:?}"
: "${V297_OPENROAD_BIN:?}"
case "$V297_VARIANT" in
  compact) policy=0 ;;
  maxpair) policy=1 ;;
  rotating) policy=2 ;;
  *) echo "V297_INVALID_VARIANT"; exit 2 ;;
esac
root=build/v297/physical
platform=build/v297/platform
mkdir -p "$root"
lib=build/v297/nangate.lib
for f in "$lib" "$platform/NangateOpenCellLibrary.tech.lef" "$platform/NangateOpenCellLibrary.macro.mod.lef" "$platform/make_tracks.tcl" "$platform/rcx_patterns.rules"; do test -s "$f"; done
"$V297_OPENROAD_BIN" -version > "$root/$V297_VARIANT.openroad.version"
sha256sum "$lib" "$platform/"* research/v297/v297_matched_physical.tcl research/v297/rtl/v297_matched_shell.v research/v297/rtl/v297_maxpair_cooldown_core.v research/v297/rtl/v297_maxpair_core.v research/v297/rtl/v297_rotating_static_core.v > "$root/$V297_VARIANT.inputs.sha256"
yosys -Q -T -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; read_verilog research/v297/rtl/v297_matched_shell.v research/v297/rtl/v297_maxpair_cooldown_core.v research/v297/rtl/v297_maxpair_core.v research/v297/rtl/v297_rotating_static_core.v; hierarchy -top v297_matched_shell -chparam POLICY $policy; synth -top v297_matched_shell -flatten; dfflibmap -liberty $lib; abc -liberty $lib; hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z; clean; check -assert; write_verilog -noattr -noexpr $root/$V297_VARIANT.v; stat -liberty $lib" > "$root/$V297_VARIANT.synth.log" 2>&1
test -s "$root/$V297_VARIANT.v"
V297_LIB="$lib" \
V297_TECH_LEF="$platform/NangateOpenCellLibrary.tech.lef" \
V297_CELL_LEF="$platform/NangateOpenCellLibrary.macro.mod.lef" \
V297_TRACKS="$platform/make_tracks.tcl" \
V297_RCX_RULES="$platform/rcx_patterns.rules" \
V297_NETLIST="$root/$V297_VARIANT.v" \
V297_OUT="$root/$V297_VARIANT" \
"$V297_OPENROAD_BIN" -exit research/v297/v297_matched_physical.tcl > "$root/$V297_VARIANT.physical.log" 2>&1
test -s "$root/$V297_VARIANT.spef"
test -s "$root/$V297_VARIANT.final.def"
grep -Fq V297_EXTRACTED_DONE "$root/$V297_VARIANT.physical.log"
echo "V297_MATCHED_PHYSICAL_COMPLETE $V297_VARIANT"
