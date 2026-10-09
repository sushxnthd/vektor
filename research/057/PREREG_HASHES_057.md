# Vektor-057 staged prediction audit

Predictions were SHA256-frozen locally before their respective tests. They were not all publicly committed before execution; the downloadable full reproducibility archive contains the evolving prediction file and raw results. This is a post-experiment GitHub record.

| Stage | SHA256 after freezing stage | Result |
|---|---|---|
| P1–P5 | `728b9fe8879728c10f3c5121f826553ca1d0eead494ac5716ec37a7895aceb7c` | P1–P4 PASS, P5 FAIL |
| P6–P7 | `fbfa322620fca77ffa150263f042f8d3d40c65502fe8e066e51aaf662d821de7` | both FAIL |
| P8–P9 | `782cfaa2a814e7404d9a2e5577e69105fdc0a5ddf49951f39a705f4e9e8f5111` | both PASS |
| P10–P11 | `1315d0c6655ef2408a8a1c82d659d67173e9aa78ffdc616aa7e97e888ab8f35d` | both PASS |
| P12–P14 | `92eb67033771de7cc45907d7ce6fa0b1f48dcb095a157ccf0c8cbe24f38a0ce7` | all PASS |
| P15–P16 | `9069d103e096dfa004b3cd4e3d86ee3c83c54220e7e25b111687672bc03407de` | both PASS |

BACB was an exploratory discovery pattern, not a fully unseen workload. P15 is conditional on ordered ages; generic cells do not establish mapped area/timing.
