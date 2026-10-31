#!/usr/bin/env bash
# Matched direct Nangate45 placement in pinned OpenLane tool image.
# Uses ORFS only for publicly available Nangate45 platform LEF/Liberty.
# No ORFS Python scripts, which require a newer Python than this image.
set -euo pipefail
out=/work/build/v309_orfs
platform="$out/orfs/flow/platforms/nangate45"
mkdir -p "$out"
openroad -version | tee "$out/openroad_version.txt"
yosys -V | tee "$out/yosys_version.txt"
for name in compact_greedy factored_exact_max; do
  case "$name" in
    compact_greedy)
      top=vektor_v309_compact_greedy_arbiter
      rtl=/work/rtl/vtile/compact_greedy_arbiter.sv ;;
    factored_exact_max)
      top=vektor_v309_factored_subset_arbiter
      rtl=/work/rtl/vtile/factored_subset_arbiter.sv ;;
  esac
  lib="$platform/lib/NangateOpenCellLibrary_typical.lib"
  test -s "$lib"
  yosys -p "read_liberty -lib $lib; read_verilog -sv $rtl; synth -top $top -noabc; abc -liberty $lib; clean; stat -liberty $lib; write_verilog -noattr -noexpr $out/$name.v" \
    2>&1 | tee "$out/$name.synthesis.log"
  for variant in dense relaxed; do
    case "$variant" in
      dense) die='0 0 30 30'; core='3 3 27 27' ;;
      relaxed) die='0 0 45 45'; core='4.5 4.5 40.5 40.5' ;;
    esac
    echo "V309_PHYSICAL_RUN $name $variant die=$die core=$core" | tee "$out/${name}_${variant}.meta"
    export V309_PLATFORM_DIR="$platform"
    export V309_NETLIST="$out/$name.v"
    export V309_TOP="$top"
    export V309_DIE="$die"
    export V309_CORE="$core"
    export V309_PLACED_DB="$out/${name}_${variant}.odb"
    openroad -exit /work/research/v309/orfs_place_direct.tcl \
      2>&1 | tee "$out/${name}_${variant}.placement.log"
    test -s "$V309_PLACED_DB" || { echo "MISSING_PLACED_DB $V309_PLACED_DB"; exit 1; }
    export V309_LIBERTY="$lib"
    export V309_SDC=/work/research/v309/orfs_placement.sdc
    openroad -exit /work/research/v309/orfs_placement_sta.tcl \
      2>&1 | tee "$out/${name}_${variant}.sta.log"
  done
done
