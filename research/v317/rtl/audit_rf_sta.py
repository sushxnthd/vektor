"""Independent V317 audit of pre-route OpenSTA output-delay experiments.

Rejects missing paths, STA errors, and nonpositive arrivals.
No routed RC, setup signoff, silicon power, or GPU throughput is claimed.
"""
import argparse
import json
import re
from pathlib import Path

LABELS = ('source_fixed', 'pairwise_fixed', 'source_rotating', 'pairwise_rotating')
LOADS = ('2', '20', '40', '60', '80', '100')  # Nangate45 capacitive_load_unit (1, ff)


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
    arrival = float(arrivals[0])  # first is forward arrival; later negative value is slack subtraction
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
    holdouts = {}
    for load in ('40', '60', '80'):
        observed = out[load]['pairwise_fixed']['arrival_ns'] - out[load]['source_fixed']['arrival_ns']
        predicted = -0.58 + (float(load) - 20.0) * (1.19 / 80.0)
        holdouts[load] = {
            'predicted_pairwise_minus_source_ns': round(predicted, 6),
            'observed_pairwise_minus_source_ns': round(observed, 6),
            'prediction_residual_ns': round(observed - predicted, 6),
            'frozen_qualitative_prediction_survives':
                (observed < 0 if load == '40' else
                 observed > 0 if load == '80' else
                 abs(observed) <= 0.20),
        }
    return {
        'frozen_holdout_predictions': holdouts,
        'frozen_qualitative_boundary_survives': all(
            x['frozen_qualitative_prediction_survives'] for x in holdouts.values()),
        'max_abs_holdout_interpolation_error_ns': round(max(
            abs(x['prediction_residual_ns']) for x in holdouts.values()), 6),
        'frozen_predicted_crossover_ff': round(20 + 80 * (0.58 / 1.19), 3),
        'evidence_tier': 'NANGATE45_PRE_ROUTE_CELL_TIMING_WITH_EXTERNAL_OUTPUT_CAP',
        'input_transition_ns': 0.02,
        'output_load_ff': list(LOADS),
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
