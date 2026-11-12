#!/usr/bin/env python3
"""Historical V317 compact/pairwise proxy audit; NOT electrical signoff or GPU IPC."""
import json
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).with_name("STRONG_BASELINE_THREE_WAY_AUDIT_20261102.json")
D = Decimal

def audit(data):
    v = data["variants"]
    c, p = v["compact"], v["pairwise"]
    def n(x, key): return D(str(x[key]))
    area = n(p,"area_um2") / n(c,"area_um2")
    clock = n(p,"fmax_mhz") / n(c,"fmax_mhz")
    power = n(p,"power_proxy_mw") / n(c,"power_proxy_mw")
    wire = n(p,"wire_um") / n(c,"wire_um")
    energy_proxy = power / clock
    assert area > 1 and clock < 1 and power < 1 and wire > 1
    assert energy_proxy > 1
    assert c["max_cap_violations"] > 0 and p["max_cap_violations"] > 0
    assert c["legal"] is False and p["legal"] is False
    assert c["macro_count"] == p["macro_count"] == 0
    return {
        "pairwise_over_compact_area": str(area),
        "pairwise_over_compact_fmax": str(clock),
        "pairwise_over_compact_power_proxy": str(power),
        "pairwise_over_compact_wire": str(wire),
        "pairwise_over_compact_power_per_clock_proxy": str(energy_proxy),
        "minimum_pairwise_cycle_reduction_for_proxy_energy_win": str(1 - 1 / energy_proxy),
        "minimum_pairwise_cycle_reduction_for_throughput_win": str(1 - clock),
        "electrically_legal": False,
    }

if __name__ == "__main__":
    print(json.dumps(audit(json.loads(DATA.read_text())), indent=2))
