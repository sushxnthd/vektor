#!/usr/bin/env python3
import random, json

SEED = 1447381844
CASES = 250000

def parts(u):
    sign = u >> 31
    exp = (u >> 23) & 255
    frac = u & 0x7fffff
    if exp == 255:
        return None
    if exp == 0:
        return sign, frac, -149
    return sign, (1 << 23) | frac, exp - 150

def finite(rng):
    while True:
        u = rng.getrandbits(32)
        if ((u >> 23) & 255) != 255:
            return u

def depth(a, b, c):
    pa, pb, pc = parts(a), parts(b), parts(c)
    sa, ma, ea = pa
    sb, mb, eb = pb
    sc, mc, ec = pc
    if ma == 0 or mb == 0 or mc == 0 or (sa ^ sb) == sc:
        return None
    mp, ep = ma * mb, ea + eb
    base = min(ep, ec)
    x = mp << (ep - base)
    y = mc << (ec - base)
    before = max(x.bit_length(), y.bit_length())
    after = abs(x - y)
    return before if after == 0 else before - after.bit_length()

def main():
    rng = random.Random(SEED)
    directed = [
        (0x3f800000, 0x3f800000, 0xbf800000),
        (0x3f800000, 0x3f800000, 0xbf7fffff),
        (0x3f800001, 0x3f800000, 0xbf800000),
        (0x00800000, 0x3f800000, 0x807fffff),
    ]
    hist = {}
    maximum = -1
    witness = None
    eligible = 0
    for i in range(CASES + len(directed)):
        triple = directed[i] if i < len(directed) else (finite(rng), finite(rng), finite(rng))
        d = depth(*triple)
        if d is None:
            continue
        eligible += 1
        hist[d] = hist.get(d, 0) + 1
        if d > maximum:
            maximum = d
            witness = [hex(x) for x in triple]
    assert depth(*directed[0]) >= 24
    print(json.dumps({
        "experiment": "FP32-CANCEL-012",
        "seed": SEED,
        "random_cases": CASES,
        "eligible_cases": eligible,
        "max_cancelled_leading_bits": maximum,
        "max_witness": witness,
        "histogram": hist,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
