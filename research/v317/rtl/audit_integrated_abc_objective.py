#!/usr/bin/env python3
"""Independently compare V317 area/speed ABC objectives from immutable ORFS ZIPs.

Usage: python audit_integrated_abc_objective.py area_artifact.zip speed_artifact.zip
Evidence: GitHub Actions 41352990340 and 41354169431, Nangate45 typical.
The script deliberately reports failed timing/electrical checks rather than treating route exit=0 as signoff.
"""
import argparse
import json
import math
import re
import zipfile

DIGEST = 'sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8'
SOURCES = {'area': '20c5165651d0a941d3c60f918e4255961b8a2a90',
           'speed': 'cac1d1185ee77179257b451805df7b65c664eafb'}


def inspect(archive_path, objective):
    prefix = {'area': 'integrated', 'speed': 'timing'}[objective]
    script = {'area': 'abc_area.script', 'speed': 'abc_speed.script'}[objective]
    with zipfile.ZipFile(archive_path) as z:
        names = set(z.namelist())

        def read(path):
            if path not in names:
                raise AssertionError('missing ' + path)
            return z.read(path).decode('utf-8', 'replace')

        assert read('source_sha.txt').strip() == SOURCES[objective]
        assert DIGEST in read('pinned_image.txt')
        assert DIGEST in read('container_digests.json')
        assert 'PASS V317 integrated issue-control equivalence cycles=4096 accepted=13153' in read('rtl_simulation.log')
        out = {}
        for variant in ('source', 'pairwise'):
            top = 'vektor_v317_issue_integrated_top_' + variant
            root = f'{prefix}_{variant}/'
            log = root + f'logs/nangate45/{top}/base/'
            assert 'exit_code=0' in read(root + 'status.txt')
            yosys = read(log + '1_2_yosys.log')
            assert 'Using ABC ' + ('area' if objective == 'area' else 'speed') + ' script.' in yosys
            assert script in yosys
            assert ('abc_speed.script' if objective == 'area' else 'abc_area.script') not in yosys
            m = json.loads(read(log + '6_report.json'))
            route = read(log + '5_2_route.log')
            extraction = read(log + '6_report.log')
            assert 'RCX-0045' in extraction
            drcs = re.findall(r'Number of violations\\s*=\\s*(\\d+)', route)
            assert drcs and int(drcs[-1]) == 0
            assert 'Found 0 net violations' in route and 'Found 0 pin violations' in route
            wires = re.findall(r'Total wire length\\s*=\\s*(\\d+)\\s*um', route)
            assert wires

            def val(key):
                return m['finish__' + key]

            assert val('design__instance__count__class:sequential_cell') == 356
            assert val('design__instance__count__macros') == 0
            out[variant] = {
                'area_um2': val('design__instance__area__stdcell'),
                'wire_um': int(wires[-1]),
                'fmax_mhz': val('timing__fmax') / 1e6,
                'setup_slack_ps': val('timing__setup__ws') * 1000,
                'setup_violations': val('timing__drv__setup_violation_count'),
                'hold_slack_ps': val('timing__hold__ws') * 1000,
                'hold_violations': val('timing__drv__hold_violation_count'),
                'max_cap_violations': val('timing__drv__max_cap'),
                'max_slew_violations': val('timing__drv__max_slew'),
                'max_fanout_violations': val('timing__drv__max_fanout'),
                'default_activity_power_mw': val('power__total') * 1000,
                'timing_repair_buffers': val('design__instance__count__class:timing_repair_buffer'),
                'route_drc_violations': int(drcs[-1]),
            }
    return out


def audit(area_zip, speed_zip):
    area = inspect(area_zip, 'area')
    speed = inspect(speed_zip, 'speed')
    result = {'provenance': {'area_run': 41352990340, 'speed_run': 41354169431,
                             'image_digest': DIGEST, 'source_shas': SOURCES},
              'area_objective': area, 'speed_objective': speed}
    for v in ('source', 'pairwise'):
        a, s = area[v], speed[v]
        result.setdefault('speed_minus_area', {})[v] = {
            'area_pct': 100 * (s['area_um2'] / a['area_um2'] - 1),
            'fmax_pct': 100 * (s['fmax_mhz'] / a['fmax_mhz'] - 1),
            'setup_slack_delta_ps': s['setup_slack_ps'] - a['setup_slack_ps'],
            'power_proxy_pct': 100 * (s['default_activity_power_mw'] / a['default_activity_power_mw'] - 1),
            'wire_pct': 100 * (s['wire_um'] / a['wire_um'] - 1),
        }
    result['frozen_prediction_adjudication'] = {
        'P1_source_timing_improves': speed['source']['setup_slack_ps'] > area['source']['setup_slack_ps'],
        'P2_pairwise_area_smaller_under_speed': speed['pairwise']['area_um2'] < speed['source']['area_um2'],
        'P3_speed_pairwise_closes_2ns': speed['pairwise']['setup_slack_ps'] >= 0 and speed['pairwise']['setup_violations'] == 0,
        'P3_speed_source_closes_2ns': speed['source']['setup_slack_ps'] >= 0 and speed['source']['setup_violations'] == 0,
        'P4_same_clock_intrinsic_service_gain': 1.0,
    }
    for v in ('source', 'pairwise'):
        assert math.isfinite(result['speed_minus_area'][v]['fmax_pct'])
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('area_zip')
    p.add_argument('speed_zip')
    args = p.parse_args()
    print(json.dumps(audit(args.area_zip, args.speed_zip), indent=2, sort_keys=True))
