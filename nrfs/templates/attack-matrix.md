# NRFS Attack Matrix — simulated launch-day assault

> Written by NRFS SECURE/ATTACK (reference `redteam.md`). Every row is an
> attack the agent simulated on THIS app. Status: `open` → `blocked` only
> after re-verified. `pending-verify` = fix shipped but not reproducible
> locally (say why). Run the prober before closing any row:

```bash
python3 nrfs/tools/nrfs_probe.py .
```

## Famous vectors (closed by default)

| ID | Persona | Vector | Target (endpoint/page) | Status | Fix applied | Verified how |
|----|---------|--------|------------------------|--------|-------------|--------------|
| A1 | P5 Injector | stored XSS via user-generated field | | | | |
| A2 | P3 Flooder | no rate limit on auth/mutation route | | | | |
| A3 | P3 Flooder | uncapped pagination / payload size | | | | |
| A4 | P4 Impersonator | IDOR — object access without ownership check | | | | |
| A5 | P4 Impersonator | CSRF on cookie-session mutation | | | | |
| A6 | P5 Injector | SQL injection via string-built query | | | | |
| A7 | P1 Scanner | verbose errors / stack traces in prod | | | | |
| A8 | P6 Thief | secrets in client bundle (probe + sweep) | | | | |
| A9 | P2 Abuser | replay / double submission | | | | |
| A10 | P2 Abuser | mass assignment — raw body into DB | | | | |
| A11 | P5 Injector | open redirect via `?next=` | | | | |
| A12 | P1 Scanner | missing security headers (CSP, X-Frame-Options) | | | | |
| A13 | P2 Abuser | upload without type/size validation | | | | |
| A14 | P4 Impersonator | weak randomness for tokens/OTPs | | | | |

## ATTACK-8 drill answers (per public endpoint)

| Endpoint | #1 volume | #2 size | #3 ID swap | #4 replay | #5 contraband fields | #6 poison | #7 bypass | #8 shortcut |
|----------|-----------|---------|------------|-----------|----------------------|-----------|-----------|-------------|
| | | | | | | | | |

## Novel threats — Asset × Verb abuse sweep (min 3, domain-born)

| ID | Asset | Verb | Abuse scenario | Status | Fix | Verified |
|----|-------|------|----------------|--------|-----|----------|
| N1 | | | | | | |
| N2 | | | | | | |
| N3 | | | | | | |

## Verdict

- HIGH findings from `nrfs_probe.py`: **N** (must be 0 before SHIP)
- open vectors: **N** (must be 0, or `pending-verify` with a named reason)
- one-line launch-day posture: …
