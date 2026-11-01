"""Independent V317 audit of pre-route OpenSTA output-delay experiments.

Rejects missing paths, STA errors, and nonpositive arrivals.
No routed RC, setup signoff, silicon power, or GPU throughput is claimed.
"""
import argparse
import json
import re
from pathlib import Path

LABELS = ('source_fixed', 'pairwise_fixed', 'source_rotating', 'pairwise_rotating')
LOADS = ('0.002', '0.02', '0.1')


def parse_report(report):
    text = Path(report).read_text()
    if re.search(r'(?im)^(?:Error:|Warning:.*(?:unconstrained|no paths))', text):
        raise AssertionError('STA error or unconstrained/no-path warning: ' + str(report))
    if 'STA_PATH_BEGIN' not in text or 'STA_PATH_END' not in text:
        raise AssertionError('Missing bounded timing report: ' + str(report))
    block = text.split('STA_PATH_BEGIN', 1)[1].split('STA_PATH_END', 1)[0]
    if 'Startpoint:' not in block or 'Endpoint:' not in block:
        raise AssertionError('No concrete timed startpoint/endpoint: ' + str(report))
    arrivals = re.findall(r'(?im)^\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s+data arrival time\s*$', block)
    if not arrivals:
        raise AssertionError('Missing data arrival time: ' + str(report))
    arrival = float(arrivals[-1])
    if not 0 < arrival < 1000:
        raise AssertionError('Invalid arrival time: ' + str(report))
    return {
        'arrival_ns': arrival,
        'startpoint': re.search(r'(?m)^Startpoint:\s*(.*)$', block).group(1).strip(),
        'endpoint': re.search(r'(?m)^Endpoint:\s*(.*)$', block).group(1).strip(),
    }


def audit(directory):
    out = {}
    for load in LOADS:
        out[load] = {label: parse_report(directory / f'{label}_{load}.log') for label in LABELS}
    ratios = {}
    for load, row in out.items():
        ratios[load] = {
            'pairwise_fixed_vs_source_fixed_delay_ratio': round(row['pairwise_fixed']['arrival_ns'] / row['source_fixed']['arrival_ns'], 6),
            'pairwise_rotating_vs_source_rotating_delay_ratio': round(row['pairwise_rotating']['arrival_ns'] / row['source_rotating']['arrival_ns'], 6),
            'pairwise_rotating_vs_pairwise_fixed_delay_ratio': round(row['pairwise_rotating']['arrival_ns'] / row['pairwise_fixed']['arrival_ns'], 6),
        }
    return {
        'evidence_tier': 'NANGATE45_PRE_ROUTE_CELL_TIMING_WITH_EXTERNAL_OUTPUT_CAP',
        'input_transition_ns': 0.02,
        'output_load_pf': list(LOADS),
        'timed_paths': out,
        'delay_ratios': ratios,
        'clock_frequency_validated': False,
        'wire_rc_extracted': False,
        'placement_routing_done': False,
        'gpu_ipc_measured': False,
        'same_policy_intrinsic_service_gain': 1.0,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('directory', type=Path)
    args = p.parse_args()
    print(json.dumps(audit(args.directory), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
