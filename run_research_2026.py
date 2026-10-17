"""Reproduce supplementary 2026 tracking offline from the repository caches."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-text", action="store_true",
                        help="Also replay the historical SVD-space text-allocation experiment (not used in the report).")
    args = parser.parse_args()
    # Refresh estimation inputs before using the frozen 2025 weights.
    subprocess.run([sys.executable, str(ROOT / "run_all.py"), "--stage1"], cwd=ROOT, check=True)
    scripts = ["backtest_2026.py", "ledoit_wolf/compare.py"]
    if args.include_text:
        scripts.append("text_weight/compare.py")
    for script in scripts:
        subprocess.run([sys.executable, str(ROOT / "research_2026" / script)], cwd=ROOT, check=True)
    validation = [sys.executable, str(ROOT / "research_2026/validate.py")]
    if args.include_text:
        validation.append("--include-text")
    subprocess.run(validation, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
