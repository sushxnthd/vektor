# V146 verification status

The frozen seed 146 matched two independent Python models over 50,000 cycles. Three unseen seeds (20261013, 5090, 141) matched for 10,000 cycles each: 80,000 total.

GitHub simulator CI passed for commit e0947595ded99ad81f3bfa8614358c912d4e7fc7 (run 38405152093).

The V146-specific HDL testbench and Yosys synthesis have NOT been executed. The existing rtl workflow tests earlier modules only. Do not infer V146 hardware verification from that workflow.

No RTX 5090-class gate advanced. Next: execute research/v146/CI.sh with Icarus and Yosys, then integrate the FMA backend.
