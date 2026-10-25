# V296 original-routed SPEF coupling and activity-correlation boundary (frozen 2026-10-25)

**Protocol status: prospective, before running this decomposition on the two original SPEFs.** Sole active architecture mechanism V296; V287 retired. This experiment is read-only postprocessing, not a physical repair, GPU performance experiment, or claim of switched power. The original integrated physical gate remains failed for both contestants.

## Immutable evidence

Read exactly the original matched run [40173311725](https://github.com/sushxnthd/vektor/actions/runs/40173311725) artifact ZIPs: pairwise SHA-256 `9ce2ede807ba5858efcd113b3cd4c2f9e8e5d4a6d97a7b04eb663dd354786259`, serial SHA-256 `5c0f7ef91a2151ac2069553cd93a34b97d38c939d6f1106ea95ef4cc8b85706e`. They share original physical Tcl SHA-256 `30b0a072ec197a47c5e2264567fee50f908b85a8d946e607765083221c0fcf3d`, 3.5 ns Nangate45 constraints and completed detailed routing. They fail setup, hold and capacitance constraints. Do not re-run or alter placement, routing, clock or source RTL.

## Positive boundary law and falsification

Parse SPEF `*CAP` into ground capacitance `C_g` and two-terminal coupling `C_c`, deduplicating identical endpoint pairs with an explicit consistency check; preserve declared `*D_NET` sums separately. Let signed transitions on the two terminals of a coupling capacitor have equal mean square amplitude `alpha V^2` and normalized covariance `rho` in [-1,1]. Then the **idealized external capacitive switching-energy coefficient** is

`K(alpha,rho) = alpha [C_g + 2 C_c(1-rho)]`, so `E_ext = V^2 K/2`.

The candidate beats the control *in this model only* iff

`alpha_V296/alpha_serial < [C_g,serial + 2 C_c,serial(1-rho_serial)] / [C_g,V296 + 2 C_c,V296(1-rho_V296)]`.

The law is derived before examining either original `*CAP` decomposition. Evaluate exactly three same-correlation corners `rho = -1,0,+1` at equal activity; report the corresponding activity break-even boundaries, whether V296 is lower at **all** corners, and the worst-candidate versus best-control independent-correlation bound. Do not select a favorable corner after the fact.

The previously observed 12.76% lower sum of declared `*D_NET` capacitance does **not** establish switching-energy savings. **Kill a correlation-robust external-energy advantage** if the candidate fails even one same-rho corner, and kill an independent-correlation guarantee unless its worst-case proxy is below the control's best-case proxy. A negative or incomplete result must be retained.

## Independent audit / failure handling

Require exact artifact hashes, both extracted SPEFs, `*C_UNIT 1 PF`, parseable finite nonnegative `*CAP` records, identical original physical Tcl hashes, and complete detailed-route markers. Fail closed for contradictory duplicate coupling values, unsupported SPEF syntax, missing artifacts or nonfinite values. Report ground/coupling components, `*D_NET` reconciliation differences, duplicate counts, and code self-tests. A physically meaningful signoff-power claim requires real workload activity, coupling-aware timing/power extraction, cell internal/clock/glitch/short-circuit energy and closed timing/electrical gates; none is supplied by this model.

## Architectural decision

The test can falsify a simplified dynamic-interconnect argument, but cannot rescue the failed 3.5 ns integrated slice, establish equal-resource Pareto dominance or imply nonzero same-clock throughput. Keep prospective workload holdouts sealed. Do not modify Kernellum PR #119 or other workstream branches.
