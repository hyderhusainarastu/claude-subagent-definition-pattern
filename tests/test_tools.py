"""Offline tests for tools/check_frontmatter.py and tools/gen_agents.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINT = ROOT / "tools" / "check_frontmatter.py"
GEN = ROOT / "tools" / "gen_agents.py"

GOOD = '---\nname: {name}\ndescription: "Does a specific thing. Use when the task needs that thing done."\nmodel: {model}\n---\n\nBody.\n'


def run(script, *args, cwd=None):
    return subprocess.run(
        [sys.executable, "-I", str(script), *args],
        capture_output=True, text=True, cwd=cwd,
    )


class LintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        p = self.dir / f"{name}.md"
        p.write_text(text, encoding="utf-8")
        return str(p)

    def test_good_file_passes(self):
        p = self.write("alpha", GOOD.format(name="alpha", model="haiku"))
        r = run(LINT, p)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_name_mismatch_fails(self):
        p = self.write("alpha", GOOD.format(name="beta", model="haiku"))
        self.assertEqual(run(LINT, p).returncode, 1)

    def test_unknown_model_fails_by_default_and_passes_with_models_flag(self):
        p = self.write("alpha", GOOD.format(name="alpha", model="small"))
        self.assertEqual(run(LINT, p).returncode, 1)
        self.assertEqual(run(LINT, "--models", "small,large", p).returncode, 0)

    def test_require_flag(self):
        text = '---\nname: alpha\ndescription: "Does a specific thing. Use when the task needs that thing done."\n---\n'
        p = self.write("alpha", text)
        self.assertEqual(run(LINT, "--require", "name,description", p).returncode, 0)
        self.assertEqual(run(LINT, p).returncode, 1)
        self.assertEqual(run(LINT, "--require", "name,description,tools", p).returncode, 1)

    def test_json_output(self):
        good = self.write("alpha", GOOD.format(name="alpha", model="haiku"))
        bad = self.write("beta", "no frontmatter here\n")
        r = run(LINT, "--json", good, bad)
        self.assertEqual(r.returncode, 1)
        doc = json.loads(r.stdout)
        self.assertEqual((doc["checked"], doc["passed"], doc["failed"]), (2, 1, 1))
        self.assertTrue(doc["results"][0]["ok"])
        self.assertFalse(doc["results"][1]["ok"])

    def test_usage_errors_exit_2(self):
        self.assertEqual(run(LINT, "--bogus").returncode, 2)
        self.assertEqual(run(LINT, "--models").returncode, 2)

    def test_repo_agents_pass(self):
        r = run(LINT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class GenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        src = self.dir / "src"
        src.mkdir()
        (src / "preamble.md").write_text("SHARED RULES\n", encoding="utf-8")
        (src / "role.md").write_text("---\nname: role\n---\n\n{{PREAMBLE}}\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def args(self, *extra):
        return ("--src", str(self.dir / "src"), "--out", str(self.dir / "out"), *extra)

    def test_generate_then_check(self):
        self.assertEqual(run(GEN, *self.args("--check")).returncode, 1)  # missing
        self.assertEqual(run(GEN, *self.args()).returncode, 0)
        out = (self.dir / "out" / "role.md").read_text(encoding="utf-8")
        self.assertIn("SHARED RULES", out)
        self.assertNotIn("{{PREAMBLE}}", out)
        self.assertEqual(run(GEN, *self.args("--check")).returncode, 0)

    def test_check_detects_stale(self):
        run(GEN, *self.args())
        (self.dir / "src" / "preamble.md").write_text("CHANGED\n", encoding="utf-8")
        r = run(GEN, *self.args("--check"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("STALE", r.stdout)

    def test_check_writes_nothing(self):
        run(GEN, *self.args("--check"))
        self.assertFalse((self.dir / "out").exists())

    def test_shipped_generated_files_are_current(self):
        r = run(GEN, "--src", str(ROOT / "agent_src"), "--out", str(ROOT / "agents" / "generated"), "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
