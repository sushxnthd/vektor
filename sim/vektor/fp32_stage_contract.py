from __future__ import annotations

import struct

def bits_to_float32(bits: int) -> float:
    return struct.unpack(">f", struct.pack(">I", bits & 0xFFFFFFFF))[0]

def classify(bits: int) -> str:
    exp=(bits>>23)&0xFF; frac=bits&0x7FFFFF
    if exp==0xFF:
        if frac==0: return "inf"
        return "qnan" if (frac>>22)&1 else "snan"
    if exp==0 and frac==0: return "zero"
    return "finite"

def sig24(bits: int) -> int:
    exp=(bits>>23)&0xFF
    frac=bits&0x7FFFFF
    return frac if exp==0 else (1<<23)|frac

def qexp(bits: int) -> int:
    exp=(bits>>23)&0xFF
    return -149 if exp==0 else exp-150

def finite_exact_pair(bits: int) -> tuple[int,int,int]:
    """Return sign, integer significand, binary exponent for finite FP32.

    Exact value is (-1)^sign * significand * 2**exponent.
    This mirrors the bounded RTL multiply-stage contract.
    """
    if classify(bits) not in ("zero","finite"):
        raise ValueError("special FP32 has no finite exact pair")
    return (bits>>31)&1, sig24(bits), qexp(bits)
