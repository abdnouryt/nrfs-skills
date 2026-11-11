# 12 — App Anatomist: Implicit Completeness Protocol

**Workspace:** the chosen page-type anatomies are recorded as numbered
checklist items in `nrfs/checklist.md` (one line per mandatory element). A
page is DONE only when its anatomy is complete or an element was excluded
with a one-line reason in `nrfs/decisions.md`. Missing anatomy = incomplete
build, never a follow-up question.

Role: application anatomist — the engineer who has built every page type so
many times that the required organs are memorized. Directive: **the user
describes an app in one sentence; NRFS already knows what that kind of page
MUST contain. Standard elements are included by default, not proposed. The
user removes — the agent never omits and then asks "do you also want…".**

## The default-inclusion rule

1. Classify the project and list its page types (landing, auth, dashboard,
   list, detail, form, settings, checkout, profile, search, errors).
2. Pull each page's anatomy from this file — automatically, silently, into
   the checklist.
3. Every mandatory element ships unless the user explicitly removes it or
   `decisions.md` records why it is excluded for this product.
4. Asking "should the list page have search and pagination?" is a defect —
   the answer is yes; the only open question is which flavor.

## Global anatomy — every web app, no exceptions

- Navigation with brand link + primary actions; auth-aware (logged-in vs
  guest states).
- Auth guard: protected routes redirect to login; logged-in users are kept
  away from login/register pages.
- 404 page with a recovery action (search or home); branded, never raw.
- Global error boundary / 500 page with retry — one broken component never
  whitescreens the app.
- Loading skeletons for every async view (never a blank wall).
- Toast/feedback system for success, failure, and undo.
- Inline form validation with field-level errors.
- Confirmation (type-to-confirm for irreversible) on destructive actions.
- Empty state for every collection: illustration/word + explanation + one
  primary action.
- Responsive from 360px up; touch targets >= 44px; keyboard accessible with
  visible focus states.
- SEO minimum for public pages: title, description, favicon, OG image.
- Theme decision recorded (dark, light, or system) — an unstyled flash or
  accidental mix is a defect.
- Privacy/terms/contact reachable for anything public that collects data.

## The state matrix — 4 states per async view

Every data-driven screen implements all four or it is not done:

| State | Requirement |
|-------|-------------|
| Loading | skeleton or spinner shaped like the real content |
| Empty | first-run explanation + primary action ("create your first X") |
| Error | what failed + retry action; never a raw error string |
| Success | the data, plus feedback for the action that caused it |

## Page-type anatomies

**Landing page:** hero (promise headline + sub-line + primary CTA + secondary
CTA + product visual), social proof strip (logos, numbers, or testimonials),
3–6 benefit features, how-it-works in 3 steps, pricing or plan summary, FAQ,
final conversion CTA, footer (nav, legal, contact).

**Auth — login:** identifier + password, show/hide password, forgot-password
link, third-party options when they exist, field-level errors, submit
loading state, redirect-after-login (to `?next=` — allow-listed), generic
"wrong email or password" (never reveal which half was wrong), rate-limited
attempts.

**Auth — register:** field validation inline, password strength signal,
terms checkbox, email-verification step, auto-login or explicit login after.

**Auth — forgot/reset:** request form (same generic response whether or not
the email exists), reset form with token-expiry messaging, invalidate old
sessions on success.

**Dashboard:** KPI summary row (3–4 numbers that matter), primary chart or
table, filters + date-range picker, recent-activity feed, new-account empty
state, skeleton loading, drill-down links into detail pages.

**List/table page:** search, filters, sort, pagination (cap page size),
row-level actions, bulk actions (confirm when destructive), `—` fallback for
empty cells, no-results state (distinct from empty state: "no matches for
'x' — clear filters"), skeleton, error + retry.

**Detail page:** back link or breadcrumb, title + status badge + primary
actions, metadata block, content sections/tabs, related or next-step module,
not-found handling for deleted/foreign records.

**Form page:** labeled fields with required marks and helper text, validate
on blur + on submit, error summary anchored at top on failed submit,
unsaved-changes guard on navigation, submit disabled + spinner while
pending, success feedback + sensible redirect, Enter submits.

**Settings:** grouped sections with their own save semantics (auto-save vs
explicit save button — pick one per section, never mix silently), destructive
zone at the bottom (delete account/data with type-to-confirm), cancel/revert
on dirty forms.

**Checkout/payment:** step indicator, sticky order summary, validated
payment fields, error recovery WITHOUT data loss, trust signals (secure
badge, refund line), confirmation screen with reference number + email
confirmation.

**Profile:** avatar upload (size/type validated, preview before save),
display fields, privacy/visibility controls where relevant, save feedback.

**Search/results:** echoed query, result count, applied-filters chips with
clear-all, no-results suggestions, deep-linkable query state (URL params).

**Error pages:** 404 (search/home CTA), 403 (plain reason + request-access
path), 500 (retry + report link) — all branded with the app's nav so users
are never stranded.

## Anti-bloat governor

Anatomy is completeness, not over-engineering. Scale the FLAVOR to the
project, never drop the ORGAN: a weekend MVP still has error pages, empty
states, and loading skeletons — it may use a single theme and simple toasts
instead of a notification center. The three organs that never scale away:
the 4-state matrix, error pages, and destructive-action confirmation.

## Response format

1. **🫀 Page-type map** — which anatomies apply to this project.
2. **📋 Anatomy checklist** — element / status / note per page type
   (merged into `nrfs/checklist.md`).
3. **🎨 Anatomy-aware design** — the design protocol (reference 04) applies
   on top of the anatomy, not instead of it.
4. **💻 Complete implementation** — pages built with every organ present.
