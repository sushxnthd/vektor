"""Conditional four-slot service ceiling for the existing V317 evidence.

This is a falsification/sensitivity tool, not a GPU IPC model.

For an equal-port implementation operating on the same request distribution,
let r_s be the measured/theoretical instantaneous service ratio relative to the
strong compact-greedy control, r_f the clock ratio, r_o the occupancy/availability
ratio, and r_b an externally established bandwidth ceiling. Under the explicit
proportional-service assumption:

    G <= min(r_b, r_s * r_f * r_o)

A material gain threshold T is impossible whenever either r_b < T or
r_f*r_o < T/r_s.

Do not apply this law to latency-limited workloads, changed request
distributions, or queueing regimes unless those assumptions are independently
validated.
"""
from fractions import Fraction

MATERIALITY = Fraction(102, 100)

def bound(service_ratio, clock_ratio=Fraction(1), occupancy_ratio=Fraction(1),
          bandwidth_ratio=None, threshold=MATERIALITY):
    s = Fraction(service_ratio)
    f = Fraction(clock_ratio)
    o = Fraction(occupancy_ratio)
    t = Fraction(threshold)
    b = Fraction(bandwidth_ratio) if bandwidth_ratio is not None else None
    if min(s, f, o, t) <= 0 or s < 1 or (b is not None and b <= 0):
        raise ValueError("ratios must be positive and service_ratio >= 1")
    upper = s * f * o
    if b is not None:
        upper = min(upper, b)
    return {
        "upper_bound": upper,
        "material_gain_possible": upper >= t,
        "required_clock_times_occupancy": t / s,
        "required_bandwidth_ratio": t,
    }

def test():
    u16 = bound(Fraction(1001025, 1000000))
    sb70 = bound(Fraction(1002278, 1000000))
    u4 = bound(Fraction(1046683, 1000000))
    hot65 = bound(Fraction(1099869, 1000000))

    assert u16["upper_bound"] == Fraction(40041, 40000)
    assert not u16["material_gain_possible"]
    assert not sb70["material_gain_possible"]
    assert u4["material_gain_possible"]
    assert hot65["material_gain_possible"]

    assert u16["required_clock_times_occupancy"] == Fraction(13600, 13347)
    assert sb70["required_clock_times_occupancy"] == Fraction(510000, 501139)
    assert u4["required_clock_times_occupancy"] == Fraction(1020000, 1046683)
    assert hot65["required_clock_times_occupancy"] == Fraction(340000, 366623)

    # Even a large instantaneous-service headroom cannot clear the materiality
    # threshold when another resource ceiling dominates.
    assert not bound(Fraction(1099869, 1000000),
                     bandwidth_ratio=Fraction(101, 100))["material_gain_possible"]
    assert not bound(Fraction(3, 2),
                     clock_ratio=Fraction(2, 3))["material_gain_possible"]
    assert not bound(Fraction(3, 2),
                     occupancy_ratio=Fraction(1, 2))["material_gain_possible"]

    try:
        bound(Fraction(99, 100))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid service ratio accepted")

if __name__ == "__main__":
    test()
    regimes = {
        "uniform16": Fraction(1001025, 1000000),
        "samebank70": Fraction(1002278, 1000000),
        "uniform4": Fraction(1046683, 1000000),
        "hotbank65": Fraction(1099869, 1000000),
    }
    for name, s in regimes.items():
        x = bound(s)
        print(
            name,
            f"service={float(s):.6f}",
            f"required_fxo={float(x['required_clock_times_occupancy']):.6f}",
            "POSSIBLE" if x["material_gain_possible"] else "FALSIFIED",
        )
