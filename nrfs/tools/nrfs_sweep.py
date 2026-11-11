#!/usr/bin/env python3
"""NRFS sweep — secret-leak scanner for the pre-launch gate.

Scans a project tree for hardcoded secrets and committed environment files.
Standard library only, no network, no installs. Findings are printed with the
secret MASKED — this tool never reprints a full secret.

High severity (exit 1, blocks NRFS SHIP):
    AWS access keys, private key blocks, Google API keys, OpenAI/Anthropic
    style keys, Slack/GitHub tokens, raw JWTs, a committed .env file.
Medium severity (reported, needs eyes):
    key/secret/token/password assignments with literal values, and
    NEXT_PUBLIC_/VITE_ names that look like they carry secrets.

Usage:
    python3 nrfs_sweep.py .                # sweep the whole project
    python3 nrfs_sweep.py src              # sweep one folder
    python3 nrfs_sweep.py . --json         # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".next", "out", "coverage", ".turbo", ".cache",
    ".ruff_cache", ".mypy_cache", "Pods", "DerivedData",
}
SKIP_FILE_PARTS = (".min.js", ".map", ".lock")
SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock",
    "poetry.lock", "composer.lock", "Cargo.lock", "nrfs_sweep.py",
}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tiff", ".pdf",
    ".zip", ".gz", ".tgz", ".tar", ".rar", ".7z", ".mp3", ".mp4", ".mov",
    ".wav", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".sqlite", ".db",
    ".class", ".jar", ".so", ".dylib", ".dll", ".exe",
}
MAX_BYTES = 1_500_000

HIGH_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS access key id",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key block",
     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY( BLOCK)?-----")),
    ("Google API key",
     re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("OpenAI/Anthropic style key",
     re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}\b")),
    ("Slack token",
     re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b")),
    ("GitHub token",
     re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("raw JWT",
     re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
]

ASSIGN_RE = re.compile(
    r"\b(api[_\-]?key|apikey|secret|secret[_\-]?key|password|passwd|pwd|"
    r"access[_\-]?token|auth[_\-]?token|client[_\-]?secret|private[_\-]?key|"
    r"token)\b\s*[:=]\s*[\"']([^\"']{8,})[\"']",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(
    r"^(your|my|the)?[_\- ]?(api[_\-]?key|secret|token|password|key|example|"
    r"placeholder|dummy|changeme|change[_\-]?me|todo|fixme|redacted|xxx+|"
    r"insert|enter|paste)[_\- ].*|<[^>]+>|\$\{.*\}|\{\{.*\}\}|\$[A-Z_]+$",
    re.IGNORECASE,
)
ENV_REF_RE = re.compile(
    r"process\.env\.|import\.meta\.env\.|os\.environ|os\.getenv|getenv\(|"
    r"System\.getenv|ENV\[|config\(|settings\.",
    re.IGNORECASE,
)
PUBLIC_SECRET_NAME_RE = re.compile(
    r"\b(?:NEXT_PUBLIC|VITE|REACT_APP|EXPO_PUBLIC|NUXT_PUBLIC)_[A-Z0-9_]*"
    r"(?:SECRET|PRIVATE|TOKEN|PASSWORD|ADMIN|MASTER)[A-Z0-9_]*\b"
)
ENV_FILES = {".env", ".env.local", ".env.production", ".env.development"}


def _is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXT:
        return True
    try:
        chunk = path.open("rb").read(1024)
    except OSError:
        return True
    return b"\x00" in chunk


def _mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts if path != root else path.parts
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        name = path.name
        if name in SKIP_FILES or any(part in name for part in SKIP_FILE_PARTS):
            continue
        if path.suffix.lower() in BINARY_EXT or _is_binary(path):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        yield path


def sweep(root: Path) -> list[dict]:
    findings: list[dict] = []
    for path in iter_files(root):
        rel = str(path)
        if path.name in ENV_FILES:
            findings.append({
                "severity": "high", "file": rel, "line": 0,
                "type": "committed env file",
                "match": path.name,
                "advice": "add it to .gitignore, rotate every value inside, "
                          "keep only .env.example with placeholders",
            })
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if len(line) > 2000:
                continue
            for kind, pattern in HIGH_PATTERNS:
                hit = pattern.search(line)
                if hit:
                    findings.append({
                        "severity": "high", "file": rel, "line": lineno,
                        "type": kind, "match": _mask(hit.group(0)),
                        "advice": "move it to an environment variable, "
                                  "rotate the credential now — treat it as leaked",
                    })
            assign = ASSIGN_RE.search(line)
            if assign and not ENV_REF_RE.search(line):
                value = assign.group(2)
                if PLACEHOLDER_RE.match(value):
                    continue
                if value.lower() in {"true", "false", "none", "null"}:
                    continue
                findings.append({
                    "severity": "medium", "file": rel, "line": lineno,
                    "type": "literal secret assignment",
                    "match": f"{assign.group(1)}={_mask(value)}",
                    "advice": "load it from the environment instead; if this is "
                              "a real value, rotate it",
                })
            for hit in PUBLIC_SECRET_NAME_RE.finditer(line):
                findings.append({
                    "severity": "medium", "file": rel, "line": lineno,
                    "type": "publicly exposed secret-named variable",
                    "match": hit.group(0),
                    "advice": "anything with this prefix ships to the browser — "
                              "remove the secret from the public bundle",
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="NRFS secret-leak sweep")
    parser.add_argument("root", nargs="?", default=".", type=Path,
                        help="project root to scan (default: current folder)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 2

    findings = sweep(root)
    high = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]

    if args.json:
        print(json.dumps({"root": str(root), "findings": findings}, indent=2))
    else:
        if not findings:
            print(f"NRFS sweep — {root}")
            print("  clean: no secrets found in scannable files.")
            print("  (this is a static scan — it is not a guarantee; "
                  "rotate any key that was ever committed)")
            return 0
        print(f"NRFS sweep — {root}")
        for sev, group in (("HIGH", high), ("MEDIUM", medium)):
            for f in group:
                where = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
                print(f"  [{sev}] {where} — {f['type']}")
                print(f"        match: {f['match']}")
                print(f"        fix:   {f['advice']}")
        print(f"  total: {len(high)} high, {len(medium)} medium")

    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
