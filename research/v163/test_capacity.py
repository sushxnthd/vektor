def test_boundary():
    for k in range(33):
        q = 1225 // (41 + 37*k)
        assert (q >= 2) == (k <= 15)
