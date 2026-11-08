#!/usr/bin/env python3
"""Valida padrao_erros.json (formato versao 1). Uso: python3 validar_padrao_erros.py padrao_erros.json"""
import json, sys, datetime

def falha(m):
    print("ERRO:", m); sys.exit(1)

def num(x): return isinstance(x, (int, float)) and not isinstance(x, bool)

try:
    s = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    falha(f"JSON ilegível: {e}")
if s.get("versao") != 1: falha("versao deve ser 1")
try:
    datetime.datetime.fromisoformat(str(s.get("gerado_em", "")).replace("Z", "+00:00"))
except Exception:
    falha("gerado_em inválido")
t = s.get("total")
if not isinstance(t, dict): falha("total ausente")
for k in ("erros", "com_motivo"):
    if not num(t.get(k)) or t[k] < 0: falha(f"total.{k} inválido")
if t["com_motivo"] > t["erros"]: falha("total.com_motivo maior que total.erros")
ds = s.get("disciplinas")
if not isinstance(ds, list) or len(ds) < 5: falha("disciplinas ausente ou incompleta")
soma_e = soma_m = 0
for d in ds:
    if not isinstance(d.get("nome"), str): falha("disciplina sem nome")
    for k in ("erros", "com_motivo"):
        if d.get(k) is not None and not num(d[k]): falha(f"{d['nome']}: {k} inválido")
    soma_e += d.get("erros") or 0
    soma_m += d.get("com_motivo") or 0
    ats = d.get("atividades")
    if not isinstance(ats, list): falha(f"{d['nome']}: atividades ausente")
    if (d.get("erros") or 0) > 0 and not ats: falha(f"{d['nome']}: tem erros mas nenhuma atividade lida")
    soma_at = 0
    for a in ats:
        for k in ("codigo", "assunto"):
            if not isinstance(a.get(k), str) or not a[k]: falha(f"{d['nome']}: atividade sem {k}")
        for k in ("q", "a", "erros"):
            if not num(a.get(k)): falha(f"{a.get('codigo')}: {k} inválido")
        if a["q"] - a["a"] != a["erros"]: falha(f"{a['codigo']}: q-a != erros")
        soma_at += a["erros"]
    if (d.get("erros") or 0) and soma_at != d["erros"]:
        print(f"AVISO: {d['nome']}: soma das atividades ({soma_at}) difere do total da disciplina ({d['erros']})")
if soma_e != t["erros"]: falha(f"soma das disciplinas ({soma_e}) difere de total.erros ({t['erros']})")
if soma_m != t["com_motivo"]: falha(f"soma com_motivo ({soma_m}) difere de total.com_motivo ({t['com_motivo']})")
ms = s.get("motivos")
if not isinstance(ms, list) or not ms: falha("motivos ausente")
if sum(m.get("n", 0) for m in ms) != t["com_motivo"]: falha("soma dos motivos difere de total.com_motivo")
txt = json.dumps(s, ensure_ascii=False).lower()
for proibido in ("@hotmail", "@gmail", "ritchely", "alunos"):
    if proibido in txt: falha(f"conteúdo proibido encontrado: {proibido}")
print(f"OK: padrão de erros válido — {t['erros']} erros, {t['com_motivo']} com motivo, {len(ds)} disciplinas")
