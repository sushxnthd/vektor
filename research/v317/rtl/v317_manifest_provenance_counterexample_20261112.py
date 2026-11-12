#!/usr/bin/env python3
"""Counterexample: v317_report_evidence_audit accepts fabricated provenance.

This is a negative checker test, NOT a routed physical result. Creates only
synthetic reports/SPEFs in a temporary directory and demonstrates that the
existing screen trusts manifest SHA-256 strings without hashing source files.
"""
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "screen", HERE / "v317_report_evidence_audit_20261112.py")
screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screen)

REPORT = "\n".join((
    "Design area 21314.6 um^2", "setup wns 0.02", "hold wns 0.01",
    "max_cap_violations 0", "max_slew_violations 0", "drc_violations 0"))

def run():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for label in ("baseline", "candidate"):
            (root / (label + ".rpt")).write_text(REPORT)
            (root / (label + ".spef")).write_text("*SPEF \"IEEE 1481-1998\"\n")
        manifest = {"run_id": "synthetic-not-a-route"}
        for label, digit in (("baseline", "a"), ("candidate", "b")):
            manifest[label] = {
                "run_id": manifest["run_id"],
                "report": label + ".rpt",
                "spef": label + ".spef",
                "rtl_sha256": digit * 64,
                "constraints_sha256": "c" * 64,
                "library_sha256": "d" * 64,
            }
        result = screen.audit(manifest, root)
        assert result["both_screen_legal"] is True
        assert result["evidence_tier"].startswith("raw-report-screen-only")
        # The SHA strings do not identify any supplied source, constraints,
        # or library files; the SPEFs contain no parasitic network.
        assert not any(root.glob("*.sv"))
        assert not any(root.glob("*.lib"))
        print(json.dumps({
            "finding": "ACCEPTS_SYNTHETIC_PROVENANCE",
            "screen_legal": result["both_screen_legal"],
            "physical_signoff": False,
            "consequence": "Do not promote raw-report screen to evidence of matched routed legality",
        }, sort_keys=True))

if __name__ == "__main__":
    run()
