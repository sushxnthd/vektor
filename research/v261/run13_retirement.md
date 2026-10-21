# V261 retirement — 2026-10-21

Evidence class E1 only. Warp-epoch-qualified RF-bank retention sleep is observationally identical to a conventional threshold-retention controller with the same inputs, counters, ports, wake latency and retention resources. Its RTL proxy contains no epoch-specific predictor, retention SRAM macro or power switch.

Frozen 4096-cycle x 4-bank traces (seeds 261101/261102/261103): positive assumed leakage savings 40.6244% with 0 readiness violations; negative 0% with 0; divergent 6.5088% with 513 readiness violations. Incremental gain over the strongest equal-resource threshold controller: 0% in every case. Independent FSM reference agrees on 164 transitions from 41 reachable states and all 49,152 bank-cycle observations. Assumed active/retention leakage 1.0/0.1 units per cycle; 32 units per sleep transition pair. No silicon power evidence.

Corrected law: with threshold 36 and 5-cycle prewake, actual sleep cycles = max(0,L-40), and net energy saved = 0.9*max(0,L-40)-32*1[L>40]. Net savings only for integer L>=76, not L>=36. E.g. L=48 loses 24.8 units, L=64 loses 10.4.

No RTL simulation, synthesis, clean max-cap/slew, matched STA, retention macro or physical PPA. Retire V261 without integrating into tile. V153/V156 FP32 timing claims remain disqualified. Full scripts/raw data and hashes in reproducibility archive from automation run 13; pending separate source publication.
