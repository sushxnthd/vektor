"""V271 training-only behavioral conservation checks. Frozen holdouts untouched."""
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("v271_model",Path(__file__).resolve().parents[1]/"research/v271/v271_model.py")
v271=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v271)

def test_all_seven_equal_storage_modes_conserve_requests():
    for mode in v271.MODES:
        for profile in ("alternating","balanced","single_skew","divergent"):
            result=v271.run(mode,profile,seed=271001,cycles=720,latency=24)
            assert result["completed"]==result["offered"]
            assert result["mean_completion_latency"]>=24

def test_positive_boundary_on_training_only():
    results={mode:v271.run(mode,"alternating",seed=271001,cycles=3600,latency=30)
             for mode in v271.MODES}
    fixed=min(results[m]["mean_completion_latency"] for m in v271.MODES if m.startswith("fixed"))
    assert results["hybrid"]["mean_completion_latency"]<fixed
    assert results["global"]["mean_completion_latency"]<=results["hybrid"]["mean_completion_latency"]

def test_negative_boundaries_on_training_only():
    balanced={m:v271.run(m,"balanced",seed=271001,cycles=3600,latency=12)
              for m in ("fixed44","hybrid")}
    skew={m:v271.run(m,"single_skew",seed=271001,cycles=3600,latency=42)
          for m in ("fixed62","hybrid","global")}
    assert balanced["hybrid"]["mean_completion_latency"]>=balanced["fixed44"]["mean_completion_latency"]
    assert skew["hybrid"]["mean_completion_latency"]>skew["fixed62"]["mean_completion_latency"]
    assert skew["hybrid"]["mean_completion_latency"]>skew["global"]["mean_completion_latency"]

def test_holdout_manifest_is_frozen_and_unopened():
    freeze=v271.frozen()
    assert freeze["sha256"]=="cedbe1c2ebb9b526f2137c560c72acc9d4ad6372fe0d24cb0a3af8d715b614a7"
    assert freeze["holdouts_evaluated"] is False
