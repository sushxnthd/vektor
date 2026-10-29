"""Independent focused V304 checks; run with pytest -q research/v304/test_bank_color.py."""
from research.v304.bank_color import bank, run, trace, independent_check

def test_bijection_and_pair_oracle():
    assert independent_check() == {"mapping_checks": 96, "pair_oracle_checks": 3072}

def test_one_bank_two_distinct_registers_are_serialized():
    workload = [[(0, 16)] * 128]
    for policy in ("modulo", "xor", "add"):
        r = run(workload, policy, 1)
        assert r.instructions == 128 and r.cycles == 256 and r.max_bank_demand == 1

def test_two_ports_allow_same_bank_sources_in_one_cycle():
    workload = [[(0, 16)] * 128]
    for policy in ("modulo", "xor", "add"):
        r = run(workload, policy, 2)
        assert r.cycles == 128 and r.max_bank_demand == 2

def test_frozen_h1_equal_to_xor_and_superior_to_modulo():
    t, ports = trace("H1_aligned", 901)
    base = run(t, "modulo", ports)
    xor = run(t, "xor", ports)
    add = run(t, "add", ports)
    assert add.instructions == xor.instructions == base.instructions == 4096
    assert add.cycles == xor.cycles == 1024 and base.cycles == 4096

def test_seeded_random_reproducible():
    t1, p1 = trace("H2_random", 903)
    t2, p2 = trace("H2_random", 903)
    assert (t1, p1) == (t2, p2)
    assert run(t1, "add", p1) == run(t2, "add", p2)
