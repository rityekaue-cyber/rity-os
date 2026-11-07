#!/usr/bin/env python3
"""Valida o guruja.json antes do commit. Uso: python3 automacao/validar_snapshot.py guruja.json"""
import json, sys, re, datetime
p = sys.argv[1] if len(sys.argv) > 1 else 'guruja.json'
erros = []
def E(m): erros.append(m)
try:
    d = json.load(open(p, encoding='utf-8'))
except Exception as e:
    print('FALHOU: JSON inválido:', e); sys.exit(1)
if d.get('versao') != 1: E('versao deve ser 1')
try:
    t = datetime.datetime.fromisoformat(str(d.get('gerado_em','')).replace('Z','+00:00'))
    if (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() > 6*3600: E('gerado_em com mais de 6 h')
    if (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds() > 300: E('gerado_em no futuro')
except Exception: E('gerado_em inválido')
for k in ('meta_atual','metas','desempenho','tempo','ritmo','fracos'):
    if k not in d: E('falta o campo '+k)
txt = json.dumps(d, ensure_ascii=False).lower()
for proibido in ('alunos','aluno ','@gmail','@hotmail','@outlook','email'):
    if proibido in txt: E('texto proibido no JSON: '+proibido)
if len(txt) > 300000: E('arquivo grande demais (>300 KB)')
ma = d.get('meta_atual') or {}
metas = d.get('metas') or []
ordens = [m.get('ordem') for m in metas]
if len(set(ordens)) != len(ordens): E('metas repetidas')
if ma.get('ordem') not in ordens: E('meta_atual.ordem não está em metas')
detalhadas = 0
for m in metas:
    at = m.get('atividades')
    if at is None: continue
    detalhadas += 1
    o = m.get('ordem')
    if len(at) != m.get('atividades_totais'): E(f'meta {o}: {len(at)} atividades != atividades_totais {m.get("atividades_totais")}')
    c = sum(1 for a in at if a.get('concluida'))
    if c != m.get('atividades_concluidas'): E(f'meta {o}: {c} concluídas != atividades_concluidas {m.get("atividades_concluidas")}')
    ig = sum(1 for a in at if a.get('ignorada'))
    if ig != m.get('atividades_ignoradas'): E(f'meta {o}: {ig} ignoradas != atividades_ignoradas {m.get("atividades_ignoradas")}')
    aids = [a.get('aid') for a in at]
    if len(set(aids)) != len(aids): E(f'meta {o}: aid repetido')
    for a in at:
        for k in ('aid','titulo','tipo','concluida','ignorada'):
            if k not in a: E(f'meta {o}: atividade sem {k}: {a.get("titulo")}')
        if a.get('concluida') and a.get('tipo') == 'Questões' and (a.get('q') is None or a.get('a') is None):
            E(f'meta {o}: concluída de Questões sem q/a: {a.get("titulo")}')
        if a.get('q') is not None and a.get('a') is not None and a['a'] > a['q']: E(f'meta {o}: acertos > questões em {a.get("titulo")}')
    sq = sum((a.get('q') or 0) for a in at if a.get('concluida'))
    if m.get('questoes') is not None and sq > m['questoes']: E(f'meta {o}: soma de q das concluídas ({sq}) > questoes da meta ({m["questoes"]})')
    for r in m.get('reforcos') or []:
        if 'aid' not in r or 'concluido' not in r: E(f'meta {o}: reforço sem aid/concluido')
if detalhadas < 1: E('nenhuma meta detalhada')
dp = d.get('desempenho') or []
if len(dp) < 5: E('desempenho com poucas disciplinas')
for x in dp:
    if x.get('q') is not None and x.get('a') is not None and x['a'] > x['q']: E('desempenho: acertos > questões em '+str(x.get('sigla')))
    if x.get('q') and x.get('pct') is not None and abs(x['a']/x['q']*100 - x['pct']) > 0.6: E('desempenho: pct não bate em '+str(x.get('sigla')))
if erros:
    print('FALHOU:'); [print(' -', e) for e in erros]; sys.exit(1)
print('OK: snapshot válido —', len(metas), 'metas,', detalhadas, 'detalhadas,', len(dp), 'disciplinas, meta atual', ma.get('ordem'), f'{ma.get("atividades_concluidas")}/{ma.get("atividades_totais")}')
