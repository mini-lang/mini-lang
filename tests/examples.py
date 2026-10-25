from pathlib import Path
import subprocess
import sys

from tests.util import done

ROOT = Path(__file__).resolve().parents[1]


def run_file(file: Path) -> bool:
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "mini.py"), str(file)], cwd=ROOT,
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
