# RF pair-rescue proof (Vektor-043)

**Evidence level:** exhaustive software verification of a four-request, two-source, two-read-port-per-bank arbitration abstraction; not RTL or silicon PPA.

The complete experiment enumerates all 4,140 equality partitions of eight operand-bank positions, every one of 16 request-valid masks, and four priority phases: **264,960 cases**. A maximum-cardinality oracle and a greedy-plus-one-for-two-rescue arbiter agree on all cases (including exact phase tie-break). Greedy admission falls short of the oracle by one request in 3,480 cases and never by more than one.

The bank-equality partition enumeration is complete for any implementation with at least eight bank IDs (including Vektor's 16-bank model). This does not prove multi-cycle throughput, fairness, area, timing, or power.

**Preregistered prediction:** A single accepted request can be exchanged for two rejected requests to recover every four-request greedy cardinality loss; any greedy deficit is at most one.

**Observed:** zero disagreements, residual zero. **Known:** exact combinational admission under the stated model. **Believed:** bounded augmentation could admit a simpler RTL implementation. **Untested:** equal-budget synthesis, multi-cycle fairness, power, 2.56 GHz feasibility. **Falsified:** greedy always maximizes admission. **Anomalous:** no gap greater than one exists in the complete four-request model. **Conflicting:** runtime feasibility-test count is not equivalent to combinational gate count.

**Cheapest discriminating next experiment:** differential RTL simulation against exact enumeration and Yosys synthesis with a common technology mapping.

Reproduce with `g++ -O2 -std=c++17 research/043/exhaustive_043.cpp -o /tmp/v043 && /tmp/v043`.

**RTX 5090-class gate:** INCONCLUSIVE.
