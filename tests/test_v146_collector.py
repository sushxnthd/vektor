"""V146 independent collector-model regression. Not an HDL test."""
import importlib.util
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "research/v146/verification/collector_oracle.py"
spec = importlib.util.spec_from_file_location("v146_collector_oracle", p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_frozen_seed_146():
    out = module.run(146, 50000)
    assert out["matched"] == 50000
    assert out["retired"] == 8739
    assert out["blocked_same_bank"] == 2823

def test_unseen_seeds():
    for seed in (20261013, 5090, 141):
        out = module.run(seed, 10000)
        assert out["matched"] == 10000
        assert out["retired"] > 100
        assert out["blocked_same_bank"] > 10
