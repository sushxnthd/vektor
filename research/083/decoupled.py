"""Vektor-083: bounded FIFO after banked pipelined operand collectors.

SIMULATED only. No dependencies, execution latencies, cache coherence, RTL or PPA.
"""
from dataclasses import dataclass
from random import Random

@dataclass
class Collector:
    state: int = 0
    job: tuple = ()
    next_operand: int = 0
    replies: int = 0
    pending: int = 0

def make_jobs(n, src_count, banks, pattern, seed):
    rng = Random(seed)
    jobs = []
    for i in range(n):
        if pattern == "spread":
            job = tuple((i * src_count + j) % banks for j in range(src_count))
        elif pattern == "hot":
            job = (0,) * src_count
        elif pattern == "skew":
            job = tuple(0 if rng.random() < 0.8 else rng.randrange(banks) for _ in range(src_count))
        elif pattern == "random":
            job = tuple(rng.randrange(banks) for _ in range(src_count))
        elif pattern == "intra_bank":
            job = (i % banks,) * src_count
        else:
            raise ValueError(pattern)
        jobs.append(job)
    return jobs

def simulate_jobs(jobs, collectors=20, fifo=4, banks=16, ports=2, issue_width=4):
    if not jobs or min(collectors, banks, ports, issue_width) < 1 or fifo < 0:
        raise ValueError("invalid dimensions")
    if any(not job or any(b < 0 or b >= banks for b in job) for job in jobs):
        raise ValueError("invalid operands")
    cs = [Collector() for _ in range(collectors)]
    admitted = retired = reads = bank_stalls = queue_stalls = cycles = 0
    queue = rr = max_fifo = issue_idle_slots = 0
    while retired < len(jobs):
        cycles += 1
        if cycles > len(jobs) * (max(map(len, jobs)) * 3 + 5) * 20:
            raise RuntimeError("no progress")
        # FIFO is drained before new enqueues; no zero-cycle bypass.
        issued = min(issue_width, queue) if fifo else 0
        queue -= issued
        retired += issued
        credits = [ports] * banks
        for off in range(collectors):
            c = cs[(rr + off) % collectors]
            if c.state == 0:
                if admitted < len(jobs):
                    c.job = jobs[admitted]
                    admitted += 1
                    c.next_operand = c.replies = c.pending = 0
                    c.state = 1
            elif c.state == 1:
                c.replies += c.pending
                c.pending = 0
                if c.next_operand < len(c.job):
                    bank = c.job[c.next_operand]
                    if credits[bank]:
                        credits[bank] -= 1
                        c.next_operand += 1
                        c.pending = 1
                        reads += 1
                    else:
                        bank_stalls += 1
                if c.replies == len(c.job):
                    assert c.pending == 0
                    c.state = 2
            elif c.state == 2:
                if fifo == 0:
                    if issued < issue_width:
                        issued += 1
                        retired += 1
                        c.state = 0
                elif queue < fifo:
                    queue += 1
                    c.state = 0
                else:
                    queue_stalls += 1
        issue_idle_slots += issue_width - issued
        max_fifo = max(max_fifo, queue)
        rr = (rr + 1) % collectors
    assert admitted == retired == len(jobs)
    assert reads == sum(map(len, jobs)) and queue == 0
    assert all(c.state == 0 for c in cs)
    return dict(cycles=cycles, completed=retired, throughput=retired / cycles,
                requests=reads, bank_stalls=bank_stalls, queue_stalls=queue_stalls,
                max_fifo=max_fifo, issue_idle_slots=issue_idle_slots)

def simulate(collectors=20, fifo=4, src_count=2, banks=16, ports=2,
             pattern="spread", instructions=1200, seed=0, issue_width=4):
    return simulate_jobs(make_jobs(instructions, src_count, banks, pattern, seed),
                         collectors, fifo, banks, ports, issue_width)
