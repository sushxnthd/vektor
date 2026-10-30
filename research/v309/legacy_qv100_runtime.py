#!/usr/bin/env python3
"""V309 frozen complete legacy QV100-SASS runtime gate. Never infers hardware speedup."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

from trace_sim_input_integrity import SHA, URL, commands, path as safe_path

MAX_ARCHIVE = 64 * 1024 * 1024
MAX_EXTRACTED = 96 * 1024 * 1024
STATS = ("gpu_sim_cycle", "gpu_tot_sim_cycle", "gpu_sim_insn",
         "gpu_tot_sim_insn", "gpgpu_n_mem_read_global",
         "gpgpu_n_mem_write_global", "L1D_total_cache_misses",
         "L2_total_cache_misses", "dram_reads")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def select_archive_bytes(data, destination, expected_sha=SHA):
    if len(data) > MAX_ARCHIVE or digest(data) != expected_sha:
        raise ValueError("archive digest or byte cap mismatch")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = {}
        for member in archive:
            name = str(safe_path(member.name))
            if name in members:
                raise ValueError("duplicate archive member")
            if member.islnk() or member.issym():
                continue  # never extract links
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
            directory = PurePosixPath(name).parent
            targets = [str(directory / safe_path(target)) for target in launches]
            if len(set(targets)) != len(targets):
                raise ValueError("duplicate launches")
            if any(t not in members or not t.endswith(".traceg") for t in targets):
                raise ValueError("incomplete exact-local launch linkage")
            total = member.size + sum(members[t].size for t in targets)
            candidates.append((total, name, targets, counts, blob))
        if not candidates:
            raise ValueError("no complete command lists")
        total, name, targets, counts, blob = min(candidates, key=lambda x: (x[0], x[1]))
        if total > MAX_EXTRACTED:
            raise ValueError("selected workload exceeds extraction cap")
        dest = Path(destination)
        dest.mkdir(parents=True, exist_ok=True)
        rows = []
        for source, output_name in [(name, "kernelslist.g")] + [
            (target, PurePosixPath(target).name) for target in targets
        ]:
            content = archive.extractfile(members[source]).read()
            if len(content) != members[source].size:
                raise ValueError("truncated member")
            target_path = dest / output_name
            if target_path.exists():
                raise ValueError("output collision")
            target_path.write_bytes(content)
            rows.append({"archive_path": source, "output": output_name,
                         "bytes": len(content), "sha256": digest(content)})
        manifest = {"status": "SELECTED_INPUT_ONLY", "archive_url": URL,
                    "archive_sha256": expected_sha, "selection_rule":
                    "smallest complete command list by total uncompressed member bytes; lexical tie",
                    "selected_list": name, "selected_bytes": total,
                    "kernel_launches": len(targets),
                    "memcpy_htod": counts["memcpy_htod"],
                    "memcpy_dtoh": counts["memcpy_dtoh"],
                    "memcpy_dtod": counts["memcpy_dtod"],
                    "files": rows, "hardware_validated": False,
                    "architecture_speedup_permitted": False}
        (dest.parent / "selection.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest


def select_archive(filename, destination):
    with open(filename, "rb") as f:
        data = f.read(MAX_ARCHIVE + 1)
    return select_archive_bytes(data, destination)


def parse_stats(log):
    results = {}
    for key in STATS:
        matches = re.findall(r"(?m)^\s*" + re.escape(key) +
                             r"\s*=\s*(\d+)\b", log)
        results[key] = int(matches[-1]) if matches else None
        results[key + "_records"] = len(matches)
    return results


def simulate(binary, trace, gpgpu, trace_config, evidence, manifest):
    out = Path(evidence)
    out.mkdir(parents=True, exist_ok=True)
    paths = [Path(binary), Path(trace), Path(gpgpu), Path(trace_config)]
    if any(not p.is_file() for p in paths):
        raise ValueError("simulator or input/config file missing")
    cmd = [str(paths[0].resolve()), "-trace", str(paths[1].resolve()),
           "-config", str(paths[2].resolve()), "-config", str(paths[3].resolve())]
    runs = []
    for index in (1, 2):
        logfile = out / ("repeat-%d.log" % index)
        timeout = False
        with logfile.open("wb") as log:
            try:
                proc = subprocess.run(cmd, cwd=str(Path(trace).parent),
                                      stdout=log, stderr=subprocess.STDOUT,
                                      timeout=240, check=False)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code, timeout = 124, True
            except OSError as exc:
                code = 127
                log.write(("EXECUTION_ERROR: " + repr(exc) + "\n").encode())
        raw = logfile.read_bytes()
        stats = parse_stats(raw.decode("utf-8", "replace"))
        completed = stats["gpu_sim_cycle_records"]
        good = (code == 0 and not timeout and
                completed >= manifest["kernel_launches"] and
                stats["gpu_tot_sim_cycle"] is not None and
                stats["gpu_tot_sim_cycle"] > 0 and
                stats["gpu_tot_sim_insn"] is not None and
                stats["gpu_tot_sim_insn"] > 0)
        runs.append({"repeat": index, "exit_code": code, "timed_out": timeout,
                     "log_sha256": digest(raw), "log_bytes": len(raw),
                     "kernel_stats_records": completed,
                     "expected_launches": manifest["kernel_launches"],
                     "full_completion_proxy": bool(good),
                     "stats": stats})
    valid = all(r["full_completion_proxy"] for r in runs)
    cycles = [r["stats"]["gpu_tot_sim_cycle"] for r in runs]
    result = {"status": "PASS_RUNTIME" if valid else "FAIL_CLOSED",
              "evidence_tier": "unmodified_QV100_SASS_simulator_runtime_only",
              "command": cmd, "config_sha256": [digest(p.read_bytes()) for p in paths[2:]],
              "simulator_sha256": digest(paths[0].read_bytes()),
              "selected_list": manifest["selected_list"], "runs": runs,
              "cycle_difference": abs(cycles[0] - cycles[1]) if all(
                  c is not None for c in cycles) else None,
              "hardware_counters_matched": False,
              "physical_speedup_permitted": False}
    (out / "runtime-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def selftest():
    sample = ("gpu_sim_cycle = 7\ngpu_sim_insn = 14\n"
              "gpu_tot_sim_cycle = 7\ngpu_tot_sim_insn = 14\n"
              "gpgpu_n_mem_read_global = 4\n")
    a = parse_stats(sample)
    assert a["gpu_tot_sim_cycle"] == 7 and a["gpu_sim_cycle_records"] == 1
    assert a["gpgpu_n_mem_read_global"] == 4 and a["dram_reads"] is None
    assert parse_stats("gpu_tot_sim_cycle = bad")["gpu_tot_sim_cycle"] is None
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as tar:
            for name, payload in [
                ("a/traces/kernelslist.g", b"MemcpyHtoD,0x1,4\nkernel-1.traceg\n"),
                ("a/traces/kernel-1.traceg", b"0 0 0 0 00 ff 1 R1 MOV 0 0\n"),
                ("b/traces/kernelslist.g", b"kernel-2.traceg\n"),
                ("b/traces/kernel-2.traceg", b"x" * 512),
            ]:
                entry = tarfile.TarInfo(name)
                entry.size = len(payload)
                tar.addfile(entry, io.BytesIO(payload))
        data = stream.getvalue()
        d = select_archive_bytes(data, Path(tmp) / "traces", digest(data))
        assert d["selected_list"] == "a/traces/kernelslist.g"
        assert d["kernel_launches"] == 1 and d["memcpy_htod"] == 1
        assert (Path(tmp) / "traces/kernelslist.g").read_bytes().startswith(b"MemcpyHtoD")
        try:
            select_archive_bytes(data, Path(tmp) / "bad", "0" * 64)
        except ValueError:
            pass
        else:
            raise AssertionError("digest drift accepted")
    return {"status": "PASS", "tests": 7}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--select")
    p.add_argument("--destination")
    p.add_argument("--simulate", action="store_true")
    p.add_argument("--binary")
    p.add_argument("--trace")
    p.add_argument("--gpgpu")
    p.add_argument("--trace-config")
    p.add_argument("--evidence")
    p.add_argument("--manifest")
    a = p.parse_args()
    if a.selftest:
        result = selftest()
    elif a.select and a.destination:
        result = select_archive(a.select, a.destination)
    elif a.simulate:
        manifest = json.loads(Path(a.manifest).read_text())
        result = simulate(a.binary, a.trace, a.gpgpu, a.trace_config,
                          a.evidence, manifest)
    else:
        p.error("choose --selftest, --select with --destination, or --simulate")
    print(json.dumps(result, indent=2, sort_keys=True))
    if a.simulate and result["status"] != "PASS_RUNTIME":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
