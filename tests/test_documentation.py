"""Run every fenced Mini example, including optional companion tutorial files."""
import contextlib
import io
import os
from pathlib import Path
import re
import unittest

from src.interpreter import execute, globalEnvironment

ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_mini_fences(self):
        paths = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
        # CI/users can check the companion checkout without a runtime dependency.
        if os.environ.get("MINI_TUTORIAL_DIR"):
            tutorial = Path(os.environ["MINI_TUTORIAL_DIR"])
            self.assertTrue(tutorial.is_dir(), f"Tutorial directory does not exist: {tutorial}")
            paths.extend(sorted(tutorial.rglob("*.md")))
        count = 0
        for path in paths:
            for match in re.finditer(r"^```mini\n(.*?)^```", path.read_text(encoding="utf-8"), re.M | re.S):
                count += 1
                source = match.group(1)
                expected = "".join(line[6:] + "\n" for line in source.splitlines() if line.startswith("// => "))
                with self.subTest(path=str(path), line=match.string[:match.start()].count("\n") + 1):
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        result = execute(io.StringIO(source), globalEnvironment())
                    self.assertIsNotNone(result, output.getvalue())
                    self.assertEqual(output.getvalue(), expected)
        self.assertGreater(count, 0)
