# V184 — RF operand-stability integration gate

Active question: Does whole-operand stability at the RF/issue boundary preserve V153 cutset's modeled switching advantage under realistic invalid-bus churn, without increasing FP32 critical-path delay or resource cost relative to equal-budget V151?

Frontier: V183 rejected exponent-only hold; V181/V182 observed occupancy and burstiness reversals in settled Boolean transitions. V156 matched OpenSTA passes, but seven-point arrival sweep is not yet executed.

Measurable objective: freeze identical accepted FP32 operand streams and compare (i) invalid operand toggles, (ii) whole-netlist settled transitions per accepted instruction, (iii) 0.05–5 ns OpenSTA worst slack, (iv) area, (v) valid outputs and ready/valid. Equal-resource control: V151 early-capture and V153 full-hold with any additional mux/register costs accounted for.

Mechanism: upstream RF/issue read-enable holds *all* FP32 payload fields during invalid cycles; suppresses V153's pre-capture logic activity. Prediction: benefit grows as invalid-bus churn increases, but timing win vanishes if operand arrival exceeds the measured cutset budget.

Falsification: a valid-output mismatch, throughput regression, physical area/timing penalty that outweighs switching savings, or absence of predicted churn/occupancy crossover.

Publishable success: novelty audit plus >=5% repeatable area-normalized performance/energy advantage over strongest public equal-budget baseline on unseen compute/memory/divergent kernels and independent checker. Architecture threshold: >=10% mapped delay gain with <=10% area cost and <=5% tile throughput regression, plus credible physical proxy. Kill: three substantive runs without improved claim or boundary. Evidence class remains simulation/RTL/STA only until physically validated.

SCIENCE and ARCHITECTURE ledgers must remain separate. Preserve failed runs. No RTX 5090 equivalence claim.
