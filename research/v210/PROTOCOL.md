# V210 frozen discriminator protocol (2026-10-18)

**Active kernel:** V209 deferred bank-aware RF fallback; this is its final qualification run. V153/V156 FP32 cutset is retired pending electrical repair, not a validated architecture claim.

**Primary architectural gate:** full V209 candidate must pass Icarus RTL differential tests and matched mapped timing/electrical (max capacitance and slew) with the current Vektor issue controller. Generic Yosys counts or Python issue grants alone cannot pass this gate. The available execution environment lacks Icarus/Yosys/OpenSTA, and GitHub executable-RTL writes may be blocked. If the gate cannot be run, retire this kernel; do not claim physical falsification.

**Frozen secondary discriminator:** compare deferred fallback with a *stronger simpler equal-port control* that tries an eligible backup immediately on RF rejection, using the same four slots, sixteen banks and two reads per bank. That control can harm later primary grants. Measure mean issued waves and number of regressions on matched synthetic traces; use the V209 predeclared seed 271828 and five classes: compute_hot, compute_uniform, memory_sparse, divergent_hot, divergent_uniform. These are NOT GPU workloads.

**Unseen win/no-win predictions:** four primaries all requiring two reads from bank zero with three disjoint legal backups: deferred grants four versus greedy one. Four primaries on disjoint bank pairs: both grant four. Verify exact bank usage <=2, uniqueness, and accepted-wave eligibility.

**Clock-frequency sensitivity:** for modeled issue gain g, candidate net issued waves/s beats baseline only when f_candidate/f_baseline > 1/(1+g). Compute this boundary for each class; do not confuse it with measured STA.

**Retirement decision:** if executable RTL cannot be committed/run and fresh matched mapped STA is unavailable by end of this run, retire V209/V210 as an unqualified mechanism. Preserve all failures and continue with one new architecture-relevant positive-law kernel in the following run. The automation itself remains enabled.
