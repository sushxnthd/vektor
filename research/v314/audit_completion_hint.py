#!/usr/bin/env python3
"""Independent event-level audit for V314, separate from arbitration decisions.

Replays the emitted RF read/completion event ledger and checks physical-port
conservation and frozen prospective outcomes. No RTL or GPU trace claims.
"""
from collections import Counter
from completion_hint_holdout import (
    BANKS, PORTS, DEPTH, SLOTS, MEASURE, WARMUP,
    REGIMES, offered_trace, simulate, evaluate,
)


def audit_events(name, policy):
    offered = sum(sum(job is not None for job in arrivals)
                  for tick, arrivals in enumerate(offered_trace(name))
                  if tick >= WARMUP)
    stats, events = simulate(list(offered_trace(name)), policy, capture_events=True)
    assert len(events) == MEASURE
    reads_by_bank = Counter()
    completed_demand = Counter()
    read_count = early_count = completed_count = 0
    for tick, reads, completed in events:
        assert tick >= WARMUP
        assert len(completed) <= SLOTS
        per_bank = Counter(bank for _, _, bank, _, _ in reads)
        assert all(0 <= bank < BANKS and n <= PORTS
                   for bank, n in per_bank.items()), (name, policy, tick, per_bank)
        assert len({(lane, op) for lane, op, _, _, _ in reads}) == len(reads)
        assert all(0 <= lane < SLOTS and op in (0, 1) and phase in (0, 1)
                   for lane, op, bank, phase, born in reads)
        reads_by_bank.update(per_bank)
        read_count += len(reads)
        early_count += sum(phase for _, _, _, phase, _ in reads)
        completed_count += len(completed)
        for pair in completed:
            assert len(pair) == 2 and all(0 <= b < BANKS for b in pair)
            completed_demand.update(pair)
    assert offered == stats["offered"]
    assert read_count == stats["rf_reads"]
    assert early_count == stats["early_reads"]
    assert completed_count == stats["issued"]
    assert abs(stats["offered"] - stats["dropped"] - stats["issued"]) <= 2 * SLOTS * DEPTH
    # At most 16 queued warmup jobs, two operands each, can complete using
    # RF reads from before the measured window.
    for bank in range(BANKS):
        assert reads_by_bank[bank] <= PORTS * MEASURE
        assert completed_demand[bank] <= reads_by_bank[bank] + 2 * SLOTS * DEPTH
    return stats


def main():
    for name in REGIMES:
        base = audit_events(name, "age")
        candidate = audit_events(name, "hint")
        result = evaluate(name)
        assert result["baseline"] == base and result["candidate"] == candidate
        print(name, "issued", base["issued"], candidate["issued"],
              "ratio", format(result["completion_ratio"], ".8f"),
              "p99", base["p99_latency"], candidate["p99_latency"],
              "prediction_pass", result["prediction_pass"],
              "materiality_pass", result["materiality_pass"])
        if name == "no_win":
            assert result["prediction_pass"] is True
        if name == "hot":
            assert result["retire"] is True, "revisit mechanism if frozen gate unexpectedly passes"
    print("PASS: independent event accounting; V314 retained as a negative screen")


if __name__ == "__main__":
    main()
