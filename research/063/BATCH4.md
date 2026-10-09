# Vektor-063: ACK batching experiment

The synthetic event model treats one data return and one strong quiescence acknowledgment as flits on the same 1-flit/cycle return link. An optional fixed-width ACK flit carries up to four tag identifiers.

At 64 tags, no replay, 16,000 cycles: unbatched ACK-first 0.499958, four-tag bundled ACK 0.799896, dedicated ACK 0.999750 completed transactions/cycle (means across three seeds). Thus bundling improved modeled throughput by 60.0% over the unbatched shared link in this particular configuration.

Negative result: at two tags and no replay, bundling regressed from 0.46527 to 0.45769 transactions/cycle (1.63% decrease) due to delayed retirement and insufficient ACK accumulation.

Evidence: 144 structured runs, 18 minimally theory-guided probes, 18 holdout conservation checks, 128 exact C++/Python single-copy comparisons. No physical measurements. The four-tag payload must fit the same flit width; ACK encoding, security, quiescence guarantees, and timing/area are unverified.

Prior art exists for multi-credit NoC flow control (Naqvi et al., DDECS 2013). No novelty claim. Next: verify fabric-side quiescence and mapped physical cost.
