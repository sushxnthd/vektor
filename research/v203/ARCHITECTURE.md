# ARCHITECTURE ledger — V203

Block: four-slot, 16-bank, two-read-port RF issue arbiter. Candidate reserves one port for decoder-certified identical source registers; baseline reserves two. No added storage or RF port, but extra logic/metadata and operand fanout are real costs.

Synthetic issue gains: compute-hot alias p=.75 +40.58%; compute-low-alias +9.54%; compute-distributed +11.91%; memory-sparse +0.84%; divergent-hot +22.67%; divergent-distributed +4.24%. Unseen hot +65.66%; unseen p=0 exactly 0%. These are synthetic modeled rates, NOT GPU IPC or physically qualified throughput.

Integration state: src_alias tied to zero in issue_control, so the existing tile still behaves like baseline. Decoder must prove full register identity (not just bank match); execution operand latches must accept multicast data. Timing, cap/slew, and mapped area are pending. Avoid counting same-bank different-register accesses as aliases.

V151 remains FP32 reference; V153 cutset not electrically qualified. No 5090-class claim.
