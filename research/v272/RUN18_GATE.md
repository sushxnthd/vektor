# V272 run18: two-phase register-bank physical discriminator

Status: **not validated**. This isolated research branch is a hardware experiment, not an integrated GPU change.

The only active mechanism is double-pumping a one-read register-file bank. Its essential feasibility inequality is `T_1R_macro + T_address_setup + T_skew + T_wire + T_margin <= T_core/2`, with write/read turnaround separately characterized. A flip-flop synthesized array cannot establish SRAM macro timing. The matched controls are one-read plus operand collector and a true two-read bank at equal total area/energy budgets. A 2x clock may erase any saved read-port area in clock-tree power. Do not infer energy or novelty from logical read counts.

V272 will be retired after at most one additional substantive physical-tool attempt if no characterized RF macro and clock tree are available. FP32 V153/V156 remain disqualified independently; V272 does not rehabilitate them.
