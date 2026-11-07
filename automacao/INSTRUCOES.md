# Atualização do guruja.json (rotina automática do RITY OS)

Esta rotina lê o Guruja (conector MCP, somente leitura) e grava **um único arquivo**, `guruja.json`, na raiz do
repositório. O app (`index.html`) lê esse arquivo ao abrir. **Nunca altere `index.html`** nem outro arquivo além de
`guruja.json`.

## Regras do conector Guruja (obrigatórias)
- Nunca escreva, estime ou insinue quantos alunos existem na plataforma ou na grade.
- Nunca inclua informação de metas futuras (só a meta em andamento e as já concluídas que `historico_de_metas` devolver).
- Não inclua nome, e-mail nem qualquer dado pessoal. Só dados de estudo.
- Números da turma entram somente como mediana/média agregada (campos `media`, `mediana`, `mediana_*`).

## Passo a passo
1. Carregue as ferramentas: ToolSearch com
   `select:mcp__Guruja__historico_de_metas,mcp__Guruja__detalhe_de_uma_meta,mcp__Guruja__meu_desempenho_por_disciplina,mcp__Guruja__meu_desempenho_comparativo,mcp__Guruja__meu_tempo_de_estudo,mcp__Guruja__contexto_do_planejamento,mcp__Guruja__meus_pontos_fracos`
2. Chame `historico_de_metas`. Identifique a meta com `esta_em_andamento=true` (meta atual).
3. Chame `detalhe_de_uma_meta` da meta atual e das **2 metas concluídas mais recentes** (3 metas no total).
   As metas mais antigas entram só com os totais (sem `atividades`/`reforcos`).
4. Chame `meu_desempenho_por_disciplina`, `meu_desempenho_comparativo`, `meu_tempo_de_estudo`,
   `contexto_do_planejamento` e `meus_pontos_fracos` (limite 10, minimo_questoes 5).
5. Monte o JSON abaixo, **copiando os números exatamente** (sem arredondar, sem inventar). Se um dado não existir, use `null`.
6. Salve em `guruja.json` (UTF-8, indentação de 1 espaço está ok) e rode `python3 automacao/validar_snapshot.py guruja.json`.
   Se o validador falhar, **corrija** o JSON e rode de novo. Não faça commit enquanto não passar.
7. `git add guruja.json && git commit -m "Guruja: snapshot AAAA-MM-DD HH:MM" && git push origin HEAD:main`.
   Se `git push` for rejeitado por divergência: `git fetch origin main && git rebase origin/main` e tente de novo (uma vez).
8. Relate em 3 linhas: gerado_em, meta atual (n, concluídas/total) e se o push foi OK.

## Formato (versao 1)
```json
{
 "versao": 1,
 "gerado_em": "2026-11-07T11:46:33Z",
 "origem": "tarefa agendada",
 "planejamento_id": 100470,
 "meta_atual": {"ordem": 4, "target_id": 0, "data_inicio": "2026-11-02T06:46:42", "dias_atraso": 0, "vezes_adiada": 0,
   "status": "ontime", "atividades_totais": 32, "atividades_concluidas": 8, "atividades_pendentes": 24,
   "atividades_ignoradas": 0, "questoes": 128, "acertos": 115, "minutos": 590},
 "metas": [
  {"ordem": 4, "target_id": 0, "concluida": false, "data_inicio": "...", "data_conclusao": null,
   "atividades_totais": 32, "atividades_concluidas": 8, "atividades_ignoradas": 0,
   "questoes": 128, "acertos": 115, "minutos": 590,
   "atividades": [
    {"aid": 130777, "taid": 25901761, "codigo": "AFO.4654.130777", "titulo": "LRF - PARTE II ...", "disciplina": "AFO e Direito Financeiro",
     "tipo": "Questões", "rel": 5, "prio": "Indispensável", "q": 20, "a": 16, "min": 90,
     "concluida": true, "ignorada": false, "link": "https://www.tecconcursos.com.br/s/Q79fdr"}
   ],
   "reforcos": [
    {"aid": 125332, "titulo": "PPA e LDO", "disciplina": "AFO e Direito Financeiro", "tipo_reforco": "Easy",
     "concluido": true, "ignorado": false, "q": 22, "a": 19, "min": 30, "link": "https://www.tecconcursos.com.br/s/Q6zhuF"}
   ]}
 ],
 "desempenho": [
  {"sigla": "DPREV", "disciplina": "Direito Previdenciário", "peso": 11.9, "q": 149, "a": 124, "pct": 83.22,
   "media": 76.14, "mediana": 75.0, "decil": 9, "tendencia": "estavel"}
 ],
 "tempo": {"total_min": 5660, "por_tipo": {"Questões": 4800, "Teoria": 290, "Teste": 210, "Lei Seca": 180, "Revisão": 0},
   "reforcos_min": 90, "aprofundamentos_min": 90, "disciplinas": [{"sigla": "TINFO", "min": 810}]},
 "ritmo": {"meu_ritmo": "no_ritmo", "meus_dias_por_meta": 7, "mediana_dias_por_meta": 7, "dias_atraso": 0,
   "decil_progresso": 8, "meus_min_por_meta": 1690, "mediana_min_por_meta": 1160,
   "minhas_q_por_meta": 363, "mediana_q_por_meta": 490},
 "fracos": [{"titulo": "Ética no setor público", "sigla": "ETICA", "q": 10, "a": 7, "pct": 70.0, "media": 79.0, "link": "https://..."}],
 "dificeis_turma": ["DPREV", "RLOG", "ESTAT"]
}
```
### Campos
- `aid` = `activity_id` do Guruja (é o que o app usa para casar com o plano). `taid` = `target_activity_id`.
- `sigla` de cada atividade = prefixo de `codigo` (ex.: `AFO.4654.130777` → `AFO`). Em `desempenho`, use a `sigla` devolvida pelo conector.
- `tendencia`: `estavel`, `melhorando`, `piorando` ou `null`. `decil` é o número (`decil_9` → 9).
- `ritmo.decil_progresso`: número (`decil_8` → 8).
- Transcreva TODAS as atividades e reforços das 3 metas detalhadas, inclusive as pendentes e as ignoradas.
