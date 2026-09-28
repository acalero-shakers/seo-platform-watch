#!/usr/bin/env python3
"""Platform Watch ledger: ingest, deduplicate and triage platform-change alerts.

Why: a weekly digest that leaves no trace evaporates, and dumping every headline
into a skill turns it into a graveyard of stale rules. This keeps a ledger with
state and traceability so that (a) nothing is lost, (b) nothing is duplicated,
and (c) you can audit what entered a skill, where, and when it expires.

Usage:
  radar.py alta <file.jsonl>          ingest new items (dedupes on title+URL hash)
  radar.py listar [state]             list items, optionally by state
  radar.py marcar <id> <state> [note] [skill] [section] [days] [review_date]
  radar.py caducadas [days]           incorporated entries due for review
  radar.py stats                      counts by state and category

Ledger location: $RADAR_DIR/ledger.jsonl (default ~/.hermes/radar).
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(os.environ.get("RADAR_DIR", Path.home() / ".hermes" / "radar")).expanduser()
LEDGER = BASE / "ledger.jsonl"
ESTADOS = ("nuevo", "accion", "conocimiento", "vigilar", "descartado", "incorporado")


def hoy():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def leer():
    if not LEDGER.is_file():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def escribir(regs):
    BASE.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in regs),
                      encoding="utf-8")


def clave_id(titulo, url):
    raw = f"{(titulo or '').strip().lower()}|{(url or '').strip()}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def alta(fichero):
    regs = leer()
    vistos = {r["id"] for r in regs}
    nuevos = []
    for line in Path(fichero).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            it = json.loads(line)
        except Exception:
            continue
        i = clave_id(it.get("titulo"), it.get("url"))
        if i in vistos:
            continue
        nuevos.append({
            "id": i,
            "fecha_deteccion": it.get("fecha") or hoy(),
            "titulo": it.get("titulo"),
            "url": it.get("url"),
            "categoria": it.get("categoria", "aviso_oficial"),
            "resumen": it.get("resumen"),
            "fuente": it.get("fuente"),
            "estado": "nuevo",
            "skill": None,
            "seccion": None,
            "fecha_incorporacion": None,
            "revisar_el": None,
            "nota": None,
        })
        vistos.add(i)
    escribir(regs + nuevos)
    print(f"  ingested: {len(nuevos)} new, {len(regs)} already known")
    for n in nuevos:
        print(f"    [{n['id']}] {(n['titulo'] or '')[:70]}")


def marcar(rid, estado, nota=None, skill=None, seccion=None, revisar_dias=90,
           revisar_el=None):
    if estado not in ESTADOS:
        sys.exit(f"invalid state: {estado} (use {'|'.join(ESTADOS)})")
    regs = leer()
    for r in regs:
        if r["id"] == rid:
            r["estado"] = estado
            if nota:
                r["nota"] = nota
            if estado == "incorporado":
                r["skill"] = skill
                r["seccion"] = seccion
                r["fecha_incorporacion"] = hoy()
                # explicit date (e.g. end of a rollout) or +N days
                r["revisar_el"] = revisar_el or (
                    datetime.now(timezone.utc) + timedelta(days=revisar_dias)
                ).strftime("%Y-%m-%d")
            escribir(regs)
            print(f"  [{rid}] -> {estado}"
                  + (f" (skill {skill}, review {r['revisar_el']})"
                     if estado == "incorporado" else ""))
            return
    sys.exit(f"no such id: {rid}")


def listar(estado=None):
    for r in leer():
        if estado and r["estado"] != estado:
            continue
        print(f"  [{r['id']}] {r['estado']:13} {r['fecha_deteccion']} "
              f"{(r.get('titulo') or '')[:64]}")


def caducadas(dias=0):
    limite = datetime.now(timezone.utc) + timedelta(days=dias)
    for r in leer():
        rev = r.get("revisar_el")
        if not rev:
            continue
        try:
            cuando = datetime.strptime(rev, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if cuando <= limite:
            print(f"  [{r['id']}] review before {rev} · {r.get('skill')} · "
                  f"{(r.get('titulo') or '')[:55]}")


def stats():
    from collections import Counter
    regs = leer()
    print("  by state:", dict(Counter(r["estado"] for r in regs)))
    print("  by category:", dict(Counter(r.get("categoria") for r in regs)))
    print("  total:", len(regs))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "alta":
        alta(sys.argv[2])
    elif cmd == "listar":
        listar(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "marcar":
        marcar(sys.argv[2], sys.argv[3],
               sys.argv[4] if len(sys.argv) > 4 else None,
               sys.argv[5] if len(sys.argv) > 5 else None,
               sys.argv[6] if len(sys.argv) > 6 else None,
               revisar_dias=int(sys.argv[7]) if len(sys.argv) > 7 else 90,
               revisar_el=sys.argv[8] if len(sys.argv) > 8 else None)
    elif cmd == "caducadas":
        caducadas(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    elif cmd == "stats":
        stats()
    else:
        print(__doc__)
