from pathlib import Path
import subprocess
import sys

from tests.util import done

ROOT = Path(__file__).resolve().parents[1]


def run_file(file: Path) -> bool:
    # Use the embedding API until the CLI itself propagates errors (v1 phase 3).
    script = """
import sys
from src.interpreter import execute, globalEnvironment
with open(sys.argv[1], encoding='utf-8') as source:
    result = execute(source, globalEnvironment())
sys.exit(1 if result is None else 0)
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script, str(file)], cwd=ROOT,
            input="24\n", capture_output=True, text=True, encoding="utf-8", timeout=5,
        )
    except subprocess.TimeoutExpired:
        print(f"Timed out: {file.name}")
        return False
    if result.returncode != 0 or result.stderr:
        print(result.stdout + result.stderr)
        return False
    if file.name == "input.m" and result.stdout != "Calculate 12 * 2: true\n":
        print(result.stdout)
        return False
    return True


def run_all() -> bool:
    print("\nRunning examples tests:")
    passed = True
    for file in sorted((ROOT / "examples").glob("*.m")):
        print(f"- examples/{file.name}")
        passed &= run_file(file)
    return passed


if __name__ == "__main__":
    done(run_all())
