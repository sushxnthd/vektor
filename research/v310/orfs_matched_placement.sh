#!/usr/bin/env bash
# Matched direct Nangate45 placement in pinned OpenLane tool image.
# Uses ORFS only for publicly available Nangate45 platform LEF/Liberty.
# No ORFS Python scripts, which require a newer Python than this image.
set -euo pipefail
out=/work/build/v310_orfs
platform="$out/orfs/flow/platforms/nangate45"
mkdir -p "$out"
openroad -version | tee "$out/openroad_version.txt"
yosys -V | tee "$out/yosys_version.txt"
for name in compact_greedy verified_coalescer; do
  case "$name" in
    compact_greedy)
      top=vektor_v310_matched_baseline
      rtl='/work/rtl/vtile/v310_compact_greedy_control.sv /work/rtl/vtile/v310_matched_baseline.sv' ;;
    verified_coalescer)
      top=vektor_v310_verified_read_coalescer
      rtl=/work/rtl/vtile/v310_verified_read_coalescer.sv ;;
  esac
  lib="$platform/lib/NangateOpenCellLibrary_typical.lib"
  test -s "$lib"
  yosys -p "read_liberty -lib $lib; read_verilog -sv $rtl; synth -top $top -noabc; abc -liberty $lib; clean; stat -liberty $lib; write_verilog -noattr -noexpr $out/$name.v" \
    2>&1 | tee "$out/$name.synthesis.log"
  # Post-hoc attribution only: same mapped netlist, no wire RC.
  export V310_PLATFORM_DIR="$platform"
  export V310_NETLIST="$out/$name.v"
  export V310_TOP="$top"
  export V310_LIBERTY="$lib"
  export V310_SDC=/work/research/v310/orfs_placement.sdc
  openroad -exit /work/research/v310/orfs_zero_wire_control.tcl \
    2>&1 | tee "$out/$name.zero_wire.sta.log"
  for variant in dense relaxed; do
    case "$variant" in
      dense) die='0 0 30 30'; core='3 3 27 27' ;;
      relaxed) die='0 0 45 45'; core='4.5 4.5 40.5 40.5' ;;
    esac
    echo "V310_PHYSICAL_RUN $name $variant die=$die core=$core" | tee "$out/${name}_${variant}.meta"
    export V310_PLATFORM_DIR="$platform"
    export V310_NETLIST="$out/$name.v"
    export V310_TOP="$top"
    export V310_DIE="$die"
    export V310_CORE="$core"
    export V310_PLACED_DB="$out/${name}_${variant}.odb"
    openroad -exit /work/research/v310/orfs_place_direct.tcl \
      2>&1 | tee "$out/${name}_${variant}.placement.log"
    test -s "$V310_PLACED_DB" || { echo "MISSING_PLACED_DB $V310_PLACED_DB"; exit 1; }
    export V310_LIBERTY="$lib"
    export V310_SDC=/work/research/v310/orfs_placement.sdc
    openroad -exit /work/research/v310/orfs_placement_sta.tcl \
      2>&1 | tee "$out/${name}_${variant}.sta.log"
  done
done
