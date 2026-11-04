#!/usr/bin/env python3
"""Fail-closed ordered bank-demand replay for V317; not a GPU throughput claim.

Strict FIFO stops at the first bank-blocked head. Greedy may bypass blocked
requests but is neither an optimal throughput upper bound nor an equal-resource RTL.\nGreedy can be suboptimal even for one cycle (requests [0,1], [0], [1]).


Input JSONL: first record {"kind":"provenance","source_sha256":"<64 hex>",
"generator_commit":"<40 hex>","kernel":"...","capture_method":"...",
"ordering":"observed","units":"requests_per_cycle"}.
Subsequent records: {"cycle":0,"requests":[{"id":"unique","banks":[0,1]},...]}.
Records must have consecutive cycles and unique request IDs. No fabricated traces.
"""
import argparse
import json
import re
from collections import deque
from pathlib import Path

def load(path, banks):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    if len(rows) < 2:
        raise ValueError("provenance and cycles required")
    p = rows.pop(0)
    required = ("source_sha256", "generator_commit", "kernel", "capture_method")
    if p.get("kind") != "provenance" or p.get("ordering") != "observed" or p.get("units") != "requests_per_cycle":
        raise ValueError("non-observed or undocumented trace")
    if not re.fullmatch(r"[0-9a-f]{64}", str(p.get("source_sha256", ""))):
        raise ValueError("source hash required")
    if not re.fullmatch(r"[0-9a-f]{40}", str(p.get("generator_commit", ""))):
        raise ValueError("pinned generator commit required")
    if any(not str(p.get(k, "")).strip() for k in required):
        raise ValueError("incomplete provenance")
    seen = set()
    for t, row in enumerate(rows):
        if row.get("cycle") != t or not isinstance(row.get("requests"), list):
            raise ValueError("cycles must be consecutive starting at zero")
        for r in row["requests"]:
            ident = r.get("id")
            bs = r.get("banks")
            if not isinstance(ident, (str, int)) or ident in seen:
                raise ValueError("request IDs must be unique")
            seen.add(ident)
            if not isinstance(bs, list) or not bs or any(type(b) is not int or b < 0 or b >= banks for b in bs):
                raise ValueError("invalid bank operands")
    return p, rows

def replay(rows, banks, ports, slots, output, policy):
    if min(banks, ports, slots, output) < 1:
        raise ValueError("resource counts must be positive")
    for row in rows:
        for req in row["requests"]:
            for bank in set(req["banks"]):
                if req["banks"].count(bank) > ports:
                    raise ValueError("unschedulable request: bank operand multiplicity exceeds ports")
    queue = deque()
    completed = 0
    busy = 0
    peak = 0
    for row in rows:
        queue.extend(row["requests"])
        peak = max(peak, len(queue))
        usage = [0] * banks
        selected = []
        if policy == "fifo":
            candidates = list(queue)[:slots]
        elif policy == "greedy":
            candidates = list(queue)
        else:
            raise ValueError(policy)
        for req in candidates:
            if len(selected) >= min(slots, output):
                break
            need = [req["banks"].count(b) for b in range(banks)]
            if all(usage[b] + need[b] <= ports for b in range(banks)):
                selected.append(req["id"])
                usage = [usage[b] + need[b] for b in range(banks)]
            elif policy == "fifo":
                # Head-of-line blocking: later requests cannot bypass the head.
                break
        done = set(selected)
        queue = deque(r for r in queue if r["id"] not in done)
        completed += len(done)
        busy += bool(done)
    arrivals = sum(len(r["requests"]) for r in rows)
    assert arrivals == completed + len(queue)
    return {"arrivals": arrivals, "completed": completed, "backlog": len(queue),
            "peak_backlog": peak, "busy_cycles": busy, "cycles": len(rows)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--banks", type=int, required=True)
    ap.add_argument("--ports", type=int, required=True)
    ap.add_argument("--slots", type=int, required=True)
    ap.add_argument("--output", type=int, required=True)
    a = ap.parse_args()
    if min(a.banks, a.ports, a.slots, a.output) < 1:
        ap.error("all resource counts must be positive")
    provenance, rows = load(a.trace, a.banks)
    result = {policy: replay(rows, a.banks, a.ports, a.slots, a.output, policy)
              for policy in ("fifo", "greedy")}
    print(json.dumps({"provenance": provenance, "resources": vars(a),
                      "results": result, "evidence_tier": "trace-replay-only; no RTL/physical validation"},
                     sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
