# Vektor-074 — finite-epoch replay alias and reset contract
Date: 2026-10-10. Classification: DISCRIMINATION + CAPABILITY-BUILDING.

## Preregistered hypotheses and outcome
An independent replay source retains a physical packet from epoch zero while transaction identifiers are reused. For a b-bit modulo epoch, the first old/new identity collision is predicted at reuse 2^b. A complete physical drain blocks reuse until the copy terminates; this is safety, not liveness. A volatile counter reset can alias immediately if a stale copy survives. A certified packet lifetime L and minimum inter-reuse spacing Q avoid the first wrap collision in the simplified model iff Q*2^b >= L.

Local tests: eight epoch widths (1..8), 96 lease-bound cases, and 16 minimally theory-guided probes (12.5% of 128 total cases). Independent C++ arithmetic reproduced 104 structured cases. Prediction residual zero in the finite model. No RTL simulation or synthesis has been completed in this run.

## Discovery Protocol V2 world model
- KNOWN: finite-width modulo tags alias after wrap if an old copy persists; constructive witnesses.
- BELIEVED: complete producer/router/CDC drain before reuse is sufficient under trustworthy accounting, based on Vektor-073 finite exploration.
- CONFLICTING: extra tag bits may reduce fencing frequency, but cannot replace an enforceable lifetime or quiescence contract.
- FALSIFIED: finite epoch bits alone guarantee safety under unbounded replay delay; reset-cleared local counters certify physical drain.
- ANOMALOUS: no unexplained residual; exact wrap boundary is retained as a negative control.
- UNTESTED: integrated RTL, formal unbounded safety, CDC implementation, synthesis/PPA, GPU performance.

## Competing explanations and uncertainty
The failure is an identity collision, not a scheduler performance effect. This simplified model has one UID and a retained packet; real routers can have parallel identifiers, hidden replay sources, and variable/unbounded stalls. Its certified-lease condition is not a universal protocol theorem.

## Prior art and closed branches
Sequence-number wrap, replay suppression and epoch tagging are established techniques, not claimed innovations. Retain Vektor-067 lifetime-bound failure, Vektor-072 producer closure insufficiency, and Vektor-073 reset/CDC counterexamples.

## Reproducibility
Run Python and independent C++ model in research/074/model; raw results and additional experimental RTL are in the Vektor-074 reproducibility package. The RTL guard consumes externally certified all_closed/all_empty/reset_quiescent; it does not itself prove those signals trustworthy.

## Single next decisive action
Integrate a two-hop RTL retirement cut with independently generated producer closure, physical copy accounting, and reset/CDC quiescence. Simulate and synthesize in free CI; test stale packet injection against actual RTL.

5090-class gates: FP32, tensor, memory, graphics, ray, frequency, area, power, software, reproducibility all INCONCLUSIVE.
