#!/usr/bin/env bash
# V312 physically matched prefilter, NOT routed/extracted signoff.
# Runs inside ghcr.io/the-openroad-project/openlane:1.0.2 with pinned ORFS Nangate45 platform.
set -euo pipefail
out=/work/build/v312_physical
platform="$out/orfs/flow/platforms/nangate45"
lib="$platform/lib/NangateOpenCellLibrary_typical.lib"
mkdir -p "$out"
test -s "$lib"
openroad -version | tee "$out/openroad_version.txt"
yosys -V | tee "$out/yosys_version.txt"
cat > "$out/io.sdc" <<'SDC'
create_clock -name virtual_issue_clock -period 1.0
set_input_delay -clock virtual_issue_clock 0 [all_inputs]
set_output_delay -clock virtual_issue_clock 0 [all_outputs]
set_input_transition 0.050 [all_inputs]
set_load 0.020 [all_outputs]
SDC
cat > "$out/zero.tcl" <<'TCL'
set p $::env(V312_PLATFORM_DIR)
read_lef "$p/lef/NangateOpenCellLibrary.tech.lef"
read_lef "$p/lef/NangateOpenCellLibrary.macro.mod.lef"
read_liberty $::env(V312_LIBERTY)
read_verilog $::env(V312_NETLIST)
link_design $::env(V312_TOP)
read_sdc $::env(V312_SDC)
puts "V312_ZERO_BEGIN"
report_checks -path_delay max
puts "V312_ZERO_END"
TCL
cat > "$out/place.tcl" <<'TCL'
set p $::env(V312_PLATFORM_DIR)
read_lef "$p/lef/NangateOpenCellLibrary.tech.lef"
read_lef "$p/lef/NangateOpenCellLibrary.macro.mod.lef"
read_liberty $::env(V312_LIBERTY)
read_verilog $::env(V312_NETLIST)
link_design $::env(V312_TOP)
initialize_floorplan -die_area $::env(V312_DIE) -core_area $::env(V312_CORE) -site FreePDK45_38x28_10R_NP_162NW_34O
make_tracks
place_pins -hor_layers metal5 -ver_layers metal6
global_placement -density 0.65
detailed_placement
write_db $::env(V312_PLACED_DB)
puts "V312_PLACED_DB_WRITTEN"
TCL
cat > "$out/sta.tcl" <<'TCL'
read_db $::env(V312_PLACED_DB)
read_liberty $::env(V312_LIBERTY)
read_sdc $::env(V312_SDC)
set_wire_rc -signal -layer metal3
estimate_parasitics -placement
puts "V312_PLACED_RC_BEGIN"
report_checks -path_delay max
puts "V312_ELECTRICAL_BEGIN"
report_check_types -max_slew -max_capacitance -violators
puts "V312_ELECTRICAL_END"
puts "V312_PLACED_RC_END"
TCL
export V312_PLATFORM_DIR="$platform" V312_LIBERTY="$lib" V312_SDC="$out/io.sdc"
for name in compact_head_only factored_fallback; do
  case "$name" in
    compact_head_only)
      top=vektor_v309_compact_greedy_arbiter
      rtl=/work/rtl/vtile/v312_compact_head_only_control.sv ;;
    factored_fallback)
      top=vektor_v312_factored_fallback
      rtl=/work/rtl/vtile/v312_factored_fallback.sv ;;
  esac
  yosys -p "read_liberty -lib $lib; read_verilog -sv $rtl; synth -top $top -noabc; abc -liberty $lib; clean; stat -liberty $lib; write_verilog -noattr -noexpr $out/$name.v" \
    2>&1 | tee "$out/$name.synthesis.log"
  export V312_NETLIST="$out/$name.v" V312_TOP="$top"
  openroad -exit "$out/zero.tcl" 2>&1 | tee "$out/$name.zero.sta.log"
  for variant in dense relaxed; do
    case "$variant" in
      dense) die='0 0 30 30'; core='3 3 27 27' ;;
      relaxed) die='0 0 45 45'; core='4.5 4.5 40.5 40.5' ;;
    esac
    export V312_DIE="$die" V312_CORE="$core" V312_PLACED_DB="$out/${name}_${variant}.odb"
    openroad -exit "$out/place.tcl" 2>&1 | tee "$out/${name}_${variant}.placement.log"
    test -s "$V312_PLACED_DB"
    openroad -exit "$out/sta.tcl" 2>&1 | tee "$out/${name}_${variant}.sta.log"
  done
done
