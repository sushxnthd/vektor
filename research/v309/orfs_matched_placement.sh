#!/usr/bin/env bash
# Execute inside openroad/flow, /work is mounted repository, output volumes
# are persisted under /work/build/v309_orfs.
set -euo pipefail
out=/work/build/v309_orfs
cd "$out/orfs/flow"
export OPENROAD_EXE="$(command -v openroad)"
export YOSYS_EXE="$(command -v yosys)"
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
  config="$out/${name}.mk"
  cat > "$config" <<CONFIG
export PLATFORM = nangate45
export DESIGN_NAME = $top
export VERILOG_FILES = $rtl
export SDC_FILE = /work/research/v309/orfs_placement.sdc
export PLACE_DENSITY = 0.65
export ABC_AREA = 1
export TNS_END_PERCENT = 100
CONFIG
  for variant in dense relaxed; do
    case "$variant" in
      dense) die='0 0 30 30'; core='3 3 27 27' ;;
      relaxed) die='0 0 45 45'; core='4.5 4.5 40.5 40.5' ;;
    esac
    echo "V309_PHYSICAL_RUN $name $variant die=$die core=$core" | tee "$out/${name}_${variant}.meta"
    make DESIGN_CONFIG="$config" FLOW_VARIANT="$variant" \
      "DIE_AREA=$die" "CORE_AREA=$core" place \
      2>&1 | tee "$out/${name}_${variant}.make.log"
    export V309_PLACED_DB="$out/orfs/flow/results/nangate45/$top/$variant/3_place.odb"
    export V309_LIBERTY=$out/orfs/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib
    export V309_SDC=/work/research/v309/orfs_placement.sdc
    test -s "$V309_PLACED_DB" || { echo "MISSING_PLACED_DB $V309_PLACED_DB"; exit 1; }
    openroad -exit /work/research/v309/orfs_placement_sta.tcl \
      2>&1 | tee "$out/${name}_${variant}.sta.log"
  done
done
