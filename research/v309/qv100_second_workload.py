#!/usr/bin/env python3
"""V309 prospective second QV100 workload selection. Source identity only, not performance."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
from legacy_qv100_runtime import MAX_ARCHIVE, MAX_EXTRACTED
from trace_sim_input_integrity import SHA, URL, commands, path as safe_path

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def select_second(data, destination, expected_sha=SHA):
    """Select rank 2 by compressed-independent uncompressed bytes; fail closed."""
    if len(data) > MAX_ARCHIVE or digest(data) != expected_sha:
        raise ValueError("original archive SHA-256 or size cap mismatch")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = {}
        for member in archive:
            name = str(safe_path(member.name))
            if name in members:
                raise ValueError("duplicate archive member")
            if member.islnk() or member.issym():
                continue
            if member.isdev() or member.isfifo():
                raise ValueError("unsafe archive member")
            if member.isfile():
                members[name] = member
        candidates = []
        for name, member in members.items():
            if PurePosixPath(name).name != "kernelslist.g":
                continue
            if member.size > 1024 * 1024:
                raise ValueError("oversize command list")
            blob = archive.extractfile(member).read()
            launches, counts = commands(blob)
            if not launches or counts["other_commands"]:
                raise ValueError("invalid command list")
            parent = PurePosixPath(name).parent
            targets = [str(parent / safe_path(t)) for t in launches]
            if len(set(targets)) != len(targets):
                raise ValueError("duplicate launch trace references")
            if any(t not in members or not t.endswith(".traceg") for t in targets):
                raise ValueError("incomplete local trace linkage")
            total = member.size + sum(members[t].size for t in targets)
            candidates.append((total, name, targets, counts))
        candidates.sort(key=lambda r: (r[0], r[1]))
        if len(candidates) < 2:
            raise ValueError("no second complete workload")
        total, name, targets, counts = candidates[1]
        if total > MAX_EXTRACTED:
            raise ValueError("second workload exceeds extraction cap")
        out = Path(destination)
        out.mkdir(parents=True, exist_ok=True)
        sources = [(name, "kernelslist.g")] + [(t, PurePosixPath(t).name) for t in targets]
        if len({target for _, target in sources}) != len(sources):
            raise ValueError("output basename collision")
        if any((out / target).exists() for _, target in sources):
            raise ValueError("refusing to overwrite evidence")
        rows = []
        for source, target in sources:
            data_part = archive.extractfile(members[source]).read()
            if len(data_part) != members[source].size:
                raise ValueError("truncated trace member")
            (out / target).write_bytes(data_part)
            rows.append({"archive_path": source, "output": target,
                         "bytes": len(data_part), "sha256": digest(data_part)})
        manifest = {
            "status": "SECOND_WORKLOAD_SELECTED_INPUT_ONLY",
            "archive_url": URL, "archive_sha256": expected_sha,
            "selection_rule": "rank 2 of complete command lists by uncompressed bytes, lexical tie",
            "selection_rank_one_based": 2, "complete_candidate_count": len(candidates),
            "first_workload_list": candidates[0][1], "selected_list": name,
            "selected_bytes": total, "kernel_launches": len(targets),
            "memcpy_htod": counts["memcpy_htod"],
            "memcpy_dtoh": counts["memcpy_dtoh"],
            "memcpy_dtod": counts["memcpy_dtod"],
            "files": rows, "hardware_validated": False,
            "architecture_speedup_permitted": False
        }
        (out.parent / "selection.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
        return manifest

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for name, blob in [
                ("a/kernelslist.g", b"kernel-1.traceg\n"),
                ("a/kernel-1.traceg", b"a"),
                ("b/kernelslist.g", b"MemcpyHtoD,0x1,4\nkernel-2.traceg\n"),
                ("b/kernel-2.traceg", b"b" * 100),
                ("c/kernelslist.g", b"kernel-3.traceg\n"),
                ("c/kernel-3.traceg", b"c" * 1000)
            ]:
                m = tarfile.TarInfo(name)
                m.size = len(blob)
                archive.addfile(m, io.BytesIO(blob))
        blob = buffer.getvalue()
        selection = select_second(blob, Path(tmp)/"second/traces", digest(blob))
        assert selection["selected_list"] == "b/kernelslist.g"
        assert selection["first_workload_list"] == "a/kernelslist.g"
        assert selection["kernel_launches"] == 1 and selection["memcpy_htod"] == 1
        assert (Path(tmp)/"second/traces/kernel-2.traceg").read_bytes() == b"b"*100
        for corrupt, dest, sha in [
            (blob, Path(tmp)/"wrong", "0"*64),
            (blob, Path(tmp)/"second/traces", digest(blob))
        ]:
            try:
                select_second(corrupt, dest, sha)
            except ValueError:
                pass
            else:
                raise AssertionError("unsafe or drifted input accepted")
        one = io.BytesIO()
        with tarfile.open(fileobj=one, mode="w:gz") as archive:
            for name, payload in [("only/kernelslist.g",b"kernel.traceg\n"),("only/kernel.traceg",b"x")]:
                m=tarfile.TarInfo(name); m.size=len(payload); archive.addfile(m,io.BytesIO(payload))
        try:
            select_second(one.getvalue(), Path(tmp)/"one", digest(one.getvalue()))
        except ValueError:
            pass
        else:
            raise AssertionError("missing second candidate accepted")
    return {"status":"PASS", "positive_controls":4, "negative_controls":3}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--archive")
    p.add_argument("--destination")
    args=p.parse_args()
    if args.selftest:
        result=selftest()
    elif args.archive and args.destination:
        with open(args.archive,"rb") as f:
            blob=f.read(MAX_ARCHIVE+1)
        result=select_second(blob,args.destination)
    else:
        p.error("choose --selftest or --archive with --destination")
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__=="__main__":
    main()
