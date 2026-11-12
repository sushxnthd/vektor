#!/usr/bin/env python3
"""Independent same-information early-collector control for V313.

This is a policy-inclusion falsification, NOT an implementation of Triple-A RTL.
It intentionally uses a separate counter-based RF scheduler from the candidate.
"""
from collections import deque
from slack_prefetch_holdout import (
    BANKS, PORTS, DEPTH, SLOTS, WARMUP, MEASURE,
    offered_trace, simulate,
)


def independent_early_collector(stream):
    waiting = [deque() for _ in range(SLOTS)]
    issued = dropped = offered = early_reads = ready_reads = 0
    durations = []
    for tick, arrivals in enumerate(stream):
        for lane, job in enumerate(arrivals):
            if job is None:
                continue
            if tick >= WARMUP:
                offered += 1
            if len(waiting[lane]) == DEPTH:
                if tick >= WARMUP:
                    dropped += 1
            else:
                born, ready, banks = job
                waiting[lane].append(dict(born=born, ready=ready, banks=banks, done=[False, False]))
        free = [PORTS for _ in range(BANKS)]
        # An already-executable instruction always has precedence over early staging.
        for eligible in (True, False):
            for operand in (0, 1):
                for offset in range(SLOTS):
                    lane = (tick + offset) % SLOTS
                    if not waiting[lane]:
                        continue
                    head = waiting[lane][0]
                    if (max(head["ready"]) <= tick) != eligible:
                        continue
                    if head["done"][operand] or head["ready"][operand] > tick:
                        continue
                    bank = head["banks"][operand]
                    if not free[bank]:
                        continue
                    free[bank] -= 1
                    head["done"][operand] = True
                    if tick >= WARMUP:
                        if eligible:
                            ready_reads += 1
                        else:
                            early_reads += 1
        assert min(free) >= 0
        for q in waiting:
            if q and q[0]["done"] == [True, True]:
                head = q.popleft()
                assert max(head["ready"]) <= tick
                if tick >= WARMUP:
                    issued += 1
                    durations.append(tick - head["born"] + 1)
    return dict(issued=issued, dropped=dropped, offered=offered,
                early_reads=early_reads, ready_reads=ready_reads,
                mean_latency=sum(durations)/len(durations),
                p99_latency=sorted(durations)[int(.99*len(durations))])


def main():
    for regime in ("win", "no_win", "transfer"):
        stream = list(offered_trace(regime))
        candidate = simulate(stream, early=True)
        strong = independent_early_collector(stream)
        for metric in strong:
            assert candidate[metric] == strong[metric], (
                regime, metric, candidate[metric], strong[metric])
        if regime == "win":
            weaker = simulate(stream, early=False)
            assert strong["issued"] > weaker["issued"]
        print(regime, "strong same-information early collector matches candidate exactly",
              "issued", strong["issued"], "early reads", strong["early_reads"])
    print("PASS: zero incremental admission advantage over independent equal-information collector")


if __name__ == "__main__":
    main()
