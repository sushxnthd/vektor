# V310 strong reuse-capable baseline: exact admission falsification (2026-10-31)

**Decision: REJECT V310 as a new admission/throughput architecture mechanism.** This result is a strong-control falsification, not a claim that every commercial GPU uses the same control policy. Preserve V310 as a historical calibration experiment. Do not revive V287, V296 or V309.

## Question and control

The earlier V310 controller-only positive results compared verified same-register read coalescing against a historical compact-greedy controller that *does not reuse identical physical registers*. That comparison cannot establish incremental novelty or performance against a competent reuse-aware controller.

A strong, equal-port alternative performs the same full-identity equality check and single-read broadcast, then uses the same fixed-priority four-slot admission policy. It has 16 banks and two read ports per bank, exactly like V310. It is an implementable control class, not a claim about a particular proprietary GPU.

For each request i and bank b, let a_i and c_i be its operand banks, and d_i be 1 **only if complete physical register identities are equal**. Both reuse-capable policies consume:

    m_i(b) = 1[a_i=b] + (1-d_i) 1[c_i=b].

Given identical request priority, bank capacities and m_i, induction over the four slots proves the same admission decisions for *every input*, independent of the workload distribution. Consequently the prospective incremental admission law against the strong control is:

    G_incremental(o,h,q) = 1 for all admissible o,h,q.

This supersedes the earlier 1 + o*h*q^2/(2-o*h) formula **only as a claim of incremental novelty**: that earlier law remains valid for its explicitly weaker no-reuse synthetic control.

## Independent executable falsification

[research/v310/falsify_strong_reuse_control.py](falsify_strong_reuse_control.py) compares the existing candidate's pair/triple conflict equations against an independent per-bank two-port allocator using actual register identities. It exhausts 4^8 operand assignments across four physical registers (two distinct IDs per bank) and all 16 valid masks: **1,048,576 cases**.

Local source-script result:

| Measure | Result |
| --- | ---: |
| Candidate vs strong reuse-capable control mismatches | 0 |
| Candidate admissions | 1,542,240 |
| Strong reuse-capable admissions | 1,542,240 |
| Historical no-reuse admissions | 1,333,760 |
| Cases where historical no-reuse admitted fewer | 203,136 |
| Cases where historical no-reuse admitted more | 0 |
| Candidate / strong admission ratio | **1.000000** |
| Candidate / historical no-reuse ratio | **1.156310** |

This is an **exhaustive reduced-domain test**, not a full 16-bank formal proof, although the equal-demand induction covers the general model. The script includes adversarial same-bank/different-register aliases and a mutation control demonstrating that it can distinguish an actually non-reuse-aware allocator.

The workflow now executes this checker alongside the earlier RTL and frozen synthetic-law tests; source-pinned hosted CI must be inspected separately. Do not treat local script execution as hosted verification.

## What the result does and does not kill

- **Killed:** a claim of incremental *issue-admission* improvement or novel mechanism from intra-instruction verified same-register coalescing under the same fixed-priority reuse-capable baseline.
- **Not measured:** full register-ID comparator and forwarding datapath timing, power, area, routed RC, electrical signoff, GPU workloads or tile-level throughput.
- **Not excluded:** an independently demonstrated PPA improvement from a genuinely different implementation, an alternative scheduling policy or a new operand-availability mechanism. Those would require a new prospective mechanism and a fully matched strong baseline.
- The earlier 251.370 vs 266.266 mapped-area and 0.41 vs 0.43 ns placed-delay results compare **controller-only candidate against no-reuse control**. They are not an equal-capability strong-control comparison, and therefore cannot rescue V310's performance claim.
- Existing BOW, CORF, Memento and related operand reuse literature further limits originality; see the preserved prior-art audit.

**Next architecture selection gate:** choose one distinct mechanism with a positive *incremental* boundary against a reuse-aware equal-resource control, then preregister win and no-win workloads before RTL/physical work. Do not run additional V310 no-reuse synthetic speedup sweeps as if they advanced hardware novelty.

**Evidence tier:** analytical strong-control identity plus locally executed exhaustive reduced-domain checker; hosted confirmation pending at report commit. No RTX-5090-equivalence claim.
