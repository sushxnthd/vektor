# V317 integrated issue-control physical gate: same scheduler, bank mux, FF boundaries.
# Only DESIGN_NAME changes between source and pairwise.
export PLATFORM = nangate45
export DESIGN_NAME = vektor_v317_issue_integrated_top_source
export VERILOG_FILES = $(VEKTOR_ROOT)/rtl/vtile/steal_warp_scheduler.sv $(VEKTOR_ROOT)/rtl/vtile/issue_control.sv $(VEKTOR_ROOT)/rtl/vtile/rf_bank_arbiter.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_bank_pairwise_credit.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_integrated_issue_top.sv
export SDC_FILE = $(VEKTOR_ROOT)/research/v317/rtl/rf_integrated_issue.sdc
export ABC_AREA = 1
export ADDER_MAP_FILE :=
export SYNTH_REPEATABLE_BUILD = 1
export GPL_PLACE_IOS = 1
export PLACE_DENSITY_LB_ADDON = 0.20
export PDN_TCL = $(FLOW_HOME)/designs/nangate45/gcd/grid_strategy-M1-M4-M7.tcl
