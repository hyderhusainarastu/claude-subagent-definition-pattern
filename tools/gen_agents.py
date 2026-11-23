#!/usr/bin/env python3
"""Generate agent definition files from one shared preamble.

Agent definition files cannot include other files, so a rule block shared by
several agents has to be copied into each one. This script keeps one source of
truth: write each agent in <src>/<name>.md with a {{PREAMBLE}} marker, put the
shared text in <src>/preamble.md, and generate the final files into <out>.

Usage:
    python3 tools/gen_agents.py [--src DIR] [--out DIR] [--check]

    --src DIR   source directory (default: agent_src)
    --out DIR   output directory (default: .claude/agents)
    --check     write nothing; exit 1 if any generated file is missing or stale
                (use in CI or a pre-commit hook)

Exit codes: 0 up to date (or written), 1 stale under --check or no sources,
2 usage error.
"""

from __future__ import annotations

import sys
from pathlib import Path

MARKER = "{{PREAMBLE}}"


def generate(src: Path, out: Path, check: bool) -> int:
    preamble_file = src / "preamble.md"
    if not preamble_file.is_file():
        print(f"missing {preamble_file}", file=sys.stderr)
        return 1
    preamble = preamble_file.read_text(encoding="utf-8").rstrip("\n")
    sources = sorted(p for p in src.glob("*.md") if p.name != "preamble.md")
    if not sources:
        print(f"no agent sources in {src}", file=sys.stderr)
        return 1

    stale = 0
    if not check:
        out.mkdir(parents=True, exist_ok=True)
    for source in sources:
        text = source.read_text(encoding="utf-8")
        if MARKER not in text:
            print(f"warning: {source} has no {MARKER} marker", file=sys.stderr)
        body = text.replace(MARKER, preamble)
        target = out / source.name
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == body:
            continue
        stale += 1
        if check:
            print(f"STALE {target}")
        else:
            target.write_text(body, encoding="utf-8")
            print(f"wrote {target}")
    return 1 if (check and stale) else 0


def main(argv: list[str]) -> int:
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    src, out, check = Path("agent_src"), Path(".claude/agents"), False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--check":
            check = True
            i += 1
        elif arg in ("--src", "--out") and i + 1 < len(argv):
            if arg == "--src":
                src = Path(argv[i + 1])
            else:
                out = Path(argv[i + 1])
            i += 2
        else:
            print(f"usage error: {arg}", file=sys.stderr)
            return 2
    return generate(src, out, check)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
