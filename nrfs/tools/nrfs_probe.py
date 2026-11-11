#!/usr/bin/env python3
"""NRFS probe — static attack-surface prober for the red-team gate.

Thinks like the attacker on launch day: scans a project tree for the
well-known doors an attacker opens first. Standard library only, no network,
no installs. This is a heuristic static scan — it finds what an attacker
finds in minutes, not a substitute for a real pentest.

High severity (exit 1, blocks NRFS SHIP):
    raw HTML injection points (XSS), eval/new Function, SQL built by string
    concatenation, JWT `alg: none`, predictable randomness used for security
    values, a project full of routes with zero rate limiting.
Medium severity (reported, needs eyes):
    wildcard CORS, open redirects, `target="_blank"` without `rel=noopener`,
    session-ish cookies without HttpOnly, unbounded queries, upload
    endpoints without a size cap, missing Content-Security-Policy,
    document.write, weak hashes.

Usage:
    python3 nrfs_probe.py .                # probe the whole project
    python3 nrfs_probe.py src              # probe one folder
    python3 nrfs_probe.py . --json         # machine-readable output
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
    "poetry.lock", "composer.lock", "Cargo.lock",
    "nrfs_probe.py", "nrfs_sweep.py", "nrfs_score.py",
}
SCAN_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".py"}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tiff", ".pdf",
    ".zip", ".gz", ".tgz", ".tar", ".rar", ".7z", ".mp3", ".mp4", ".mov",
    ".wav", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".sqlite", ".db",
    ".class", ".jar", ".so", ".dylib", ".dll", ".exe",
}
MAX_BYTES = 1_500_000
MAX_LINES_PER_FILE = 4000

SANITIZER_RE = re.compile(r"DOMPurify|dompurify|sanitize|Sanitize|purify|xss\(.*\)")
SECURITY_VALUE_RE = re.compile(
    r"token|secret|session|otp|passwd|password|nonce|csrf|api[_\-]?key|salt|verify",
    re.IGNORECASE,
)
ROUTE_RE = re.compile(
    r"^\s*export\s+(?:async\s+)?function\s+(?:GET|POST|PUT|PATCH|DELETE)\b"
    r"|\b(?:app|router)\.(?:get|post|put|patch|delete|all)\s*\("
    r"|@(?:app|router)\.(?:get|post|put|patch|delete)\s*\(",
)
RATE_LIMIT_RE = re.compile(
    r"rate[_\-]?limit|ratelimit|limiter|throttle|token[_\- ]?bucket|"
    r"sliding[_\- ]?window|\b429\b",
    re.IGNORECASE,
)
CSP_RE = re.compile(r"Content-Security-Policy|helmet\(", re.IGNORECASE)


def C(pattern: str, flags: int = 0) -> re.Pattern[str]:
    return re.compile(pattern, flags)


# --- per-line rules -------------------------------------------------------
# (rule_id, severity, pattern, message, fix)
LINE_RULES: list[tuple[str, str, re.Pattern[str], str, str]] = [
    ("XSS-002", "high",
     C(r"\.\s*innerHTML\s*=\s*[^;\n]*(?:`|\+)"),
     "innerHTML assigned from a template/concatenation expression",
     "insert text nodes instead, or sanitize with DOMPurify before injection"),
    ("XSS-003", "high",
     C(r"\beval\s*\("),
     "eval() executes attacker-controlled strings as code",
     "use JSON.parse, lookup objects, or explicit branching — delete eval"),
    ("XSS-004", "high",
     C(r"new\s+Function\s*\("),
     "new Function() is eval in disguise",
     "remove it; dynamic behavior belongs in data, not generated code"),
    ("XSS-005", "medium",
     C(r"document\.write\s*\("),
     "document.write can inject markup into the live DOM",
     "render through the framework; never write raw markup post-load"),
    ("RAND-001", "high",
     C(r"Math\.random\s*\(\)|random\.(?:random|randint|choice|randbytes)\s*\("),
     "predictable randomness used in a security-sensitive line",
     "use crypto.getRandomValues() / node:crypto randomBytes for tokens, "
     "OTPs, secrets"),
    ("CRYPTO-001", "medium",
     C(r"hashlib\.(?:md5|sha1)\s*\(|createHash\(\s*[\"'](?:md5|sha1)[\"']"),
     "weak hash (MD5/SHA-1) in use",
     "use SHA-256 or better; passwords need bcrypt/argon2/scrypt"),
    ("JWT-001", "high",
     C(r"(?:algorithm|alg)\s*:\s*[\"']none[\"']"),
     "JWT accepts/signs with alg:none — anyone can forge tokens",
     "pin an explicit algorithm (e.g. HS256/RS256) on sign AND verify"),
    ("SQLI-001", "high",
     C(r"f[\"']\s*(?:SELECT|INSERT|UPDATE|DELETE)"
       r"|\.execute\(\s*f[\"']|\.query\(\s*f[\"']"
       r"|[\"'](?:SELECT|INSERT|UPDATE|DELETE)[^\"']*[\"']\s*\+"),
     "SQL query built by string interpolation/concatenation",
     "parameterized queries or ORM calls only — never build SQL text"),
    ("SQLI-002", "high",
     C(r"\$(?:query|execute)RawUnsafe\s*\("),
     "raw unsafe query accepts a free-form SQL string at runtime",
     "use the tagged-template $queryRaw or parameterized ORM calls"),
    ("CORS-001", "medium",
     C(r"origin\s*:\s*[\"']\*[\"']"
       r"|Access-Control-Allow-Origin[\"']?\s*[,:]\s*[\"']\*"),
     "wildcard CORS origin",
     "allow-list the exact frontend origins; never reflect arbitrary origins"),
    ("URL-002", "medium",
     C(r"target\s*=\s*[\"']?_blank(?![^>]*rel\s*=)"),
     "link opens a new tab without rel=noopener (reverse tabnabbing)",
     'add rel="noopener noreferrer"'),
    ("OPENRED-001", "medium",
     C(r"redirect\s*\([^)]*(?:searchParams|params\.get|query\.get|req\.query|"
       r"nextUrl\.searchParams)"),
     "redirect target taken from a request parameter without validation",
     "validate against an allow-list of internal paths before redirecting"),
    ("COOKIE-001", "medium",
     C(r"(?:cookies\(\)\.set\(|\.cookie\(\s*[\"']|Set-Cookie)"
       r"[^\n]*",
     ),
     "cookie set on a security-looking line — check the flags",
     "session/auth cookies need HttpOnly, Secure, SameSite (see "
     "redteam.md famous doors)"),
]

COOKIE_NAME_RE = re.compile(r"token|session|jwt|auth|refresh", re.IGNORECASE)
HTTPONLY_RE = re.compile(r"httpOnly|httponly|HttpOnly", re.IGNORECASE)

# --- per-file rules (multi-line) -----------------------------------------
DANGEROUS_HTML_RE = C(r"dangerouslySetInnerHTML|v-html|\.html\s*\(\s*[^)]*\+")
FIND_MANY_RE = C(r"\.findMany\s*\(")
TAKE_RE = C(r"\btake\s*[:=]")
UPLOAD_RE = C(r"formData\s*\(|multipart|file\(\)\s")
SIZE_CAP_RE = C(
    r"MAX_(?:FILE|SIZE)|maxSize|max_file_size|fileSize|file_size|sizeLimit|"
    r"content[-_]?length|1024\s*\*\s*1024",
    re.IGNORECASE,
)


def _is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXT:
        return True
    try:
        chunk = path.open("rb").read(1024)
    except OSError:
        return True
    return b"\x00" in chunk


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        name = path.name
        if name in SKIP_FILES or any(part in name for part in SKIP_FILE_PARTS):
            continue
        if path.suffix.lower() not in SCAN_EXT:
            continue
        if _is_binary(path):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        yield path


def probe(root: Path) -> list[dict]:
    findings: list[dict] = []
    route_count = 0
    rate_limit_seen = False
    csp_seen = False

    def add(sev: str, rid: str, file: str, line: int,
            msg: str, match: str, fix: str) -> None:
        findings.append({
            "severity": sev, "rule": rid, "file": file, "line": line,
            "message": msg, "match": match.strip()[:160], "fix": fix,
        })

    for path in iter_files(root):
        rel = str(path)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        lines = text.splitlines()
        if len(lines) > MAX_LINES_PER_FILE:
            lines = lines[:MAX_LINES_PER_FILE]

        has_sanitizer = bool(SANITIZER_RE.search(text))
        has_dangerous_html = False
        find_many_lines: list[int] = []
        has_take = bool(TAKE_RE.search(text))
        is_upload = False
        has_size_cap = bool(SIZE_CAP_RE.search(text))
        route_in_file = False

        for lineno, line in enumerate(lines, 1):
            if len(line) > 2000:
                continue
            if ROUTE_RE.search(line):
                route_count += 1
                route_in_file = True
            if RATE_LIMIT_RE.search(line):
                rate_limit_seen = True
            if CSP_RE.search(line):
                csp_seen = True

            for rid, sev, pattern, msg, fix in LINE_RULES:
                hit = pattern.search(line)
                if not hit:
                    continue
                if rid == "RAND-001" and not SECURITY_VALUE_RE.search(line):
                    continue
                if rid == "COOKIE-001":
                    if not COOKIE_NAME_RE.search(line):
                        continue
                    if HTTPONLY_RE.search(text):
                        continue  # set somewhere in this file — needs eyes, not a firing
                add(sev, rid, rel, lineno, msg, hit.group(0), fix)

            if DANGEROUS_HTML_RE.search(line):
                has_dangerous_html = True
            if FIND_MANY_RE.search(line):
                find_many_lines.append(lineno)
            if UPLOAD_RE.search(line):
                is_upload = True

        # file-level verdicts
        if has_dangerous_html:
            if not has_sanitizer:
                add("high", "XSS-001", rel, 0,
                    "raw HTML injection point (dangerouslySetInnerHTML/v-html/"
                    ".html) with no sanitizer in the file",
                    "dangerouslySetInnerHTML / v-html",
                    "sanitize user content with DOMPurify, or render plain "
                    "text — never trust client HTML")
            else:
                add("low", "XSS-001", rel, 0,
                    "HTML injection point WITH a sanitizer present — verify "
                    "every value passes through it",
                    "dangerouslySetInnerHTML / v-html",
                    "confirm the sanitizer wraps every dynamic value")
        if find_many_lines and not has_take:
            for lineno in find_many_lines:
                add("medium", "DOS-001", rel, lineno,
                    "findMany() without take — unbounded query, one request "
                    "can dump the whole table",
                    ".findMany()",
                    "cap it (take <= 50) + cursor/offset pagination")
        if is_upload and route_in_file and not has_size_cap:
            add("medium", "DOS-002", rel, 0,
                "upload handling with no visible server-side size cap",
                "formData()/multipart",
                "enforce max file size + type allow-list, re-encode images")

    # project-level verdicts
    if route_count >= 3 and not rate_limit_seen:
        add("high", "RL-001", "(project)", 0,
            f"{route_count} route handlers and zero rate limiting in the "
            "project — request floods can crush the API and the bill",
            "no rate-limit/throttle/429 reference found",
            "add per-IP + per-identity limits (stricter on auth and money "
            "routes), return 429 with Retry-After; see redteam.md")
    if route_count >= 1 and not csp_seen:
        add("medium", "CSP-001", "(project)", 0,
            "no Content-Security-Policy found for a project that serves routes",
            "no CSP/helmet reference found",
            "set CSP (default-src 'self'; no unsafe-inline without nonce) "
            "via headers/middleware")

    findings.sort(key=lambda f: ({"high": 0, "medium": 1, "low": 2}[f["severity"]],
                                 f["rule"], f["file"], f["line"]))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="NRFS attack-surface probe")
    parser.add_argument("root", nargs="?", default=".", type=Path,
                        help="project root to scan (default: current folder)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 2

    findings = probe(root)
    high = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]
    low = [f for f in findings if f["severity"] == "low"]

    if args.json:
        print(json.dumps({"root": str(root), "findings": findings}, indent=2))
    else:
        print(f"NRFS probe — {root}")
        if not findings:
            print("  clean: no known attack surface found in scannable files.")
            print("  (static scan — it finds doors an attacker finds in "
                  "minutes, not a pentest; run the ATTACK-8 drill too)")
            return 0
        for sev, group in (("HIGH", high), ("MEDIUM", medium), ("LOW", low)):
            for f in group:
                where = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
                print(f"  [{sev}] {f['rule']} {where}")
                print(f"        what:  {f['message']}")
                print(f"        match: {f['match']}")
                print(f"        fix:   {f['fix']}")
        print(f"  total: {len(high)} high, {len(medium)} medium, {len(low)} low")
        if high:
            print("  verdict: NOT SAFE TO SHIP — close every HIGH first "
                  "(redteam.md famous doors + ATTACK-8 drill)")
        else:
            print("  verdict: no HIGH findings — review MEDIUM items, then "
                  "run the ATTACK-8 drill on every public endpoint")

    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
