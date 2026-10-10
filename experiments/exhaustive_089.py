"""Bounded exhaustive Vektor-089 action traces."""
from itertools import product
from cancel_aba_089 import TagMachine

def run():
    choices=list(product((False,True),(False,True),(1,3)))
    counts=[0,0,0]
    total=0
    for actions in product(choices,repeat=6):
        ms=[TagMachine(1,3,p) for p in ('unsafe','quarantine','quarantine_boundary')]
        for offer,cancel,delay in actions:
            for m in ms:m.step(offer,cancel,delay)
        total+=1
        for i,m in enumerate(ms):counts[i]+=bool(m.false_accept)
    assert (total,counts)==(262144,[14976,0,0])
    print(total,counts)
if __name__=='__main__':run()
