"""Independent V301 cycle oracle and deterministic clocked RTL vectors.

Uses a Python record list, not the RTL's parallel register arrays. Compares
ready/admission, oldest-first retirement, epoch-safe OR and conservation.
This is NOT an end-to-end GPU throughput model.
"""
import argparse
import random
from pathlib import Path


def step(queue, events, full_cam):
    q = list(queue)
    out = q.pop(0) if q else None
    ready = []
    blocked = False
    for ev in events:
        if ev is None:
            ready.append(1)
            continue
        if blocked:
            ready.append(0)
            continue
        w, epoch, mask = ev
        matches = [i for i, (qw, qe, _) in enumerate(q) if qw == w and qe == epoch]
        if matches:
            i = matches[0]
            old = q[i]
            q[i] = (old[0], old[1], old[2] | mask)
            ready.append(1)
        elif len(q) < 8 and (full_cam or sum(qw % 2 == w % 2 for qw, _, _ in q) < 4):
            q.append(ev)
            ready.append(1)
        else:
            ready.append(0)
            blocked = True
    return q, ready, out


def encode_stim(events):
    val = 0
    for lane, ev in enumerate(events):
        if ev is not None:
            w, e, mask = ev
            val |= 1 << lane
            val |= w << (4 + lane * 6)
            val |= e << (28 + lane * 8)
            val |= mask << (60 + lane * 8)
    return val


def encode_expect(ready, out):
    val = sum(int(bit) << i for i, bit in enumerate(ready))
    if out is not None:
        w, epoch, mask = out
        val |= 1 << 4
        val |= w << 5
        val |= epoch << 11
        val |= mask << 19
    return val


def stimuli(seed=301, cycles=1024):
    rng = random.Random(seed)
    for t in range(cycles):
        if t < 80:
            hot = .75
        elif t < 160:
            hot = 0.
        elif t < 240:
            hot = .97
        else:
            hot = [.1, .4, .8, 0.][(t // 67) % 4]
        row = []
        for lane in range(4):
            if rng.random() < (.95 if t < 240 else .68):
                warp = 0 if rng.random() < hot else rng.randrange(64)
                epoch = (t // 17) % 256
                if t % 47 == 0:
                    epoch = (epoch + lane) % 256
                row.append((warp, epoch, 1 << rng.randrange(8)))
            else:
                row.append(None)
        yield row


def write_vectors(folder, full_cam, seed=301, cycles=1024):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    q = []
    stim, expected = [], []
    accepted = {}
    emitted = {}
    for row in stimuli(seed, cycles):
        nextq, ready, out = step(q, row, full_cam)
        for ev, ok in zip(row, ready):
            if ev is not None and ok:
                k = ev[:2]
                accepted[k] = accepted.get(k, 0) | ev[2]
        if out is not None:
            k = out[:2]
            emitted[k] = emitted.get(k, 0) | out[2]
        stim.append(f"{encode_stim(row):023x}")
        expected.append(f"{encode_expect(ready, out):07x}")
        q = nextq
    for w, e, mask in q:
        emitted[(w, e)] = emitted.get((w, e), 0) | mask
    assert accepted == emitted, (full_cam, len(accepted), len(emitted))
    suffix = 'cam' if full_cam else 'set4'
    (folder / f'stim_{suffix}.hex').write_text('\n'.join(stim)+'\n')
    (folder / f'exp_{suffix}.hex').write_text('\n'.join(expected)+'\n')
    return len(stim)


def selftest():
    assert step([], [(0,1,1),(0,1,2),None,None], True)[0] == [(0,1,3)]
    assert step([(0,1,1)], [(0,2,2),None,None,None], True)[2] == (0,1,1)
    q = [(1,0,1)] + [(2*i,0,1) for i in range(4)]
    _, ready, _ = step(q, [(8,0,2),(1,0,4),None,None], False)
    assert ready == [0,0,1,1], ready
    assert len(step([], [(0,1,1),(0,2,2),None,None], True)[0]) == 2
    print('V301 independent oracle microtests passed')


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output', default='research/v301/rtl_vectors')
    p.add_argument('--cycles', type=int, default=1024)
    args=p.parse_args()
    selftest()
    for cam in (True,False):
        print(('CAM' if cam else 'set4'),write_vectors(args.output,cam,cycles=args.cycles),'cycles verified for conservation')
