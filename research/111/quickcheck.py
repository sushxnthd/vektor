from scoped_validator import Access,validate,conflict
def A(tid=0,cta=0,pc=0,epoch=0,op='S',space='S',addr=4096,size=8):
    return Access(tid,cta,pc,epoch,op,space,addr,size)
a=A(); b=A(tid=32,cta=1,pc=1,op='L')
assert validate([a,b],[[1],[0]])
assert not conflict(a,b)
assert not validate([a,A(tid=32,pc=1,op='L')],[[1],[0]])
assert not validate([a,b],[[0,1]])
assert not validate([a,b],[[0],[1],[1]])
assert not validate([a,b],[[0]])
assert validate([A(space='G'),A(tid=32,pc=1,space='S',op='L')],[[1],[0]])
assert not validate([A(space='G'),A(tid=32,cta=1,pc=1,space='G',op='L')],[[1],[0]])
assert validate([A(op='L',space='G',addr=(1<<64)-16,size=16)],[[0]])
assert not validate([A(op='L',space='G',addr=(1<<64)-15,size=16)],[[0]])
for space in ('G','S','L'):
    for size in (1,2,4,8,16):
        for x in range(48):
            for y in range(48):
                p=A(space=space,addr=x,size=size)
                q=A(tid=32,cta=0,pc=1,op='L',space=space,addr=y,size=size)
                same=space!='L'
                expect=same and bool(set(range(x,x+size))&set(range(y,y+size)))
                assert conflict(p,q)==expect
print('V111 scoped-validator directed and 34560 byte-overlap controls passed')
