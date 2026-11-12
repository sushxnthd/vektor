# V317 bank-law robustness: correlated mapping kill sensitivity (2026-11-03)

This is an **assumption sensitivity**, not a GPU benchmark or a new active mechanism. The earlier exact formula for the restricted two-cycle oracle opportunity assumes eight independently and uniformly bank-assigned operand identities. A real compiler/register file may violate that independence.

Predeclared countermodel: with probability q, use the independent-uniform mapping; otherwise all eight identities map to one common bank. The latter has no oracle-over-greedy scheduling opportunity in the studied model. Thus P_mix(E|B,q)=q P_ind(E|B), exactly. This illustrates non-identifiability from bank count alone: the same B admits opportunity probabilities from zero through the independent prediction. q is a model parameter, **not** a measured GPU property.

The accompanying script prints exact rational mixture probabilities and a deliberately optimistic bound on throughput after a clock penalty δ: (1+P_mix(E))/(1+δ). This is an upper bound, not a prediction: it assumes each opportunity yields one extra completion and greedy's expected completions are at least one. A value below 1 is a *necessary kill* for that model and δ, while a value above 1 does not establish a win.

For δ=0.005 and B=16, q=0.25, the optimistic bound is 0.998779×; for B=48 even q=1 yields a bound below 1. These are model-based kill results only.

**Next decisive experiment:** obtain provenance-pinned, binary-verified real-kernel register bank demand; determine whether the independence assumption holds; then evaluate a matched RTL controller against the strongest compact baseline under realistic wiring and loads. Preserve previous electrical/area failures. Do not promote another scheduler or claim GPU IPC improvement.
