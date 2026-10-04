#!/usr/bin/env python3
"""Independent finite-FP32 multiply-stage contract checker.

This does not validate the complete FMA. It attacks only the bounded frontend
contract with an independently written IEEE-754 decoder using Fraction.
"""
from __future__ import annotations
from fractions import Fraction
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sim.vektor.fp32_stage_contract import classify, finite_exact_pair

SEED = 0x5090
N = 200_000

def ieee_fraction(bits: int) -> Fraction:
    sign = -1 if bits >> 31 else 1
    e = (bits >> 23) & 0xff
    f = bits & 0x7fffff
    if e == 0xff:
        raise ValueError("non-finite")
    if e == 0:
        n, q = f, -149
    else:
        n, q = (1 << 23) | f, e - 150
    return sign * Fraction(n * (1 << max(q, 0)), 1 << max(-q, 0))

def pair_fraction(bits: int) -> Fraction:
    s, n, q = finite_exact_pair(bits)
    mag = Fraction(n * (1 << max(q, 0)), 1 << max(-q, 0))
    return -mag if s else mag

def main() -> None:
    rng = random.Random(SEED)
    checked = 0
    # Directed exponent/subnormal/sign boundaries.
    directed = [
        0x00000000,0x80000000,0x00000001,0x007fffff,0x00800000,
        0x3f800000,0x3f000000,0x7f7fffff,0xff7fffff,
    ]
    finite = directed[:]
    while len(finite) < N:
        x = rng.getrandbits(32)
        if classify(x) in ("zero","finite"):
            finite.append(x)
    for x in finite:
        assert pair_fraction(x) == ieee_fraction(x), hex(x)
        checked += 1
    # Independent exact-product check over paired operands.
    for i in range(0, len(finite)-1, 2):
        a,b = finite[i],finite[i+1]
        sa,na,qa = finite_exact_pair(a)
        sb,nb,qb = finite_exact_pair(b)
        product_pair = Fraction(((-1 if sa ^ sb else 1) * na * nb) * (1 << max(qa+qb,0)),
                                1 << max(-(qa+qb),0))
        assert product_pair == ieee_fraction(a) * ieee_fraction(b), (hex(a),hex(b))
    print(f"PASS finite decode={checked} exact products={len(finite)//2} seed={SEED:#x}")

if __name__ == "__main__":
    main()
