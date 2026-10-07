"""FP32 CLOSE-path width/classification invariants.

This is a cheap exhaustive abstract proof over all legal significand widths and
the three effective-leading-exponent deltas admitted by CLOSE.  It deliberately
separates cancellation from same-sign addition so CI cannot regress the contract.
"""

def _aligned_maxima(prod_width: int, c_width: int, lead_delta: int):
    # Set product LSB exponent to zero without loss of generality.  Choose c's
    # LSB exponent so lead_p - lead_c == lead_delta.
    ep = 0
    ec = prod_width - c_width - lead_delta
    base = min(ep, ec)
    p = ((1 << prod_width) - 1) << (ep - base)
    c = ((1 << c_width) - 1) << (ec - base)
    return p, c


def test_opposite_sign_close_difference_fits_49_bits():
    worst = 0
    for prod_width in range(1, 49):
        for c_width in range(1, 25):
            for lead_delta in (-1, 0, 1):
                p, c = _aligned_maxima(prod_width, c_width, lead_delta)
                worst = max(worst, abs(p - c).bit_length())
    assert worst <= 49


def test_same_sign_close_is_not_covered_by_49_bit_contract():
    # Exhaustively establish that at least one legal abstract CLOSE geometry
    # needs a 50th sum bit.  This is why RTL must require opposite signs.
    witnesses = []
    for prod_width in range(1, 49):
        for c_width in range(1, 25):
            for lead_delta in (-1, 0, 1):
                p, c = _aligned_maxima(prod_width, c_width, lead_delta)
                if (p + c).bit_length() > 49:
                    witnesses.append((prod_width, c_width, lead_delta))
    assert witnesses, "same-sign routing guard lost its width justification"


def test_raw_lsb_delta_is_not_a_valid_close_classifier():
    # Real FMA operands have different significand widths (48b product, 24b c).
    # Equal effective leading exponents can therefore coexist with a 24-bit
    # LSB-exponent gap.  A raw-LSB classifier would miss this cancellation.
    prod_width, c_width = 48, 24
    prod_lsb, c_lsb = 0, 24
    prod_lead = prod_lsb + prod_width - 1
    c_lead = c_lsb + c_width - 1
    assert prod_lead == c_lead
    assert abs(prod_lsb - c_lsb) == 24
