"""V317 falsification: prospective contention selector under persistent queues.

Paired arrival streams; four oldest requests visible; two reads per bank;
two read ports/bank; at most four admissions/cycle. No RTL/physical claim.
Run: python research/v317/rtl/queued_selector_falsification_20261107.py
"""
import random

SEEDS = (11, 23, 37)
CYCLES = 20000
BANKS = 3

def arrivals(seed, hot):
    rng = random.Random(seed)
    for _ in range(CYCLES):
        batch = []
        for _ in range(3):
            if rng.random() < 0.68:
                a = 0 if rng.random() < hot else rng.randrange(BANKS)
                b = 0 if rng.random() < hot else rng.randrange(BANKS)
                batch.append((a, b))
        yield batch

def simulate(stream, policy):
    queue = []
    completed = 0
    total_wait = 0
    for cycle, batch in enumerate(stream):
        queue.extend((a, b, cycle) for a, b in batch)
        head = queue[:4]
        order = list(range(len(head)))
        if policy == "minimum_contention":
            order.sort(key=lambda i: (
                sum((head[i][0] in (x[0], x[1])) +
                    (head[i][1] in (x[0], x[1])) for x in head), i))
        elif policy == "weighted_contention":
            loads = [sum((a == j) + (b == j) for a, b, _ in head)
                     for j in range(BANKS)]
            order.sort(key=lambda i: (
                loads[head[i][0]] + loads[head[i][1]], i))
        else:
            raise ValueError(policy)
        used = [0] * BANKS
        selected = []
        for i in order:
            a, b, _ = head[i]
            demand = [int(a == j) + int(b == j) for j in range(BANKS)]
            if all(used[j] + demand[j] <= 2 for j in range(BANKS)):
                selected.append(i)
                used = [used[j] + demand[j] for j in range(BANKS)]
        for i in sorted(selected, reverse=True):
            total_wait += cycle - queue[i][2]
            queue.pop(i)
            completed += 1
    return completed, len(queue), total_wait / completed

def main():
    print("hot,seed,policy,completed,backlog,mean_completed_wait")
    for hot in (0.0, 0.3, 0.7):
        for seed in SEEDS:
            scores = {}
            for policy in ("minimum_contention", "weighted_contention"):
                score = simulate(arrivals(seed, hot), policy)
                scores[policy] = score
                print(f"{hot},{seed},{policy},{score[0]},{score[1]},{score[2]:.6f}")
            # Frozen adverse control: weighted must not be called a winner
            # solely from instantaneous admission when its queue service loses.
            if hot == 0.3:
                assert scores["weighted_contention"][0] < scores["minimum_contention"][0]
    print("PASS: all moderate-skew paired streams falsify weighted selector")

if __name__ == "__main__":
    main()
