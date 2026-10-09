#!/usr/bin/env python3
"""Static PTX virtual-register identity audit; not SASS or dynamic tracing."""
import re,json,argparse
from collections import Counter,defaultdict
from pathlib import Path
OPS=set('add sub mul mad fma max min and or xor shl shr div rem selp setp set lop3 prmt'.split())
INST=re.compile(r'^\s*(?:@!?%[\w.]+\s+)?([a-z][a-z0-9]*)(?:\.[a-z0-9_.]+)?\s+(.+?)\s*;')
REG=re.compile(r'%[A-Za-z_][\w.]*')
ENTRY=re.compile(r'\.entry\s+([A-Za-z_]\w*)\s*\(')
def analyze(text):
    text=re.sub(r'/\*[\s\S]*?\*/','',text);kernel='outside'
    summary=Counter();templates=Counter();per=defaultdict(Counter)
    for raw in text.splitlines():
        line=raw.split('//',1)[0];e=ENTRY.search(line)
        if e:kernel=e.group(1)
        m=INST.match(line)
        if not m or m.group(1) not in OPS:continue
        a=[x.strip() for x in m.group(2).split(',')]
        if len(a)<3:continue
        src=[z[0] for x in a[1:] if len(z:=REG.findall(x))==1]
        if len(src)<2:continue
        alias=len(src)-len(set(src))
        for c in (summary,per[kernel]):
            c['instructions']+=1;c['source_reads']+=len(src);c['alias_savings']+=alias
            c['alias_instructions']+=int(alias>0)
            c['three_source_instructions']+=int(len(src)==3)
            c['three_source_alias_instructions']+=int(len(src)==3 and alias>0)
        templates[f'{len(src)}src_{"alias" if alias else "distinct"}']+=1
    return dict(summary=dict(summary),templates=dict(templates),per_kernel={k:dict(v) for k,v in per.items()})
def test():
    s='''// add.f32 %z, %a, %a;
.visible .entry demo(
) {
 fma.rn.f32 %d, %a, %b, %c;
 mul.f32 %z, %a, %a;
 add.f32 %x, %a, 1;
 @%p add.f32 %y, %a, %b;
 fma.rn.f32 %t, %a, 0f3f800000, %b;
}'''
    a=analyze(s)
    assert a['summary']['instructions']==4 and a['summary']['source_reads']==9
    assert a['summary']['alias_savings']==1
    print('PASS parser unit test')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('paths',nargs='*');p.add_argument('--output');p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    if args.self_test:test()
    out={Path(x).name:analyze(Path(x).read_text()) for x in args.paths}
    if args.output:Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    if out:print(json.dumps({k:v['summary'] for k,v in out.items()},indent=2))
