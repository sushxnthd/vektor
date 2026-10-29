#!/usr/bin/env python3
"""Independent occupancy-law check for V302's warp-aggregated FIFO control.
Classical occupancy identity, not a novel V302 throughput law.
"""
import json
import sys

PARAMS = {
    'H1': (.8, [.55, .15, .12, .10, .08]),
    'H2': (.35, [1 / 256] * 256),
    'H3': (.75, [.55, .15, .12, .10, .08]),
    'H4': (.05, [1 / 32] * 32),
    'H5': (.8, [.8, .2]),
}


def predict(rate, probs, lanes=4, warps=4):
    unique = sum(1 - (1 - p) ** lanes for p in probs)
    return min(warps * rate * lanes, lanes / unique)


def check(result):
    errors = {}
    for regime, (rate, probs) in PARAMS.items():
        expected = predict(rate, probs)
        observed = result['regimes'][regime]['mean']['fifo']['throughput']
        error = abs(observed / expected - 1)
        errors[regime] = {'predicted': expected, 'observed': observed,
                          'relative_error': error}
        assert error < .005, (regime, error)
    return errors


if __name__ == '__main__':
    with open(sys.argv[1] if len(sys.argv) > 1 else 'v302_holdout.json') as f:
        result = json.load(f)
    print(json.dumps(check(result), indent=2, sort_keys=True))
