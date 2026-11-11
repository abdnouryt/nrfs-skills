# NRFS Preflight — verdict per item before launch

> Written by NRFS SHIP. Every item is PASS or FAIL **with evidence** (command
> output, file, number). Report the numbers, not a vibe.

## Gate 1 — secrets (BLOCKER)

```bash
python3 nrfs/tools/nrfs_sweep.py .
```

- [ ] sweep clean — no hardcoded keys, tokens, or private URLs
- [ ] `.env` in `.gitignore`, `.env.example` present without real values
- [ ] no secret behind any `NEXT_PUBLIC_`/`VITE_` prefix

## Gate 2 — correctness (BLOCKER)

- [ ] production build passes (`npm run build` / framework equivalent)
- [ ] zero open S1/S2 in `bugs.md`
- [ ] all `must` rows done in `features.csv` (`nrfs_score.py` — print the score)

## Gate 3 — resilience

- [ ] global error boundary: one broken component ≠ white screen
- [ ] the 4 states on every data-driven screen
- [ ] production cleanup: no test logs, dummy buttons, unused imports

## Gate 4 — attack surface (BLOCKER)

```bash
python3 nrfs/tools/nrfs_probe.py .
```

- [ ] probe exits 0 — zero HIGH findings (XSS, floods, injection, alg:none,
      weak randomness, uploads without caps)
- [ ] every vector in `attack-matrix.md` is `blocked` or `pending-verify`
      with a named reason
- [ ] rate limiting present on auth + money routes; 429 with Retry-After

## Gate 5 — core flow (human test)

- [ ] main journey end to end, desktop + mobile widths
- [ ] main action survives fast repeated clicking

## Deployment (click-by-click for the chosen platform)

1. …
2. …

## Post-launch checklist for the user (4 points)

1. open on a phone: mobile view + login
2. run the money path once for real
3. click the main action fast and repeatedly — watch for errors
4. try the obvious abuse once (wrong password x6, huge upload, `<script>`
   in a field) — expect a clean rejection, never a crash
