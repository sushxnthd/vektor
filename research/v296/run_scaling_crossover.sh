#!/usr/bin/env bash
# Same V296 mechanism, parameterized combinational arbitration only.
# Preregistered SCALING_CROSSOVER_PREREG_20261024.md.
set -euo pipefail
root=build/v296/scaling
mkdir -p "$root"
lib=build/v296/nangate.lib
test -s "$lib"
yosys -V > "$root/yosys.version"
iverilog -V > "$root/iverilog.version" 2>&1 || true
sha256sum "$lib" research/v296/v296_scaling_arbiters.sv \
  research/v296/tb_v296_scaling.sv \
  research/v296/scaling_crossover_audit.py \
  research/v296/run_scaling_crossover.sh > "$root/inputs.sha256"
python3 research/v296/scaling_crossover_audit.py --self-test
while read -r bits slots tier; do
  echo "V296_SCALING_START bits=$bits slots=$slots tier=$tier"
  iverilog -g2012 -s tb_v296_scaling \
    -Ptb_v296_scaling.BANK_BITS="$bits" \
    -Ptb_v296_scaling.SLOTS="$slots" \
    -o "$root/b${bits}_s${slots}.vvp" \
    research/v296/v296_scaling_arbiters.sv research/v296/tb_v296_scaling.sv
  vvp "$root/b${bits}_s${slots}.vvp" > "$root/b${bits}_s${slots}.sim.log"
  grep -q "V296_SCALING_ORACLE_PASS bits=$bits slots=$slots " \
    "$root/b${bits}_s${slots}.sim.log"
  for kind in pairwise onehot; do
    if [ "$kind" = pairwise ]; then top=v296_pairwise_scaling; else top=v296_onehot_scaling; fi
    yosys -p "read_liberty -lib -ignore_miss_func -ignore_miss_dir $lib; \
      read_verilog -sv research/v296/v296_scaling_arbiters.sv; \
      hierarchy -top $top -chparam BANK_BITS $bits -chparam SLOTS $slots; \
      synth -top $top -flatten; \
      abc -liberty $lib; clean; check -assert; stat -liberty $lib" \
      > "$root/b${bits}_s${slots}_$kind.synth.log" 2>&1
    grep -q 'Chip area for' "$root/b${bits}_s${slots}_$kind.synth.log"
  done
  echo "V296_SCALING_DONE bits=$bits slots=$slots tier=$tier"
done < <(python3 research/v296/scaling_crossover_audit.py --cases)
python3 research/v296/scaling_crossover_audit.py "$root"
