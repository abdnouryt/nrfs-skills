# NRFS Master Checklist

> The plan of record. Every NRFS mode reads this; NRFS PLAN and NRFS BUILD keep
> it current. One numbered task per line. Indent sub-steps under their task.
> Status: `[X]` done · `[⏳]` in progress · `[ ]` pending.

## Master Task Checklist

1. [ ] Project scaffold + `.gitignore` + `.env.example` (Boosters #3, #9)
2. [ ] Data model + migrations + seed data (Booster #4)
3. [ ] API contract implemented (from `plan.md`)
4. [ ] Core flow end to end (the vertical slice — ugly but working)
5. [ ] Screen: ___ — all 4 states (loading / empty / error / success)
6. [ ] Screen: ___ — all 4 states
7. [ ] Auth hardening (only if the project has auth — SECURE mode)
8. [ ] Test plan executed (`test-plan.md`), zero open S1/S2
9. [ ] Parity score ≥ target, all `must` rows done (`nrfs_score.py`)
10. [ ] Preflight passed (`audit.md`), sweep clean (`nrfs_sweep.py`)

## How to add a discovered idea (Scope Guard, Booster #11)

New idea mid-build → append it as a new numbered item below, mark `[ ]`,
never fold it silently into the current step.

## Discovered during build

- (append here)
