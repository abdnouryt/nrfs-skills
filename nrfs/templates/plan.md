# NRFS Plan

> Written by NRFS PLAN. Read by NRFS BUILD, SECURE, TEST, SHIP. Update it when
> a decision changes, and log the change in `decisions.md`.

## 1. Scope (one sentence)

What this project is, for whom, and its real-world environment:

## 2. Stack (and why)

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Frontend |  |  |
| Backend |  |  |
| Database |  |  |
| Auth |  | (or: none needed — do not over-engineer) |
| Payments/Email/etc. |  |  |

## 3. Data model

Entities, fields, relations, constraints. Include the constraint that
prevents the worst race condition (e.g., two users claiming the same slot):

```
(users) ──< (orders)
  ...
```

## 4. API contract (before any endpoint code)

One consistent error envelope across the whole API:

```json
{ "error": { "code": "VALIDATION", "message": "..." } }
```

| Route | Method | Request | Response | Auth |
|---|---|---|---|---|
| /api/v1/… | POST |  |  |  |

## 5. Build order

The order NRFS BUILD executes. The core flow end-to-end comes FIRST (vertical
slice), screens after, polish last:

1. Scaffold + env + git
2. Data layer + seed
3. Core flow end to end
4. Screen by screen (list them)
5. Hardening + tests

## 6. Out of scope (on purpose)

Things deliberately excluded, so SCORE never punishes them:
- …
