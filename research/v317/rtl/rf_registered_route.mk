# V317 registered source/pairwise fixed-priority arbiter matched physical flow.
# Override DESIGN_NAME and CORE_UTILIZATION on the make command line.
export PLATFORM = nangate45
export DESIGN_NAME = vektor_v317_rf_physical_top_source
export VERILOG_FILES = $(VEKTOR_ROOT)/rtl/vtile/rf_bank_arbiter.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_bank_pairwise_credit.sv $(VEKTOR_ROOT)/research/v317/rtl/rf_registered_physical_top.sv
export SDC_FILE = $(VEKTOR_ROOT)/research/v317/rtl/rf_registered_route.sdc
export ABC_AREA = 1
export ADDER_MAP_FILE :=
export CORE_UTILIZATION ?= 35
export SYNTH_REPEATABLE_BUILD = 1
export GPL_PLACE_IOS = 1
export PLACE_DENSITY_LB_ADDON = 0.20
export PDN_TCL = $(FLOW_HOME)/designs/nangate45/gcd/grid_strategy-M1-M4-M7.tcl
