"""Vektor-082: resource upper bounds, not GPU throughput."""
def max_issue_rate(issue_width, banks, ports, sources, hot_bank=False):
    if min(issue_width, banks, ports, sources) < 1:
        raise ValueError("positive parameters required")
    rf_limit = ports / sources if hot_bank else banks * ports / sources
    return min(issue_width, rf_limit)

if __name__ == "__main__":
    assert max_issue_rate(4, 16, 2, 2, True) == 1
    assert max_issue_rate(4, 16, 2, 4, True) == 0.5
    assert max_issue_rate(4, 16, 2, 2, False) == 4
    print("Vektor-082 analytic bounds: PASS")
