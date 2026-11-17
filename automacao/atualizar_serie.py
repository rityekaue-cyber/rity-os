#!/usr/bin/env python3
"""Atualiza guruja_serie.json (histórico diário do Guruja) a partir de guruja.json.

Uso: python3 automacao/atualizar_serie.py guruja.json guruja_serie.json

Como funciona: o Guruja só informa totais acumulados (sem datas). Este script guarda o total da última leitura
e, a cada leitura nova, soma a DIFERENÇA ao dia em que o estudo aconteceu. Isso dá ao app (aba Dados) questões,
acertos e minutos por matéria e por dia, sem ninguém registrar nada à mão.

Regra do dia: usa o horário de Brasília (UTC-3). Leitura feita antes das 06h da manhã conta para o dia anterior
(a rotina das 04h10 enxerga o que foi estudado ontem). Leitura repetida ou mais antiga que a última é ignorada.
"""
import json, sys, os
from datetime import datetime, timedelta, timezone

def dia_local(gerado_em):
    t = datetime.fromisoformat(gerado_em.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=-3)))
    if t.hour < 6:
        t -= timedelta(days=1)
    return t.strftime('%Y-%m-%d')

def totais(s):
    mat = {}
    for d in s.get('desempenho') or []:
        sg = d.get('sigla')
        if not sg:
            continue
        mat.setdefault(sg, {'q': 0, 'a': 0, 'min': 0})
        mat[sg]['q'] = int(d.get('q') or 0)
        mat[sg]['a'] = int(d.get('a') or 0)
    tempo = s.get('tempo') or {}
    for d in tempo.get('disciplinas') or []:
        sg = d.get('sigla')
        if not sg:
            continue
        mat.setdefault(sg, {'q': 0, 'a': 0, 'min': 0})
        mat[sg]['min'] = int(d.get('min') or 0)
    tipo = {k: int(v or 0) for k, v in (tempo.get('por_tipo') or {}).items()}
    tipo['Reforços'] = int(tempo.get('reforcos_min') or 0)
    tipo['Aprofundamentos'] = int(tempo.get('aprofundamentos_min') or 0)
    ativ = sum(int(m.get('atividades_concluidas') or 0) for m in (s.get('metas') or []))
    return {'mat': mat, 'tipo': tipo, 'atividades': ativ}

def diff(novo, ant):
    out = {'mat': {}, 'tipo': {}, 'atividades': max(0, novo['atividades'] - ant.get('atividades', 0))}
    for sg, v in novo['mat'].items():
        a = (ant.get('mat') or {}).get(sg, {})
        d = {k: max(0, v[k] - int(a.get(k, 0))) for k in ('q', 'a', 'min')}
        if any(d.values()):
            out['mat'][sg] = d
    for k, v in novo['tipo'].items():
        d = max(0, v - int((ant.get('tipo') or {}).get(k, 0)))
        if d:
            out['tipo'][k] = d
    return out

def somar(dst, d):
    dst['atividades'] = dst.get('atividades', 0) + d['atividades']
    for sg, v in d['mat'].items():
        x = dst.setdefault('mat', {}).setdefault(sg, {'q': 0, 'a': 0, 'min': 0})
        for k in ('q', 'a', 'min'):
            x[k] += v[k]
    for k, v in d['tipo'].items():
        dst.setdefault('tipo', {})[k] = dst.get('tipo', {}).get(k, 0) + v

def main(snap_path, serie_path):
    s = json.load(open(snap_path, encoding='utf-8'))
    serie = {'versao': 1, 'planejamento_id': s.get('planejamento_id'), 'ultimo': None, 'dias': {}}
    if os.path.exists(serie_path):
        try:
            serie = json.load(open(serie_path, encoding='utf-8'))
        except Exception:
            pass
    if serie.get('planejamento_id') != s.get('planejamento_id'):
        serie = {'versao': 1, 'planejamento_id': s.get('planejamento_id'), 'ultimo': None, 'dias': {}}
    ult = serie.get('ultimo')
    if ult and ult.get('gerado_em') and ult['gerado_em'] >= s['gerado_em']:
        print('leitura já registrada; nada a fazer')
        return
    novo = totais(s)
    d = diff(novo, ult or {})
    dia = dia_local(s['gerado_em'])
    alvo = serie['dias'].setdefault(dia, {'atividades': 0, 'mat': {}, 'tipo': {}})
    somar(alvo, d)
    serie['ultimo'] = {'gerado_em': s['gerado_em'], **novo}
    serie['dias'] = dict(sorted(serie['dias'].items()))
    json.dump(serie, open(serie_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"ok: dia {dia} · +{sum(v['q'] for v in d['mat'].values())} questões · +{sum(v['min'] for v in d['mat'].values())} min · +{d['atividades']} atividades")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
