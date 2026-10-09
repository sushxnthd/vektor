# Vektor-068 — ACK producer closure vs transport extinction

**Evidence:** finite software model plus independent C++ enumeration. New RTL simulation and synthesis remain pending. See WORLD_MODEL.md for claims, assumptions, negative results, and next experiment.

## Reproduce
```sh
python3 research/068/exhaustive_068.py
g++ -std=c++17 -O2 -Wall -Wextra -Werror research/068/replica_068.cpp -o /tmp/v068 && /tmp/v068
iverilog -g2012 -s tb_ack_closure_068 -o /tmp/v068.vvp research/068/rtl/*.sv && vvp /tmp/v068.vvp
yosys -Q -T -p 'read_verilog -sv research/068/rtl/ack_closure_068.sv; hierarchy -top ack_closure_068; proc; opt; techmap; opt; check; stat'
```

Only the first two commands are confirmed run. Existing repository RTL CI does not test the new module. The dedicated 068 GitHub workflow currently verifies Python/C++ only.

## Finding
Vektor-067's experimental RTL rejects incoming ACKs after ACK producer closure. This conflates *no further ACK emission* with *no ACK replicas remaining in transit*. In a finite abstract model, 16 legal post-closure ACK delivery transitions exist among 6,064 legal transitions across 114 reachable states. An independently written C++ checker reproduced the aggregate counts. No GPU-level performance or novelty claim follows.

## Next decisive action
Run new RTL simulation and synthesis, then integrate bounded router-generated physical replica terminal indications and reset fencing. Do not merge into main until verified.
