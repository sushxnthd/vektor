"""Source-pinned JSON evidence for the V317 register-identity reuse challenge."""
import json
from research.v317.operand_identity_reuse import (
    evaluate, make_instructions, independent_partition_optimum, predicted_cycles,
)
from research.v317.test_operand_identity_reuse import FROZEN


def main():
    frozen = {}
    for name, (a,b,s,k,expected) in FROZEN.items():
        result = evaluate(a,b,s,k)
        actual = tuple(x[0] for x in result)
        if actual != expected:
            raise AssertionError(f"frozen prediction failed: {name} {actual} != {expected}")
        frozen[name] = {
            "a":a,"b":b,"shared_B_identity_pairs":s,"K":k,
            "baseline_cycles":actual[0],"candidate_cycles":actual[1],
            "ideal_service_gain":actual[0]/actual[1],
            "baseline_witness":[list(x) for x in result[0][1]],
            "candidate_witness":[list(x) for x in result[1][1]],
        }
    worlds, independent_checks, mismatches = 0, 0, []
    for a in range(5):
        for b in range(5):
            if a+b == 0:
                continue
            for s in range(min(a,b)+1):
                for k in (1,2,3):
                    observed = tuple(x[0] for x in evaluate(a,b,s,k))
                    predicted = predicted_cycles(a,b,s,k)
                    if observed != predicted:
                        mismatches.append([a,b,s,k,list(predicted),list(observed)])
                    for candidate, cycles in zip((False,True),observed):
                        if a+b <= 7:
                            rows = make_instructions(a,b,s,candidate)
                            if independent_partition_optimum(rows,k) != cycles:
                                raise AssertionError("independent partition oracle disagrees")
                            independent_checks += 1
                    worlds += 1
    if mismatches or worlds != 162:
        raise AssertionError(f"law mismatch: {mismatches}")
    print(json.dumps({
        "evidence_tier":"exact idealized synthetic service cycles; NOT GPU IPC or physical timing",
        "mechanism":"hypothetical AB B-read elimination, not implemented",
        "strong_baseline":"same-value B-bank multicast to at most two admitted collectors",
        "physical_caveat":"B multicast, cache, bank mapping, control/wire costs not measured",
        "frozen_regimes":frozen,
        "worlds_checked":worlds,
        "independent_partition_checks":independent_checks,
        "law_mismatches":mismatches,
        "law":"K=1: T0=T1=a+b; K>=2: T0=a+b-s; T1=max(a,b)",
    },sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
