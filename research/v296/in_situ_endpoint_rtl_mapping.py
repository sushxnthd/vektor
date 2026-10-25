#!/usr/bin/env python3
"""Map original SHA-verified extracted path endpoints to mapped RTL netlist pins.

Never changes original hardware or relabels synthesized cells as RTL causality.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile
from in_situ_path_artifact_recovery import analyze_one


def cell(verilog, instance):
    pattern = r'(?m)^\s*(DFF\w*_X\d+)\s+' + re.escape(instance) + r'\s*\((.*?)\);'
    hits = re.findall(pattern, verilog, re.S)
    if len(hits) != 1:
        raise ValueError('Missing/ambiguous mapped flop: '+instance)
    typ, body = hits[0]
    pins = dict(re.findall(r'\.(\w+)\((.*?)\)', body, re.S))
    if not {'CK','D','Q'}.issubset(pins):
        raise ValueError('Flop pin mapping incomplete')
    return {'cell_type':typ,'instance':instance,
            'Q':pins['Q'].strip(),'D':pins['D'].strip(),
            'CK':pins['CK'].strip()}


def mapped(path, variant):
    forensic = analyze_one(path,variant)
    with ZipFile(path) as z:
        verilog=z.read(variant+'.v').decode()
    result={}
    for kind in ('setup','hold'):
        record=forensic[kind]['critical_paths'][0]
        start=record['start'].split(' (')[0]
        end=record['end'].split(' (')[0]
        result[kind]={'start': start if kind=='hold' else cell(verilog,start),
                      'end':cell(verilog,end),
                      'extracted_slack_ns':record['slack_ns']}
    if '.scheduler.rr1' not in result['setup']['start']['Q']:
        raise ValueError('Unexpected setup startpoint RTL net')
    if not result['setup']['end']['Q'].startswith('executed_data['):
        raise ValueError('Unexpected setup endpoint RTL net')
    if not result['hold']['start'].startswith('rf_write_data['):
        raise ValueError('Unexpected hold startpoint input')
    if not result['hold']['end']['Q'].startswith('\\rf['):
        raise ValueError('Unexpected hold endpoint RF register')
    return result


def self_test():
    text='''DFFR_X1 _42_ (\n .CK(clk),\n .D(net),\n .Q(\\candidate.issue.scheduler.rr1 [2]),\n .QN(nq),\n .RN(rst_n)\n);'''
    assert cell(text,'_42_')['Q']=='\\candidate.issue.scheduler.rr1 [2]'
    for bad in [text.replace(' .Q(', ' .Z('),text+ '\n'+text]:
        try: cell(bad,'_42_')
        except ValueError: pass
        else: raise AssertionError('Bad mapped cell accepted')
    print('V296_ENDPOINT_NETLIST_MAPPING_SELFTEST_PASS')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pairwise-zip',type=Path)
    p.add_argument('--serial-zip',type=Path)
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test: self_test()
    if a.pairwise_zip or a.serial_zip:
        if not a.pairwise_zip or not a.serial_zip:
            p.error('both immutable ZIPs required')
        print(json.dumps({'evidence':'PINNED_EXTRACTED_PATH_AND_MAPPED_NETLIST_ASSOCIATION',
                          'not_proof_of_unique_critical_logic_cause':True,
                          'rows':{'pairwise':mapped(a.pairwise_zip,'pairwise'),
                                  'serial_onehot':mapped(a.serial_zip,'serial_onehot')}},
                         indent=2,sort_keys=True))
    if not a.self_test and not a.pairwise_zip:
        p.error('choose --self-test or paired ZIPs')

if __name__=='__main__': main()
