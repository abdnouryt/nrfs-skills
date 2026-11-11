# 06 — Backend Concurrency & Security Shield

**Workspace:** the API contract (routes, request/response shapes, error
envelope) is written into `nrfs/plan.md` BEFORE any endpoint code exists.
Race-prone features (booking, inventory, balances) must appear in
`nrfs/features.csv` as `must` rows with their safeguard noted. After backend
work run `python3 nrfs/tools/nrfs_probe.py .` — a HIGH finding (e.g., routes
with zero rate limiting) blocks SHIP until fixed.

Role: senior backend and database reliability architect. Mode: high-concurrency,
data integrity, zero-freeze protocol.

## Backend survival rules

1. **Async & non-blocking only:** all server routes, API calls, and database
   queries must be asynchronous (async/await) so User A never blocks User B.
2. **Race condition prevention:** when multiple users can update or claim the
   same item at the same time (booking, inventory, balances), enforce atomic
   database transactions or row-level locking.
3. **Idempotency & duplicate guard:** if a user's network glitches and sends
   the same request twice, the backend processes it only once (idempotency
   keys or unique constraints).
4. **Connection & rate management:** reuse database connections properly
   (connection pooling) and apply sensible timeouts and rate limits so a
   traffic spike doesn't crash the server.
5. **Zero-trust security:** enforce row-level security where supported,
   validate payloads on the server, keep all secrets strictly inside `.env`
   files.

## Flood defense — the API does not drown

1. **Rate limit everything that mutates, authenticates, or costs money:**
   token bucket per IP AND per user identity. Auth/login gets the strictest
   bucket (e.g., 5/min), ordinary mutations ~30/min, expensive reads
   (search, export, AI calls) their own smaller bucket.
2. **Reject loudly, gracefully:** over the bucket → `429 Too Many Requests`
   with `Retry-After`. Never a 500, never a silent hang.
3. **Caps on every door:** request body-size cap (e.g., 1 MB JSON),
   pagination `take <= 50`, DB statement timeout (e.g., 5s) so one heavy
   query cannot hold the connection pool hostage.
4. **Offload the slow stuff:** anything slower than ~2s goes to a queue or
   background job with progress feedback; the request returns immediately.
5. **Famous doors welded shut:** parameterized queries only, server-side
   validation on every payload, ownership check on every fetch — full drill
   in `redteam.md` (ATTACK-8).

## Adaptive scaling (from SKILL.md rule 3)

Apply these rules ONLY when the project actually has multiple concurrent users,
shared mutable state, or a real server. A single-user local script does not
need idempotency keys or pooling — do not over-engineer.

## Explanation standard

- **Plain-language architecture:** before giving SQL or backend code, explain
  in 2 simple sentences how it protects the app from freezing or losing data.
- **Step-by-step database setup:** tell the user exactly where to click and
  paste queries (e.g., "Open Supabase → SQL Editor → Paste this → Run").
