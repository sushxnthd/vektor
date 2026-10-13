"""Exact integer IEEE-754 binary32 FMA oracle, round-to-nearest-even.
Canonical NaNs; flags {NV,DZ,OF,UF,NX}, tininess after rounding.
Adapted from independently checked V138 oracle (34,000 glibc fmaf cases).
"""
def decode(x):
    sign=x>>31; exp=(x>>23)&255; frac=x&0x7fffff
    nan=exp==255 and frac!=0
    return sign,nan,nan and not (frac&0x400000),exp==255 and not frac,exp==0 and not frac,(frac if exp==0 else frac|0x800000),(-149 if exp==0 else exp-150)

def rne(mag,shift):
    if shift<=0:return mag<<-shift,False
    whole,rem=divmod(mag,1<<shift)
    half=1<<(shift-1)
    return whole+int(rem>half or (rem==half and bool(whole&1))),bool(rem)

def fma_bits(a,b,c):
    sa,na,sna,ia,za,ma,qa=decode(a)
    sb,nb,snb,ib,zb,mb,qb=decode(b)
    sc,nc,snc,ic,zc,mc,qc=decode(c)
    sp=sa^sb
    invalid=sna or snb or snc or ((ia or ib) and (za or zb)) or ((ia or ib) and ic and sp!=sc)
    if na or nb or nc or invalid:return 0x7fc00000,16 if invalid else 0
    if ia or ib:return (sp<<31)|0x7f800000,0
    if ic:return (sc<<31)|0x7f800000,0
    prod=(ma*mb)<<(qa+qb+298)
    add=mc<<(qc+298)
    exact=(-prod if sp else prod)+(-add if sc else add)
    if exact==0:
        sign=sp if prod==0 and add==0 and sp==sc else 0
        return sign<<31,0
    sign=int(exact<0);mag=abs(exact)
    highest=mag.bit_length()-1;e=highest-298
    if e>=-126:
        mant,nx=rne(mag,highest-23)
        if mant==1<<24:mant>>=1;e+=1
        if e>127:return (sign<<31)|0x7f800000,5
        return (sign<<31)|((e+127)<<23)|(mant&0x7fffff),int(nx)
    mant,nx=rne(mag,149)
    if mant>=1<<23:return (sign<<31)|0x00800000,int(nx)
    return (sign<<31)|mant,3 if nx else 0
