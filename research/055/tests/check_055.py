"""Independent Vektor-055 trace checker (no reference model imports)."""
def check(path,dedup):
    slots={};fault=0;completed=0
    for n,line in enumerate(open(path)):
        t=line.split()
        assert len(t)==21,(n,len(t))
        iv,rr,rv,cr,ready,qv,cv,err=[int(t[i]) for i in (1,5,6,11,12,13,17,20)]
        tag,regs,mask,rt,rg,rd,qt,qreg,ct,data=[int(t[i],16) for i in (2,3,4,7,9,10,14,16,18,19)]
        ro,qo=int(t[8]),int(t[15])
        assert err==fault,(n,'error')
        if qv:
            assert qt in slots,(n,'request tag')
            x=slots[qt]
            assert (x[0]>>qo)&1 and x[1][qo]==qreg and qo not in x[2],(n,'request')
            if dedup:assert not any(((x[0]>>j)&1) and x[1][j]==qreg for j in range(qo)),(n,'root')
        if cv:
            assert ct in slots,(n,'completion tag')
            x=slots[ct]
            assert all(not ((x[0]>>j)&1) or j in x[3] for j in range(3)),(n,'complete')
            for j in range(3):
                if (x[0]>>j)&1:assert (data>>(32*j))&0xffffffff==x[3][j],(n,'data')
        if cv and cr:del slots[ct];completed+=1
        if iv and ready:
            assert tag not in slots and len(slots)<2,(n,'issue')
            slots[tag]=(mask,[(regs>>(8*j))&255 for j in range(3)],set(),{})
        if qv and rr:slots[qt][2].add(qo)
        if rv:
            x=slots.get(rt)
            if x is None or ro not in x[2] or ro in x[3] or x[1][ro]!=rg:fault=1
            else:
                indices=[j for j in range(3) if (x[0]>>j)&1 and x[1][j]==rg] if dedup else [ro]
                for j in indices:x[3][j]=rd
    return completed
