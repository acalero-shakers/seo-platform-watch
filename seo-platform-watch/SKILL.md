---
name: platform-watch
description: Turn platform change alerts into durable, expiring skill knowledge.
version: 1.0.0
license: MIT
metadata:
  tags: [seo, geo, marketing, knowledge-management, agents, skills]
---

# From alert to durable knowledge

## When to use

Whenever a platform change alert arrives — a search-engine update, an ads API
change, a new policy — and you have to decide **what deserves to become a
procedure**. Also useful before an audit or a weekly plan: check the active
register so you don't misread a platform rollout as a site problem.

Golden rule: **a skill is a procedure, not a news archive.** If an alert does not
change what you will do, it does not enter the skill.

## The circuit (4 steps)

```
1. INGEST      weekly digest -> ledger.jsonl        (nothing is lost)
2. TRIAGE      each item    -> action | knowledge | watch | discarded
3. INCORPORATE only "knowledge" -> dated entry in the skill's REGISTER
4. REVIEW      every entry expires -> renewed or retired (prevents rot)
```

Tool: `scripts/radar.py` (`alta | listar | marcar | caducadas | stats`).
The ledger deduplicates by title+URL hash, so re-running an alert changes nothing.

## What counts as knowledge

**Yes, all three must hold:**

1. An **official notice or verifiable technical change** — not a rumour, not an
   opinion, not a blog post's interpretation of a paper.
2. It **changes a procedure**: adds a step, a threshold, a check, a constraint.
3. It can be written as **"if X, then we do Y"**, with a date.

**No** (keep it in the ledger as `watch` or `discarded`, with the reason):

- Brand news, case studies, campaigns, launch announcements.
- Trends without data.
- Inflated headlines: studies or papers the press frames as a ranking change when
  the primary source says otherwise.
- Anything whose only action is "keep an eye on it".

## Verify the primary source before incorporating

A headline is not a source. Check the platform's own documentation, status
dashboard, changelog or the paper itself, and store **the primary URL** — not the
outlet that reported it. If you cannot verify it, it does not become knowledge.

## Register entry format

```markdown
### <short title> · <YYYY-MM-DD of the change>
- What changed: <verifiable fact, with the exact number or scope>
- Source: <primary URL>
- What we do differently: <concrete step / threshold / check>
- Revisit on: <YYYY-MM-DD — end of rollout if known, else +90 days>
- Status: active | superseded | retired
```

Everything incorporated is also marked in the ledger with
`estado=incorporado`, its `skill`, its `seccion` and its `revisar_el`, giving a
trace of what entered, where, and when it expires.

## REGISTER OF ACTIVE CHANGES

### Google spam update, September 2026 · 2026-09-24
- What changed: Google released the September 2026 spam update on 24 Sep at
  09:15 PDT, **globally and in all languages** — the fourth spam update of 2026.
  Google allows a rollout of **up to 14 days** (~8 Oct), far longer than the
  previous three (which closed in 19.5 h, 2 days and 2.7 days). No target, no new
  policy and no affected-query figure were published. Recovery from a penalty is
  measured in **months**.
- Source: Google Search Status Dashboard and the official spam-updates docs
- What we do differently:
  1. **Annotate the window** (24 Sep → 8 Oct) in Search Console / Analytics for
     every project before drawing any traffic conclusion.
  2. **Avoid large structural changes during the rollout** — their effect cannot
     be attributed.
  3. If traffic drops, **review the spam policies** (scaled content, links, site
     reputation abuse) before touching anything else.
  4. When reporting, state the measured data **and the window**. Never "it's the
     update".
- Revisit on: 2026-10-08 (expected end of rollout) → close or renew
- Status: active

### SAFE (Scaled Abuse Forensics Examiner) · 2026-09 (paper)
- What changed: Google published a three-page paper on **SAFE**, a team of agents
  that speeds up forensic investigation of "AI slop" networks. **It announces no
  change to Search**: the paper discusses **YouTube channels**, never mentions
  websites or rankings, and **publishes no results** (the evaluation section is
  written in the future tense).
- Source: the paper itself, plus the critical read at elevarus.com (Aug 2026)
- What we do differently: **nothing yet.** Do not rewrite content strategies over
  this paper. If Google ever ships it as a Search rule, it enters as a new entry.
- Revisit on: +90 days → retire if still not a Search rule
- Status: active (classified as **watch**, not action)

### Generative AI performance report in Search Console, global · 2026-08-31
- What changed: since 31 Aug 2026 the generative-AI performance report is
  available to **all sites** (global rollout confirmed in Search Console help and
  the Search Central blog). It measures **impressions only** on AI surfaces
  (AI Overviews and AI Mode), with page/country/device/date dimensions; it shows
  **no clicks, no CTR and no queries**.
- Source: Search Console help (answer/16984139) and the Search Central blog
- What we do differently:
  1. In every SEO/GEO audit, **open the generative-AI report** and report
     impressions by surface and page.
  2. **Never infer clicks or demand from it** — AI impressions are not traffic.
  3. Keep measuring real demand with Search Console clicks and paid data.
- Revisit on: +90 days
- Status: active

## Monthly anti-rot routine

1. `radar.py caducadas 30` → entries expiring within 30 days.
2. For each: still true? **Renew** the date, or **retire** the entry from the
   register and mark the ledger `discarded` with "retired as expired".
3. `radar.py stats` → if the register keeps growing, the triage filter is too
   soft. Tighten it.

## Pitfalls

- **Confusing an alert with an action.** An official notice with no concrete
  action is `watch`, not knowledge.
- **Swallowing the headline.** Worked example: several outlets presented SAFE as
  part of the spam update and as an AI detector for Search. The primary source
  says YouTube, with no published results. Verify before incorporating.
- **Turning the skill into an archive.** Only lines that change a procedure.
  History lives in the ledger, not in the skill.
- **Never expiring anything.** Policies change; an entry without a review date
  becomes a false rule over time.
- **Duplicating alerts week over week.** The ledger deduplicates by hash — check
  it before writing a new entry.
