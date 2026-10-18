# SCIENCE — V198

V196's direct-pin capacitance repairs are sensitive to omitted wire capacitance. The archived Nangate45 netlists give the following minimum *hypothetical added capacitance per sink* at which a max-capacitance violation reappears (fF/sink):

| Repair headroom | Control | Cutset |
| --- | ---: | ---: |
| 0% | 0.01223 | 0.01073 |
| 10% | 0.17900 | 0.20568 |
| 20% | 0.40185 | 0.43066 |
| 30% | 0.72866 | 0.62726 |

These are exact symbolic margins from the archived mapped netlists, NOT extracted interconnect capacitances or STA. They do not establish physical feasibility. No novelty or energy claim. Raw executable evidence remains to be uploaded after repository write restrictions are resolved.
