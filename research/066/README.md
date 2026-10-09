# Vektor-066: replayed ACK identity and tag reclamation

The `research/066/fabric_066.py` deterministic two-sided model runs 288 structured, 36 exploratory and 16 adversarial configurations. Run with `python3 research/066/fabric_066.py`.

The independent identity predicate oracle runs with `g++ -std=c++17 -O2 research/066/independent_066.cpp -o /tmp/066 && /tmp/066`.

The synthesizable ACK filter is `rtl/ack_uid_guard_066.sv`. Run its directed test using `iverilog -g2012 -s tb_ack_uid_guard_066 -o /tmp/066.vvp research/066/rtl/*.sv && vvp /tmp/066.vvp`. GitHub Actions also performs generic Yosys synthesis.

Read [WORLD_MODEL.md](WORLD_MODEL.md), [RESULTS.md](RESULTS.md), and [TARGET_LEDGER.md](TARGET_LEDGER.md) before interpreting numbers. This component does not demonstrate an RTX 5090-class GPU. It assumes a truthful external DATA quiescence fence and immutable UIDs distinct across any stale ACK replay horizon.
