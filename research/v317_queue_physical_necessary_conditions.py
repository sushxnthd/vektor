"""V317 necessary physical break-even from paired persistent-queue observations.

Evidence tier: algebraic falsification of previously reported seed-11 counts,
NOT an independent queue-simulator replay, RTL result, or synthesis measurement.
Source: research experiment 34e0c003fe0db07d1a69995361f42bdebe524b87.
Assume equal work per completion and equal 20,000-cycle observation windows.
Throughput ratio = service_ratio * FIFO_period/candidate_period *
candidate_useful_fraction/FIFO_useful_fraction.
This is necessary, not sufficient, for workload-level performance.
"""
from fractions import Fraction

DATA = {
    "uniform_seed11": (40916, 40910),
    "moderate_skew_seed11": (28782, 35764),
    "severe_skew_seed11": (20932, 24091),
}

def boundary(candidate, fifo):
    service = Fraction(candidate, fifo)
    return service, 1 / service

def main():
    for regime, (candidate, fifo) in DATA.items():
        service, useful_required = boundary(candidate, fifo)
        assert service * useful_required == 1
        print(f"{regime}: service_ratio={float(service):.9f}; "
              f"maximum_candidate_period_ratio={float(service):.9f}; "
              f"minimum_useful_fraction_ratio_at_equal_period={float(useful_required):.9f}; "
              f"required_period_reduction_pct={100*(1-float(service)):.4f}")
    assert boundary(28782, 35764)[0] < Fraction(81, 100)
    assert boundary(20932, 24091)[0] < Fraction(87, 100)
    assert boundary(40916, 40910)[0] > 1
    print("PASS: exact-rational crossover assertions")

if __name__ == "__main__":
    main()
