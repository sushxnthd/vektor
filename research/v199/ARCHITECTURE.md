# ARCHITECTURE — V199

Keep V151 as FP32 integration reference. V153 is not electrically qualified (V195 73 control and 61 cutset max-cap violations); V196 buffer repair lacks routed wire, slew and fresh timing. The V199 Tcl diagnostic does not repair these defects. Select no cutset until repaired matched electrical STA, actual RF arrival traces, equal-budget area and Wave32 workload gates pass.

Build direction remains integrated FP32 tile -> timing/PPA -> compute/memory/divergence workloads -> tensor/memory/NoC/compiler. No RTX 5090-class claim.