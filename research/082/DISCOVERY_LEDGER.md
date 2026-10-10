# Vektor-082 Discovery Ledger

DISCRIMINATION: Four-wide issue interface caps throughput. Simulated 0/230 violations. Operand-ready 4.790 becomes issue 3.992; 5.698 becomes 3.988.

SURPRISE: Bank-aware operand ordering improved 23/100 controlled cases, worsened 3, tied 74. Holdout: improved 23/80, worsened 2, tied 55. Largest gain: 378 to 364 cycles. Occasional reversals indicate scheduling-phase effects.

CAPABILITY-BUILDING: Independent C++17 checker matched 640/640 integer comparisons across 160 configurations. Prior fixed-order model reproduced exactly.

KNOWN: issue-width bound in this software model. BELIEVED: bank-aware reads sometimes relieve conflicts. CONFLICTING: fewer bank stalls can still cost cycles. FALSIFIED: operand-ready rate proves sustainable issue rate. ANOMALOUS: occasional reversals. UNTESTED: coherent operand values, RTL, physical implementation.

Next: integrate coherent WAW/RAW and finite issue width into the canonical V-Tile simulator.
