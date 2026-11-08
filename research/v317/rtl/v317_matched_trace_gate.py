#!/usr/bin/env python3
"""Independent matched-resource service-trace gate; NOT RTL/STA evidence.

CSV columns: cycle,request_id,bank,operand,complete,retained_words.
One row per granted operand; complete=1 on at most one row/request/cycle.
retained_words is sampled post-cycle occupancy, repeated across cycle rows.
An idle cycle may use request_id=-1,bank=-1,operand=-1.
"""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path

def audit(path, *, period_ns, bank_ports, return_ports, word_budget, max_cycles, retention_mode='bypass'):
    if min(period_ns,bank_ports,return_ports,max_cycles) <= 0 or word_budget < 0:
        raise ValueError('invalid physical budget')
    if retention_mode not in ('bypass','registered'): raise ValueError('unknown retention mode')
    by_cycle = defaultdict(list)
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            r = {k:int(row[k]) for k in ('cycle','request_id','bank','operand','complete','retained_words')}
            if r['cycle'] < 0 or r['cycle'] >= max_cycles: raise ValueError('cycle outside fixed horizon')
            by_cycle[r['cycle']].append(r)
    acquired, completed = defaultdict(set), set()
    peak = 0
    for cycle in range(max_cycles):
        rows = by_cycle[cycle]
        occupancy = {r['retained_words'] for r in rows}
        if len(occupancy)>1: raise ValueError('inconsistent retention sample')
        grants = defaultdict(int)
        retire = set()
        for r in rows:
            rid,bank,op = r['request_id'],r['bank'],r['operand']
            if rid == -1:
                if (bank,op,r['complete']) != (-1,-1,0): raise ValueError('bad idle row')
                continue
            if rid < 0 or bank < 0 or op not in (0,1): raise ValueError('bad grant')
            if rid in completed or op in acquired[rid]: raise ValueError('duplicate operand/retired request')
            acquired[rid].add(op)
            grants[bank]+=1
            if r['complete']:
                if rid in retire: raise ValueError('duplicate completion')
                retire.add(rid)
        # Completion is a cycle-level event, independent of CSV row ordering.
        if any(acquired[rid] != {0,1} for rid in retire):
            raise ValueError('premature completion')
        if any(n>bank_ports for n in grants.values()): raise ValueError('bank port exceeded')
        if len(retire)>return_ports: raise ValueError('return port exceeded')
        # Registered retention must hold every acquired word until the cycle's
        # retirement edge; combinational bypass may retire without registering.
        pre_retire = sum(len(ops) for rid,ops in acquired.items() if rid not in completed)
        if retention_mode == 'registered' and pre_retire > word_budget:
            raise ValueError('registered pre-retirement word budget exceeded')
        completed.update(retire)
        live = sum(len(ops) for rid,ops in acquired.items() if rid not in completed)
        if live>word_budget: raise ValueError('physical word budget exceeded')
        if rows and occupancy != {live}: raise ValueError('reported retention disagrees with replay')
        peak=max(peak,live)
    return {'completed':len(completed),'horizon_ns':max_cycles*period_ns,
            'throughput_per_ns':len(completed)/(max_cycles*period_ns),
            'peak_retained_words':peak,'retention_mode':retention_mode,'bank_ports':bank_ports,'return_ports':return_ports}

def compare(base, candidate):
    if (base['bank_ports'],base['return_ports']) != (candidate['bank_ports'],candidate['return_ports']):
        raise ValueError('unmatched port resources')
    return {'ratio':candidate['throughput_per_ns']/base['throughput_per_ns'] if base['throughput_per_ns'] else None,
            'baseline':base,'candidate':candidate}

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'trace.csv'
        p.write_text('cycle,request_id,bank,operand,complete,retained_words\n0,0,0,0,0,1\n1,0,1,1,1,0\n')
        b=audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=1,max_cycles=2)
        c=audit(p,period_ns=4,bank_ports=1,return_ports=1,word_budget=1,max_cycles=2)
        assert abs(compare(b,c)['ratio']-0.75)<1e-12
        try: audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=0,max_cycles=2)
        except ValueError: pass
        else: raise AssertionError('failed to reject unbudgeted storage')
        p.write_text('cycle,request_id,bank,operand,complete,retained_words\n0,0,0,0,0,1\n0,1,0,0,0,2\n')
        try: audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=2,max_cycles=2)
        except ValueError: pass
        else: raise AssertionError('failed to reject overbooked bank')
        for lines in (
            '0,0,0,0,1,0\n0,0,1,1,0,0\n',
            '0,0,1,1,0,0\n0,0,0,0,1,0\n',
        ):
            p.write_text('cycle,request_id,bank,operand,complete,retained_words\n'+lines)
            assert audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=0,max_cycles=1)['completed']==1
        p.write_text('cycle,request_id,bank,operand,complete,retained_words\n0,0,0,0,1,1\n')
        try: audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=1,max_cycles=1)
        except ValueError: pass
        else: raise AssertionError('failed to reject incomplete request')
        # Identical completed trace is feasible with zero registered words
        # only when a timing-validated combinational bypass is assumed.
        p.write_text('cycle,request_id,bank,operand,complete,retained_words\n0,0,0,0,0,0\n0,0,1,1,1,0\n')
        audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=0,max_cycles=1,retention_mode='bypass')
        try: audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=0,max_cycles=1,retention_mode='registered')
        except ValueError: pass
        else: raise AssertionError('registered path silently borrowed unbudgeted bypass')
        audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=2,max_cycles=1,retention_mode='registered')
    print('PASS: wall-clock, word budget, bank ports, row-order invariance, incomplete completion')

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline'); ap.add_argument('--candidate')
    ap.add_argument('--baseline-period-ns',type=float,default=3)
    ap.add_argument('--candidate-period-ns',type=float,default=3)
    ap.add_argument('--bank-ports',type=int,default=2)
    ap.add_argument('--return-ports',type=int,default=2)
    ap.add_argument('--word-budget',type=int,default=4)
    ap.add_argument('--retention-mode',choices=('bypass','registered'),default='registered',help='registered charges pre-retirement operand words; bypass requires independent path timing proof')
    ap.add_argument('--cycles',type=int,default=1000)
    a=ap.parse_args()
    selftest()
    if a.baseline and a.candidate:
        kwargs=dict(bank_ports=a.bank_ports,return_ports=a.return_ports,word_budget=a.word_budget,max_cycles=a.cycles,retention_mode=a.retention_mode)
        b=audit(a.baseline,period_ns=a.baseline_period_ns,**kwargs)
        c=audit(a.candidate,period_ns=a.candidate_period_ns,**kwargs)
        print(json.dumps(compare(b,c),indent=2))
    elif a.baseline or a.candidate: ap.error('both traces required')
