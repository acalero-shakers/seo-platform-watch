# seo-platform-watch — an SEO skill that keeps itself current

An [agent skill](https://hermes-agent.nousresearch.com/docs) + dependency-free CLI
for SEO/GEO practitioners. A weekly radar tells you what changed in search
(algorithm and spam updates, Search Console features, AI Overviews / AI Mode
surfaces, ads policies); this converts only the parts that **change a procedure**
into a dated, sourced register inside the skill — with an expiry date, so an old
rule can never quietly become a wrong rule.

Built for the reality of SEO work: the platform moves constantly, and the half-life
of a "best practice" is short.

## The problem

Two failure modes, both quiet:

1. **Alert goes nowhere.** You read Monday's digest, act on nothing, and by Friday
   the detail is gone.
2. **Skill becomes a news archive.** Dump every headline into your notes and your
   skill grows a graveyard of stale rules that later poison real work.

## The circuit (4 steps)

```
1. INGEST    radar digest  -> ledger.jsonl            (nothing is lost)
2. TRIAGE    each item     -> accion | conocimiento | vigilar | descartado
3. INCORPORATE  only "knowledge" -> dated entry in the skill's REGISTER
4. REVIEW    every entry expires -> renewed or retired (no rot)
```

`ledger.jsonl` deduplicates by title+URL hash, so a repeated alert never doubles up.

## What qualifies as knowledge

All three must hold:

1. It is an **official notice or verifiable technical change** — not a rumour, not
   an opinion, not a headline about someone else's blog post.
2. It **changes a procedure**: adds a step, a threshold, a check or a constraint.
3. It can be written as **"if X happens, do Y"** with a date attached.

If the honest action is "keep an eye on it", it stays `vigilar` — it does not enter
the skill. The register is for procedures; history stays in the ledger.

## Worked example: same week, two alerts

Both items arrived in the same weekly digest:

| Alert | Verdict | Why |
|---|---|---|
| September 2026 Google spam update | **knowledge** | Verified in the primary source: global rollout, window of up to 14 days, months to recover → enters with concrete actions (annotate the window in GSC/GA, avoid structural changes mid-rollout) |
| SAFE ("AI slop" forensics paper) | **watch** | The paper describes YouTube channel networks, never mentions Search or rankings, and publishes no results. Headlines claimed a new Search detector; the source does not |

That distinction is the whole point: noise stays out, and the real notice enters
with the action glued to it.

## Install

Copy the skill into your agent's skills directory:

```bash
mkdir -p ~/.hermes/skills/research
git clone <this-repo> ~/.hermes/skills/research/seo-platform-watch
```

The CLI is dependency-free Python 3.9+:

```bash
export RADAR_DIR=~/.hermes/radar          # defaults to ~/.hermes/radar
python3 scripts/radar.py alta  items/2026-01-01.jsonl
python3 seo-platform-watch/scripts/radar.py listar nuevo
python3 seo-platform-watch/scripts/radar.py marcar <id> incorporado "why" my-skill "REGISTER"
python3 seo-platform-watch/scripts/radar.py caducadas 30
python3 seo-platform-watch/scripts/radar.py stats
```

## Ledger item format

One JSON object per line, per published alert:

```json
{
  "titulo": "September 2026 spam update (global, rollout up to 14 days)",
  "url": "https://developers.google.com/search/updates/spam-updates",
  "categoria": "aviso_oficial",
  "fuente": "Google Search Status Dashboard",
  "resumen": "One sentence with the concrete fact.",
  "fecha": "2026-09-24"
}
```

`fecha` is the date of the **change**, not the date you read about it.

## Register entry format

```markdown
### <short title> · <YYYY-MM-DD of the change>
- What changed: <verifiable fact, with the exact number or scope>
- Source: <primary URL>
- What we do differently: <concrete step / threshold / check>
- Revisit on: <YYYY-MM-DD — end of rollout if known, else +90 days>
- Status: active | superseded | retired
```

## Hard rules baked in

1. **Append only.** Never rewrite existing prescriptions — agents are good at
   "improving" text and bad at knowing which instruction someone depends on.
2. **No entry without a verified primary source.** A headline is not a source.
3. **"Keep an eye on it" is not knowledge.** It is `vigilar`.
4. **Every entry expires.** A rule with no review date becomes a false rule.

## Automating it

The circuit is designed to run as two scheduled agent jobs:

- **Weekly digest** — filters the raw feed, publishes the report, and writes the
  week's items to `items/<date>.jsonl`, then runs `radar.py alta`.
- **Weekly triage** (30 min later) — verifies each new item against its primary
  source, decides the state, appends register entries, and marks the ledger.
  On the first Monday of the month it also runs `radar.py caducadas 30` and
  renews or retires expired entries.

Prompts for both jobs are in [`examples/`](examples/).

## License

MIT — see [LICENSE](LICENSE).
