# V317 RF-proxy integration: identical 16-bank 2R1W flop-mapped proxy and sink.
# Only DESIGN_NAME changes; compact challenger adds unchanged same-policy logic; this is NOT SRAM macro or a GPU tile.
export PLATFORM = nangate45
export DESIGN_NAME = vektor_v317_rf_proxy_top_source
export VERILOG_FILES = $(VEKTOR_ROOT)/rtl/vtile/steal_warp_scheduler.sv $(VEKTOR_ROOT)/rtl/vtile/issue_control.sv $(VEKTOR_ROOT)/rtl/vtile/rf_bank_arbiter.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_bank_pairwise_credit.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_integrated_issue_top.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_proxy_banked_tile.sv $(VEKTOR_ROOT)/research/v317/rtl/compact_greedy_equal_policy.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_proxy_compact_challenger.sv
export SDC_FILE = $(VEKTOR_ROOT)/research/v317/rtl/rf_proxy_banked_tile.sdc
export ABC_AREA = 1
export ADDER_MAP_FILE :=
export SYNTH_REPEATABLE_BUILD = 1
export GPL_PLACE_IOS = 1
export PLACE_DENSITY_LB_ADDON = 0.05
export PDN_TCL = $(FLOW_HOME)/designs/nangate45/gcd/grid_strategy-M1-M4-M7.tcl
