# NRFS Boosters — 12 strengthening protocols

These twelve protocols extend the twelve specialists — the ten inherited from
the NR-AI system plus the Red Team Lead (`redteam.md`, #11) and the App
Anatomist (`anatomy.md`, #12). They cover what the base system did not
explicitly spell out. Apply them alongside every relevant specialist — they
are part of the standard, not optional.

**Workspace note:** key choices made under these rules are recorded in
`nrfs/decisions.md` (one line each: decision · why · date). Future sessions
read it before touching anything.

## 1. Verify before "done"

- Never claim a task is complete without evidence: the code ran, the build
  passed, or the exact manual test path was written out.
- Definition of done for every step: code complete → build/compile passes →
  the specific flow tested → result reported with what was actually verified.
- If something could not be verified in this environment, say exactly what and
  why — never imply success.

## 2. State truth & anti-hallucination

- Derive project state from the filesystem, not from memory of earlier
  conversation turns: re-read files before editing them.
- Never invent file paths, APIs, CLI flags, or library functions. If unsure,
  verify with tools (search the codebase, read docs, check package.json).
- If a fact cannot be verified, label it as unverified instead of guessing.

## 3. Git discipline

- `.gitignore` exists from step 0 (node_modules, build output, .env, OS junk).
- One atomic commit per checklist step, message format:
  `type: short description` (feat / fix / chore / docs).
- Never commit secrets, `.env`, or generated artifacts. Tag releases
  (`v1.0.0`) at launch.

## 4. Data model & migration safety

- Design the schema first (entities, relations, constraints) before writing
  queries or UI that depends on it.
- Migrations are additive by default; destructive changes (drop column/table)
  require an explicit warning and a backup step.
- Provide seed/demo data for anything the user must see to verify the build.

## 5. API contract first

- Before implementing endpoints, define the contract: route, method, request
  shape, response shape, and error shape.
- One consistent error envelope across the whole API (e.g.,
  `{ "error": { "code": "...", "message": "..." } }`).
- Keep frontend and backend in sync with the same types; version the API
  (`/api/v1/...`) when a breaking change is unavoidable.

## 6. Accessibility baseline

- Semantic HTML first (button, form, nav, main); keyboard path for every
  action; visible focus states.
- ARIA attributes only where semantics are not enough; every image has alt
  text; every icon-only button has an accessible name.
- Text contrast meets WCAG AA; interactive targets are at least 44px on touch
  screens.

## 7. Performance budget

- Optimize images (modern formats, correct sizes), lazy-load below-the-fold
  content, cache what is cacheable.
- No blocking operations on the main thread; heavy work goes async.
- Measure before optimizing: fix the slowest real thing first, not what looks
  slow in theory.

## 8. Arabic & RTL readiness

- If the audience is Arabic-speaking, design RTL from day one: `dir="rtl"`,
  fonts with real Arabic coverage, mirrored layouts via CSS logical properties
  (`margin-inline-start`, not `margin-left`).
- Locale-aware dates, numbers, and currency; never concatenate translated
  fragments — use full translated strings.
- Mixed Arabic/English content: test both directions in the same screen.

## 9. Environment & config hygiene

- Ship a `.env.example` listing every required variable (names only, no real
  values); `.env` itself is git-ignored.
- Validate configuration at boot and fail fast with a clear message naming the
  missing variable.
- No secrets behind `NEXT_PUBLIC_`/`VITE_`/frontend-visible prefixes — if the
  browser can see it, it is public.

## 10. Dependency hygiene

- Add a dependency only when the cost is justified (maintenance, size,
  supply-chain risk). Prefer stdlib and framework built-ins first.
- Pin versions; before adding a package check that it is maintained and does
  not duplicate something already installed.
- Removing an unused dependency is a legitimate chore step.

## 11. Scope guard

- New ideas discovered mid-build become new numbered checklist items — never
  silent scope creep inside the current step.
- If it is not on the checklist, it does not ship in this step.
- Distinguish explicitly: bug fix vs new feature vs refactor — each has a
  different protocol (debugger vs tracker vs engineer).

## 12. Docs & handoff

- Every project ends with a README: what it is, how to run it, how to build
  it, how to deploy it, where the env variables live.
- Record key decisions (stack choices, trade-offs) in one place as they are
  made — future sessions and future developers depend on it.
- Leave the project understandable to a non-technical owner: plain-language
  architecture summary included.
