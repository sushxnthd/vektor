#!/usr/bin/env bash
# Three equal-resource mapped architectures, three identical RC sensitivity cases.
set -euo pipefail
mkdir -p build/v296/sta
LIB=build/v296/nangate.lib
test -s "$LIB"
: "${V296_STA_BIN:?Set V296_STA_BIN to OpenSTA executable}"
sha256sum "$LIB" > build/v296/sta/lib.sha256
for variant in original optimized pairwise; do
  case "$variant" in
    original)
      top=vektor_issue_control
      src="rtl/vtile/steal_warp_scheduler.sv rtl/vtile/rf_bank_arbiter.sv rtl/vtile/issue_control.sv"
      pre=""
      ;;
    optimized)
      top=v295_issue_core
      src="rtl/vtile/steal_warp_scheduler.sv research/v295/v295_issue_core.sv"
      pre="hierarchy -top v295_issue_core -chparam PREDECODE 0;"
      ;;
    pairwise)
      top=v296_issue_core
      src="rtl/vtile/steal_warp_scheduler.sv research/v296/v296_issue_core.sv"
      pre=""
      ;;
  esac
  yosys -p "read_verilog -sv $src; $pre synth -top $top -flatten; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; check -assert; write_verilog -noattr -noexpr build/v296/sta/$variant.v; stat -liberty $LIB" > "build/v296/sta/$variant.synth.log" 2>&1
  test -s "build/v296/sta/$variant.v"
  for scenario in low nominal high; do
    case "$scenario" in
      low) cap=0.002; res=0.1 ;;
      nominal) cap=0.004; res=0.2 ;;
      high) cap=0.008; res=0.4 ;;
    esac
    V296_LIB="$LIB" V296_NETLIST="build/v296/sta/$variant.v" V296_TOP="$top" \
      V296_WIRE_CAP="$cap" V296_WIRE_R="$res" V296_VARIANT="$variant-$scenario" \
      "$V296_STA_BIN" -no_splash -exit research/v296/sta_mapped.tcl \
      > "build/v296/sta/$variant.$scenario.sta.log" 2>&1
    grep -q 'V296_STA_COMPLETE' "build/v296/sta/$variant.$scenario.sta.log"
  done
done
python3 research/v296/analyze_sta.py build/v296/sta
