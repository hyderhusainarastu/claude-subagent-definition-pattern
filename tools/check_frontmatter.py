#!/usr/bin/env python3
"""Validate the YAML frontmatter of subagent definition files.

Usage:
    python3 tools/check_frontmatter.py [options] [path ...]

With no paths, checks every *.md file under ./agents that is not a README.

Options:
    --models LIST    comma-separated allowed values for 'model'
                     (default: haiku,sonnet,opus)
    --require LIST   comma-separated required fields
                     (default: name,description,model)
    --json           print one JSON document instead of text lines
    -h, --help       show this help

Checks:
  - the file opens with a '---' fence and has a closing '---'
  - the frontmatter block parses (PyYAML if installed, otherwise a flat
    key: value reader, which is all this frontmatter shape needs)
  - every --require field is present and non-empty
  - 'name' matches the filename stem and is a lowercase slug
  - 'model' (when present) is one of --models
  - 'description' is a single line and non-trivial in length

Exit codes: 0 all files pass, 1 at least one file fails (or no files),
2 usage error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DEFAULT_MODELS = ("haiku", "sonnet", "opus")
DEFAULT_REQUIRED = ("name", "description", "model")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Return the frontmatter mapping, or raise ValueError."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file does not open with a '---' frontmatter fence")
    try:
        end = next(i for i, ln in enumerate(lines[1:], start=1) if ln.strip() == "---")
    except StopIteration:
        raise ValueError("frontmatter fence is never closed") from None
    block = "\n".join(lines[1:end])
    if not block.strip():
        raise ValueError("frontmatter block is empty")

    try:
        import yaml  # type: ignore
    except ImportError:
        pass
    else:
        data = yaml.safe_load(block)
        if not isinstance(data, dict):
            raise ValueError("frontmatter does not parse to a mapping")
        return {str(k): str(v) for k, v in data.items()}

    # Fallback: flat "key: value" reader.
    data: dict[str, str] = {}
    for lineno, raw in enumerate(block.splitlines(), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1].isspace():
            raise ValueError(f"line {lineno}: unexpected indentation (expected flat keys)")
        if ":" not in raw:
            raise ValueError(f"line {lineno}: not a 'key: value' pair")
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if not key:
            raise ValueError(f"line {lineno}: empty key")
        if key in data:
            raise ValueError(f"line {lineno}: duplicate key {key!r}")
        data[key] = value
    return data


def check(
    path: Path,
    models: tuple[str, ...] = DEFAULT_MODELS,
    required: tuple[str, ...] = DEFAULT_REQUIRED,
) -> list[str]:
    problems: list[str] = []
    try:
        data = parse_frontmatter(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return [str(exc)]

    for field in required:
        if not data.get(field):
            problems.append(f"missing or empty required field: {field}")

    name = data.get("name", "")
    if name:
        if not SLUG.match(name):
            problems.append(f"name {name!r} is not a lowercase-hyphen slug")
        if name != path.stem:
            problems.append(f"name {name!r} does not match filename stem {path.stem!r}")

    model = data.get("model", "")
    if model and model not in models:
        problems.append(f"model {model!r} is not one of {sorted(models)}")

    description = data.get("description", "")
    if description:
        if "\n" in description:
            problems.append("description spans multiple lines")
        if len(description) < 30:
            problems.append("description is too short to route on")

    return problems


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(v.strip() for v in value.split(",") if v.strip())


def parse_args(argv: list[str]) -> tuple[list[str], tuple[str, ...], tuple[str, ...], bool]:
    paths: list[str] = []
    models, required, as_json = DEFAULT_MODELS, DEFAULT_REQUIRED, False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--models", "--require"):
            if i + 1 >= len(argv):
                raise ValueError(f"{arg} needs a value")
            value = _split_list(argv[i + 1])
            if not value:
                raise ValueError(f"{arg} needs a non-empty list")
            if arg == "--models":
                models = value
            else:
                required = value
            i += 2
        elif arg.startswith("--models=") or arg.startswith("--require="):
            flag, _, raw = arg.partition("=")
            value = _split_list(raw)
            if not value:
                raise ValueError(f"{flag} needs a non-empty list")
            if flag == "--models":
                models = value
            else:
                required = value
            i += 1
        elif arg == "--json":
            as_json = True
            i += 1
        elif arg.startswith("--"):
            raise ValueError(f"unknown option {arg}")
        else:
            paths.append(arg)
            i += 1
    return paths, models, required, as_json


def main(argv: list[str]) -> int:
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    try:
        args, models, required, as_json = parse_args(argv)
    except ValueError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return 2

    if args:
        paths = [Path(a) for a in args]
    else:
        root = Path(__file__).resolve().parent.parent / "agents"
        paths = sorted(p for p in root.rglob("*.md") if p.name != "README.md")

    if not paths:
        print("no files to check", file=sys.stderr)
        return 1

    results = [{"path": str(p), "problems": check(p, models, required)} for p in paths]
    failures = sum(1 for r in results if r["problems"])

    if as_json:
        print(
            json.dumps(
                {
                    "checked": len(results),
                    "passed": len(results) - failures,
                    "failed": failures,
                    "results": [
                        {"path": r["path"], "ok": not r["problems"], "problems": r["problems"]}
                        for r in results
                    ],
                },
                indent=2,
            )
        )
    else:
        for r in results:
            if r["problems"]:
                print(f"FAIL {r['path']}")
                for problem in r["problems"]:
                    print(f"     - {problem}")
            else:
                print(f"ok   {r['path']}")
        print(f"\n{len(results) - failures}/{len(results)} files passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
