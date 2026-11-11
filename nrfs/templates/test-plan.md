# NRFS Test Plan

> Written by NRFS TEST (from the flows in `plan.md`). Read by FIX and SHIP.

## Severity ladder

- **S1** — blocks ship: data loss, security hole, core flow broken
- **S2** — core broken in a real scenario, workaround ugly or absent
- **S3** — cosmetic / minor; note it, fix if cheap

## Flows under test

| # | Flow (from plan.md) | Happy path | Edge cases to try |
|---|---|---|---|
| F1 | sign up → verify → first action |  | double submit, expired link, weak password |
| F2 | core action (the money path) |  | simultaneous claims, network drop mid-submit |
| F3 |  |  |  |

## Edge-case battery (run on every data-driven screen)

- [ ] empty state (first-ever use)
- [ ] loading state (skeleton, not frozen UI)
- [ ] error state + Retry
- [ ] long content (60-char names, big numbers, RTL text)
- [ ] 390px mobile width and 1440px desktop
- [ ] keyboard-only completion of the flow
- [ ] double-click protection on every mutating button
- [ ] no console errors during any flow

## Results → `bugs.md`

Every failure gets a `bugs.md` entry with severity. TEST ends when zero S1/S2
are open or every open one has an owner and a plan in `bugs.md`.
