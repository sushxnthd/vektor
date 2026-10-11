from pathlib import Path
import subprocess
import sys

def test_vektor109_cohort_conservation():
    script = Path(__file__).resolve().parents[1] / "research/109/quickcheck.py"
    subprocess.run([sys.executable, str(script)], check=True)
