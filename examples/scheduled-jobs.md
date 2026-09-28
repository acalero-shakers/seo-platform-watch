# Example: the two scheduled jobs

This circuit is meant to run unattended as two agent jobs. Both prompts below are
generic — replace the feed source and the paths.

## Job 1 — weekly digest (Monday 08:00)

Script feeds the job the raw unread items (any RSS/blogwatcher/API output works).

```text
You are a platform-change analyst. Raw material: unread items above.

MANDATORY FILTER — include ONLY:
1) official notices (search engines, ad platforms, LLM providers: algorithm
   updates, new ad features, API changes, policies),
2) new trends WITH data behind them (not opinions),
3) concrete, actionable tactics (a real how-to, not a concept).

EXCLUDE ruthlessly: promotional brand cases, company news, opinions, generic
"X trends to watch" lists. If an item does not change what we do next week, drop it.

Structure: OFFICIAL NOTICES (source + what changed + since when + URL) /
TRENDS WITH DATA (which figure, what it implies) / TACTICS (concrete step + tool) /
ACTION OF THE WEEK (one, concrete).

SECOND DELIVERABLE (mandatory): leave a structured trace so the knowledge does not
evaporate. Write one JSONL line per published alert to
`items/YYYY-MM-DD.jsonl` with: titulo, url (PRIMARY source), categoria
(aviso_oficial|tendencia|tactica|investigacion), fuente, resumen (one sentence with
the concrete fact), fecha (YYYY-MM-DD of the change, not today). Then run:
`python3 scripts/radar.py alta items/YYYY-MM-DD.jsonl`
If the digest is empty, write nothing.
```

## Job 2 — triage into skills (Monday 08:40)

```text
Turn this week's platform alerts into durable knowledge.

STEP 1 — `python3 scripts/radar.py listar nuevo`
If nothing is new, answer only "No new alerts to triage" and stop.

STEP 2 — VERIFY THE PRIMARY SOURCE for every alert (platform docs, status
dashboard, changelog, the paper itself). Headlines exaggerate: check that the
source actually says what the outlet claims. If you cannot verify it, it does NOT
become knowledge.

STEP 3 — decide the state and apply it:
`python3 scripts/radar.py marcar <id> <state> "<note>" [skill] [section] [days] [review_date]`
  - knowledge   → changes a PROCEDURE (adds a step, threshold, check, constraint)
  - action      → something concrete to do this week; report it, do not skill it
  - watch       → relevant but no clear action yet (e.g. a paper with no effect)
  - discarded   → noise, opinion, or a headline the source does not support (say why)
  - incorporated→ ONLY after the skill entry has been written

STEP 4 — for each "knowledge", append an entry to the skill's REGISTER OF ACTIVE
CHANGES using this exact format:
### <short title> · <YYYY-MM-DD of the change>
- What changed: <verifiable fact with the exact scope>
- Source: <primary URL>
- What we do differently: <concrete step / threshold / check>
- Revisit on: <YYYY-MM-DD: end of rollout if known, else +90 days>
- Status: active
HARD RULES: append only, never rewrite or delete existing prescriptions; nothing
enters without a verified primary source; "keep an eye on it" is `watch`, not
knowledge; after writing the entry mark the ledger `incorporado` with the skill,
the section and the review date.

STEP 5 — anti-rot: on the first Monday of the month run
`python3 scripts/radar.py caducadas 30` and, for each due entry, either renew its
review date or retire it from the register (marking the ledger `discarded` with
"retired as expired").

STEP 6 — reply with at most 8 lines: how many alerts, how many became skill
entries (with their titles), how many were discarded and why, and what is pending
review. No filler.
```
