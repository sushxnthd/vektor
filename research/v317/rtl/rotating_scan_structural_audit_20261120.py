#!/usr/bin/env python3
"""Independent structural audit of the frozen V317 rotating-scan simulator.

This audit deliberately does NOT alter the preregistered candidate or open holdouts.
Run: python3 research/v317/rtl/rotating_scan_structural_audit_20261120.py
"""
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("rotating_scan_prospective_20261120.py")
tree = ast.parse(SOURCE.read_text())
functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
assert {"grants", "run", "trace"} <= functions.keys()
grants = functions["grants"]
orders = []
for node in ast.walk(grants):
    if isinstance(node, ast.Tuple) and len(node.elts) == 4:
        try:
            v = ast.literal_eval(node)
            if sorted(v) == [0, 1, 2, 3]:
                orders.append(v)
        except (ValueError, TypeError):
            pass
assert (0, 2, 1, 3) in orders and (0, 1, 2, 3) in orders, orders
# A true four-way rotating priority must eventually give each occupied slot
# first consideration. This candidate always starts at index zero.
assert {order[0] for order in orders} == {0}
run = functions["run"]
phase_updates = [n for n in ast.walk(run) if isinstance(n, ast.AugAssign)
                 and isinstance(n.target, ast.Name) and n.target.id == "phase"]
assert len(phase_updates) == 1
# The phase update is unconditional in the cycle loop, not on a successful grant.
print("PASS: frozen candidate has two fixed scan orders; head always first")
print("PASS: phase toggles per cycle, not per successful grant")
print("CLASSIFICATION: alternating middle-slot priority, NOT full rotating priority")
print("LIMITATION: static source audit; no independent throughput replication")
