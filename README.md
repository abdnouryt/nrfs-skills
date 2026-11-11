<div align="center">

# NRFS — NR Full-Stack Engine

**One skill that gives any AI coding agent a complete engineering method — an attacker's paranoia and an anatomist's memory included.**


NR FULL STACK (NRFS) · formerly NR-FULL-STACK · v1.0.0 · `SKILL.md` · 12 specialists · 12 boosters · 8 templates · 3 verification tools · MIT

</div>

---

## English

### What this is

NRFS is **one instruction skill** in the open [Agent Skills](https://code.claude.com/docs/en/skills) format: a `SKILL.md` with reference protocols, ready templates, and three small verification tools. Load it into Claude Code, Cursor, Windsurf, Cline, Aider, Codex CLI, OpenCode — or paste it into any chat model — and the agent stops guessing and starts running a pipeline: review the idea → plan in weighted steps → design with intent → build complete files → secure what matters → **attack it like a hacker** → test by flows → score the result → audit and ship.

It is **instructions, not software**: no runtime, no server, no API keys, nothing to subscribe to. The only executable code is three standard-library Python tools (no installs, no network) that turn opinions into numbers. Result quality depends on the model that executes the method.

### What makes it strong

- **A chained workspace.** Every stage writes real files into a `nrfs/` folder in your project — the plan, the weighted feature matrix, the checklist, design tokens, the attack matrix, the test plan, the bug log, the audit verdict — and the next stage reads them. Work survives across sessions instead of evaporating with the chat.
- **An attacker lives inside.** The Red Team Lead protocol (`redteam.md`) simulates launch day before it happens: seven attacker personas, the ATTACK-8 drill on every endpoint, and an Asset × Verb sweep that invents threats specific to YOUR app — the agent hunts the holes itself, you never have to point at one. The famous doors (XSS, injection, CSRF, IDOR, rate-limit floods, weak randomness) are welded shut by default.
- **It already knows what your pages need.** The App Anatomist protocol (`anatomy.md`) carries the mandatory organ list for every page type — landing, auth, dashboard, list, detail, form, settings, checkout, profile, search, errors — plus the 4-state matrix (loading/empty/error/success). Standard elements are included automatically; the user removes, the agent never omits and then asks.
- **Weighted scoring, not vibes.** `nrfs_score.py` scores the feature matrix: must=3, should=2, could=1, partial counts as half, skipped rows excluded, additions listed separately — and any unfinished must-have means **not shippable**, exit code non-zero.
- **Launch gates that actually block.** `nrfs_sweep.py` scans for hardcoded secrets and committed `.env` files (masked output). `nrfs_probe.py` plays the attacker against your code: raw HTML injection, eval, string-built SQL, `alg:none` JWTs, predictable randomness, uploads without size caps, unbounded queries — and a project full of routes with zero rate limiting. Any HIGH finding from either tool blocks NRFS SHIP.
- **Templates, not blank pages.** Eight ready artifacts: `features.csv`, `checklist.md`, `plan.md`, `design-tokens.json`, `attack-matrix.md`, `test-plan.md`, `bug-report.md`, `preflight.md`.
- **Trigger words.** Say "NRFS plan", "NRFS attack my app", "is it ready to ship" — or just describe the task; the skill's description routes it.

### What's inside

```
nrfs/
├── SKILL.md                # the engine: NXS loop, modes, workspace contract, non-negotiables
├── references/             # 12 specialist protocols + NXS core + 12 boosters
│   ├── nxs-core.md         # 00 · full cognitive engine (deep mode)
│   ├── tracker.md          # 01 · master checklist, one step at a time
│   ├── engineer.md         # 02 · production code, complete files only
│   ├── edge-cases.md       # 03 · real-world risk discovery before building
│   ├── design.md           # 04 · bespoke visual direction, anatomy-first
│   ├── uiux.md             # 05 · 4 UI states, anti-double-click, resilience
│   ├── backend.md          # 06 · async, races, idempotency, flood defense
│   ├── security.md         # 07 · auth hardening, encryption, anti-scraping
│   ├── debugger.md         # 08 · zero-regression root-cause fixing
│   ├── audit.md            # 09 · preflight gates + click-by-click deploy
│   ├── reviewer.md         # 10 · missing-requirement discovery
│   ├── redteam.md          # 11 · attacker personas, ATTACK-8 drill, novel threats
│   ├── anatomy.md          # 12 · the mandatory organs of every page type
│   └── boosters.md         # git, API contracts, a11y, RTL, deps, scope…
├── templates/              # 8 artifacts the workspace copies and fills
├── tools/
│   ├── nrfs_score.py        # weighted feature-parity scorer
│   ├── nrfs_sweep.py        # secret-leak sweep (masked output)
│   └── nrfs_probe.py        # attack-surface prober (XSS, SQLi, floods…)
├── sources/                # the 11 original JSON modules NRFS was distilled from
└── install.sh
```

### The modes

| Say | Runs | Writes |
|---|---|---|
| `NRFS review` | reviewer + edge-cases | findings + ready-to-paste requirements |
| `NRFS plan` | tracker + engineer + edge-cases | `plan.md`, `features.csv`, `checklist.md` |
| `NRFS design` | art director + state guard + anatomist | `design-tokens.json` + anatomy-merged checklist + components |
| `NRFS build` | engineer + uiux + anatomist (+ backend) | code + checklist/features/build-log updates |
| `NRFS secure` | security + backend + redteam | hardened auth/API + famous vectors closed in `attack-matrix.md` |
| `NRFS attack` | redteam + `nrfs_probe.py` | full launch-day drill: ATTACK-8 per endpoint, ≥3 novel threats, verified fixes |
| `NRFS fix` | surgical debugger | `bugs.md` + complete corrected files |
| `NRFS test` | uiux + boosters | `test-plan.md`, `bugs.md` |
| `NRFS score` | `nrfs_score.py` | parity score + missing list |
| `NRFS ship` | audit + `nrfs_sweep.py` + `nrfs_probe.py` | `audit.md` + deployment walkthrough |

Full pipeline: `review → plan → design → build → secure (if needed) → attack → test → score → ship`. Enter at any mode; NRFS reads the existing `nrfs/` artifacts first.

### The tools

```bash
python3 nrfs/tools/nrfs_score.py nrfs/features.csv     # parity score + missing list
python3 nrfs/tools/nrfs_sweep.py .                     # secret sweep — blocks ship when dirty
python3 nrfs/tools/nrfs_probe.py .                     # attack probe — exit 1 on any HIGH
```

All three are standard-library Python 3.8+, no installs, no network, no data leaves your machine.

### Installation

**Claude Code — as a plugin** (from this repo's root):

```
/plugin marketplace add abdnouryt/nrfs-skills
/plugin install nrfs@nrfs
```

**Claude Code — plain skills:**

```bash
./install.sh project    # this project → ./.claude/skills/
./install.sh global     # all projects → ~/.claude/skills/
```

**Any other agent or chat model:**

```bash
./install.sh --flat NRFS.md   # the whole engine as one markdown file
```

Point your agent to that file (`.cursorrules`, `AGENTS.md`, custom instructions) or paste `nrfs/SKILL.md` into the system prompt — the method works even without tools, you just lose the three CLI gates.

### A worked example (small but real)

*"Build a booking page for my barbershop."*

1. **NRFS review** — flags what you forgot: double-booking the same slot, no-shows, Arabic-first customers. Those become `should`/`must` rows in `features.csv`.
2. **NRFS plan** — picks the stack, writes the data model **with the constraint that two guests can never book the same slot**, defines the API contract, orders the build. 12 checklist items.
3. **NRFS build** — one step per response, complete files, all 4 UI states per screen — and the anatomy of a booking page (slot grid, confirmation state, no-show handling) was already merged into the checklist before you asked.
4. **NRFS attack** — the probe flags `dangerouslySetInnerHTML` on the reviews feed (HIGH), zero rate limiting across 9 routes (HIGH), and an unbounded `findMany()` (MEDIUM). The ATTACK-8 drill adds: one user hammering the same slot 10,000×/minute, and booking someone else's appointment by editing the ID. Every vector lands in `attack-matrix.md`, gets a fix, and gets re-verified — probe exit code `1 → 0`.
5. **NRFS test** — double submit, network drop mid-booking, 60-char names. One S2 → **NRFS fix** closes it, verified.
6. **NRFS score** — `83%` — must-haves 1/2 done. Not shippable, and the tool says so in exactly those words.
7. **NRFS ship** — sweep finds a hardcoded API key in `src/config.ts` (masked), blocks launch, you move it to `.env`, both gates turn green, deployment goes click-by-click.

That is the difference: the agent does not *feel* done — the gates say done, and the attacker was already invited and turned away.

### Fine print (read this)

- This is a methodology with three small scanners, not a guarantee. It structures an agent's work; it does not replace the model's capability.
- The red-team protocol hardens apps against common attack classes (XSS, injection, floods, IDOR, session theft, scraping). No instruction file makes anything "un-hackable", and `nrfs_sweep.py` + `nrfs_probe.py` are heuristic static scans — they are not a security audit or a penetration test. For anything touching real money or sensitive data at scale, hire a professional pentest.
- The parity score measures what `features.csv` says. If the matrix is wrong, the score is honestly wrong with it.
- The anatomies cover conventional web app shapes. Genuinely novel interfaces still need human judgment — the protocol forces the completeness question, it cannot answer every product question.
- Works best with agents that can read files, edit files, and run commands. In a plain chat, planning/design/attack-simulation protocols still apply; tool-gated rules have nothing to act on.

### Credits & license

Distilled from the NR-AI agent system by **NR01X** — the original 11 JSON modules are included verbatim in [`nrfs/sources/`](nrfs/sources/).

- Instagram: **[@nr01xx](https://instagram.com/nr01xx)**
- License: MIT (see [LICENSE](LICENSE))

---

