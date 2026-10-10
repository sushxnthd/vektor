"""Vektor-089 follow-up: exact callback-first reclamation boundary."""
from cancel_aba_089 import TagMachine
import random
def run():
    total=0;zero_stall=0
    for D in range(2,17):
        for bits in range(1,6):
            for policy in ('quarantine','quarantine_boundary'):
                m=TagMachine(bits,D,policy)
                for _ in range(1024):m.step(True,True,D)
                assert m.false_accept==0
                if policy=='quarantine_boundary' and (1<<bits)>=D:
                    assert m.tag_stalls==0
                    zero_stall+=1
                total+=1
    for seed in range(100,120):
        rng=random.Random(seed)
        models=[TagMachine(4,16,p) for p in ('quarantine','quarantine_boundary')]
        for _ in range(3000):
            offer=rng.random()<.93;cancel=rng.random()<.65;delay=rng.randint(1,16)
            for m in models:m.step(offer,cancel,delay)
        for m in models:assert m.false_accept==0;total+=1
    assert total==190 and zero_stall==41
    print('PASS',total,'boundary cases;',zero_stall,'N>=D no-stall cases')
if __name__=='__main__':run()
