#!/usr/bin/env python3
import json,sys
v=json.load(open(sys.argv[1]))
expected={
 'bpf_kernels_full.ptx':(272,564,10,20,0),
 'vector_add.ptx':(6,13,0,1,0)
}
for name,values in expected.items():
 s=v[name]['summary']
 assert tuple(s[k] for k in ('instructions','source_reads','alias_savings','three_source_instructions','three_source_alias_instructions'))==values,(name,s)
assert v['bpf_kernels_full.ptx']['templates']=={'2src_alias':10,'2src_distinct':242,'3src_distinct':20}
assert v['vector_add.ptx']['templates']=={'2src_distinct':5,'3src_distinct':1}
print('PASS pinned PTX corpus identity counts')
