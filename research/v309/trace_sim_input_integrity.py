#!/usr/bin/env python3
"""Bounded Accel-Sim kernelslist.g -> .traceg integrity audit. No cycle claims."""
import argparse, collections, hashlib, io, json, re, tarfile
from pathlib import PurePosixPath as P
SHA = "aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1"
URL = "https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz"
ROW = re.compile(r"^\d+\s+\d+\s+\d+\s+\d+\s+[0-9a-fA-F]+\s+[0-9a-fA-F]+\s+\d+\s+")

def path(s):
    p = P(s)
    if not s or p.is_absolute() or ".." in p.parts or "\\" in s or "\x00" in s:
        raise ValueError("unsafe path")
    return p

def commands(blob):
    try: lines = blob.decode("utf-8").splitlines()
    except UnicodeDecodeError as e: raise ValueError("non-UTF8 list") from e
    launches, counts = [], collections.Counter()
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"): continue
        if s.endswith(".traceg"):
            if "," in s or any(c.isspace() for c in s): raise ValueError("invalid launch")
            path(s); launches.append(s); counts["launches"] += 1
        elif ".traceg" in s: raise ValueError("malformed launch")
        elif s.startswith("MemcpyHtoD,"): counts["memcpy_htod"] += 1
        elif s.startswith("MemcpyDtoH,"): counts["memcpy_dtoh"] += 1
        elif s.startswith("MemcpyDtoD,"): counts["memcpy_dtod"] += 1
        else: counts["other_commands"] += 1
    return launches, counts

def evaluate(traces, lists, prefixes, links=0):
    c = collections.Counter(trace_members=len(traces), command_lists=len(lists), tar_links_skipped=links)
    basenames = collections.defaultdict(list)
    for t in traces: basenames[P(t).name].append(t)
    referenced, examples = set(), collections.defaultdict(list)
    for name, blob in sorted(lists.items()):
        launches, cnt = commands(blob); c.update(cnt); seen = set()
        for target in launches:
            local = str(P(name).parent / path(target))
            if local in traces: resolved, status = local, "exact_local"
            else:
                matches = basenames[P(target).name]
                resolved = matches[0] if len(matches) == 1 else None
                status = "weak_fallback" if len(matches) == 1 else ("missing" if not matches else "ambiguous")
            c[status] += 1
            if status != "exact_local" and len(examples[status]) < 8:
                examples[status].append([name, target, resolved])
            if resolved:
                if resolved in seen: c["duplicate_launch"] += 1
                seen.add(resolved); referenced.add(resolved)
    missing = sorted(traces - referenced)
    c["unreferenced_traces"] = len(missing)
    c["referenced_unique_traces"] = len(referenced)
    c["prefixes_with_rows"] = sum(any(ROW.match(x.strip()) for x in b.decode("utf-8","replace").splitlines()) for b in prefixes.values())
    strict = bool(lists and c["launches"] and c["exact_local"] == c["launches"] and
                  not c["duplicate_launch"] and not missing and not c["other_commands"])
    return dict(status="PASS_AUDIT", strict_local_linkage=strict, counts=dict(c),
                examples={**dict(examples), "unreferenced":missing[:8]},
                evidence_tier="trace_input_linkage_only_NOT_cycle_simulation",
                simulator_runtime_verified=False, hardware_counters_matched=False,
                physical_speedup_permitted=False)

def scan(filename):
    with open(filename,"rb") as f: data = f.read(64*1024*1024+1)
    if len(data) > 64*1024*1024 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError("source digest or byte cap mismatch")
    traces, lists, prefixes, links = set(), {}, {}, 0
    with tarfile.open(fileobj=io.BytesIO(data),mode="r:gz") as tf:
        for i, m in enumerate(tf):
            if i >= 200000: raise ValueError("member cap")
            name = str(path(m.name))
            if m.isdev(): raise ValueError("device member")
            if m.issym() or m.islnk(): links += 1; continue
            if not m.isfile(): continue
            if name.endswith(".traceg"):
                if name in traces: raise ValueError("duplicate trace")
                traces.add(name); prefixes[name] = tf.extractfile(m).read(4096)
            elif P(name).name == "kernelslist.g":
                if name in lists or m.size > 1024*1024: raise ValueError("duplicate/large list")
                lists[name] = tf.extractfile(m).read(1024*1024+1)
    result = evaluate(traces,lists,prefixes,links)
    result.update(archive_sha256=SHA, archive_bytes=len(data), source=URL)
    return result

def selftest():
    d="a/backprop-rodinia-2.0-ft/traces/"
    traces={d+"kernel-1.traceg",d+"kernel-2.traceg"}
    lst={d+"kernelslist.g":b"MemcpyHtoD,0x1000,4\nkernel-1.traceg\nkernel-2.traceg\n"}
    ok=evaluate(traces,lst,{t:b"0 0 0 0 0000 ffffffff 1 R1 MOV 0 0\n" for t in traces})
    assert ok["strict_local_linkage"] and ok["counts"]["exact_local"]==2
    negatives=[
        (traces,{d+"kernelslist.g":b"kernel-1.traceg\nkernel-99.traceg\n"}),
        (traces,{d+"kernelslist.g":b"kernel-1.traceg\nkernel-1.traceg\n"}),
        (traces|{"b/kernel-3.traceg"},lst),
        ({"a/kernel-1.traceg","b/kernel-1.traceg"},{"c/kernelslist.g":b"kernel-1.traceg\n"}),
        ({"a/kernel-1.traceg"},{"c/kernelslist.g":b"kernel-1.traceg\n"})]
    for ts,ls in negatives: assert not evaluate(ts,ls,{})["strict_local_linkage"]
    for blob in (b"../kernel-1.traceg\n",b"\xff\n",b"kernel-1.traceg extra\n"):
        try: commands(blob)
        except ValueError: pass
        else: raise AssertionError("accepted bad command")
    for s in ("../x.traceg","/x.traceg","x\\y.traceg"):
        try: path(s)
        except ValueError: pass
        else: raise AssertionError("accepted unsafe path")
    return dict(status="PASS", valid_fixture=1, negative_controls=11)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("archive",nargs="?");p.add_argument("--selftest",action="store_true")
    a=p.parse_args()
    if not a.selftest and not a.archive: p.error("archive required")
    print(json.dumps(selftest() if a.selftest else scan(a.archive),indent=2,sort_keys=True))
