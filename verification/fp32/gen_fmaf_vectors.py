from __future__ import annotations

import ctypes
import random
import struct
from pathlib import Path

SEED = 5090
RANDOM_CASES = 8000
TARGETED_CASES = 2000


def f32_from_bits(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits & 0xFFFFFFFF))[0]


def bits_from_f32(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def is_nan(bits: int) -> bool:
    return ((bits >> 23) & 0xFF) == 0xFF and (bits & 0x7FFFFF) != 0


def main() -> None:
    libm = ctypes.CDLL("libm.so.6")
    libm.fmaf.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
    libm.fmaf.restype = ctypes.c_float
    if hasattr(libm, "fesetround"):
        # glibc FE_TONEAREST is zero on the Ubuntu CI target.
        libm.fesetround(0)

    def ref(a: int, b: int, c: int) -> int:
        out = libm.fmaf(
            ctypes.c_float(f32_from_bits(a)),
            ctypes.c_float(f32_from_bits(b)),
            ctypes.c_float(f32_from_bits(c)),
        )
        bits = bits_from_f32(out)
        # NaN payload/sign propagation is not the subject of this gate;
        # Vektor currently emits a canonical quiet NaN.
        return 0x7FC00000 if is_nan(bits) else bits

    rng = random.Random(SEED)
    cases: list[tuple[int, int, int]] = []

    edge = [
        0x00000000, 0x80000000,
        0x00000001, 0x80000001,
        0x007FFFFF, 0x807FFFFF,
        0x00800000, 0x80800000,
        0x3EFFFFFF, 0x3F000000, 0x3F800000, 0xBF800000,
        0x40000000, 0xC0000000,
        0x7F7FFFFF, 0xFF7FFFFF,
        0x7F800000, 0xFF800000,
        0x7FC00000, 0x7F800001,
    ]

    deterministic = [
        (0x3F800000, 0x3F800000, 0x3F800000),
        (0x3F800000, 0x3F800000, 0xBF800000),
        (0x7F7FFFFF, 0x40000000, 0x00000000),
        (0x00000001, 0x3F000000, 0x00000000),
        (0x00000001, 0x3F800000, 0x00000000),
        (0x7F800000, 0x00000000, 0x00000000),
        (0x7F800000, 0x3F800000, 0xFF800000),
        (0x80000000, 0x3F800000, 0x80000000),
    ]
    cases.extend(deterministic)

    for _ in range(TARGETED_CASES):
        cases.append((rng.choice(edge), rng.choice(edge), rng.choice(edge)))
    for _ in range(RANDOM_CASES):
        cases.append((rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)))

    out_path = Path("build/rtl/fmaf_vectors.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="ascii") as f:
        for a, b, c in cases:
            f.write(f"{a:08x} {b:08x} {c:08x} {ref(a, b, c):08x}\n")

    print(f"wrote {len(cases)} fused binary32 vectors to {out_path}")


if __name__ == "__main__":
    main()
