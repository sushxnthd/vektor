# Vektor-063 Discovery Protocol V2 world model

KNOWN (conditional): 1 DATA plus 1 ACK consumes two slots on a shared one-flit-per-cycle return link. Four ACK tags per flit reduces amortized control traffic when bundles fill. These are elementary conservation laws, not architectural novelty.

BELIEVED: packed ACK transport may be useful at high GPU fabric occupancy. Equal-width encoding, queuing, timing, and area have not been validated.

CONFLICTING: ACK-first improves tag reuse at low occupancy, while data-first or batching can improve saturated throughput.

FALSIFIED (synthetic): the 062 independent-ACK throughput model remains valid unchanged on a shared return lane. FALSIFIED (synthetic): four-tag batching always helps; at two tags, no replay, throughput fell 1.63%.

ANOMALOUS: finite-window completions may exceed the asymptotic link bound slightly because ACKs remain queued at the measurement cutoff. No violation of flit conservation.

UNTESTED: strong ACK generation and exactly-once delivery, reset, loss, replay outside the modeled lifetime, real packet widths, PPA, GPU workloads, graphics/ray/tensor/ISA equivalence.

Experiment mechanism: shared return-link contention, replay and ACK packing. Preregistered P1-P6 in the local reproducibility package. Outcome: 144 structured simulations, 18 surprise probes, 18 holdout conservation checks, 128 independent C++ comparisons. Saturated zero-replay mean: shared 0.499958, packed 0.799896, dedicated 0.999750 tx/cycle. Residual to 0.8 packed ceiling: -0.000104 tx/cycle. Main uncertainty is physical implementation and traffic representativeness.

Foothold: bounded, reproducible capacity regime; not novel. Preserve prior negative results on replay, tag wrap and backpressure. Next decisive experiment: fabric-side strong ACK producer plus equal-budget synthesis of shared, bundled and separate control return links.
