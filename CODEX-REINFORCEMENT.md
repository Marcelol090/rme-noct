# Codex Reinforcement Input — rme-noct

---

## Regras de reforço

### R1 — Sempre ler o repositório local e origin antes de qualquer implementação

```bash
# Sincronizar com origin antes de qualquer trabalho
git fetch origin
git status
git log --oneline -10

# Verificar divergência entre local e origin
git diff HEAD origin/main --stat

# Repositório de referência oficial
# https://github.com/karolak6612/remeres-map-editor-redux
```

**Nunca implementar sem verificar o estado atual do origin.**
Se o branch local estiver atrás do origin → `git pull --rebase` antes de começar.

---

### R2 — Usar o plugin GitHub do Codex para todas as operações de repositório

O plugin GitHub está ativo com as seguintes skills — usar sempre pelo nome correto:

| Skill | Função | Quando usar |
|---|---|---|
| **Publish Changes** | Commit + push + abrir PR | Após gate de verificação aprovado |
| **CI Debug** | Inspecionar e corrigir GitHub Actions | Quando CI falhar após push |
| **Review Follow-up** | Endereçar feedback acionável do PR | Quando PR receber review comments |
| **GitHub** | Inspecionar PRs, issues, CI e publish flows | Consulta de estado do repositório |

```
# Invocar as skills pelo nome exato do plugin
use_skill("publish-changes")       → commit + push + PR
use_skill("ci-debug")              → debug Actions quebrado
use_skill("review-follow-up")      → address PR review comments
use_skill("github")                → inspecionar estado do repo/PR/issues
```

**Sequência padrão de fechamento de slice:**
```
1. gate de verificação aprovado (pytest + ruff + mypy + preflight)
2. use_skill("publish-changes")     → abre PR
3. use_skill("ci-debug")            → se CI vermelho
4. use_skill("review-follow-up")    → se PR receber comments
5. gh pr merge --squash             → após CI verde + review aprovado
```

---

### R3 — gh auth obrigatório antes de qualquer operação GitHub

```bash
# Verificar antes de qualquer publish-changes
gh auth status

# Se falhar → autenticar
gh auth login
# Escolher: GitHub.com → HTTPS → Browser
```

**Nunca chamar `publish-changes` sem auth verde.**
Se auth falhar → reautenticar no browser e repetir o comando.

---

### R4 — Commits separados por escopo — nunca commit monolítico

GSD exige commits por milestone/slice. Sempre separar:

```bash
# Verificar o que está staged antes de commitar
git diff --cached --stat

# Nunca git add -A — sempre stage seletivo por escopo
git add <arquivos do escopo M###>
git diff --cached --stat
git commit -m "feat(M###/S##): one-liner do summary"

# Formato obrigatório GSD
# {type}(M###/S##): {one-liner}
# Tipos: feat | fix | test | refactor | docs | perf | chore
```

**Cada milestone tem seu commit. Nunca misturar M003 + M004 em um único commit.**

---

### R5 — PR body deve usar resultados reais de teste — nunca hardcodar

```bash
# Capturar resultado real antes de publish-changes
pytest_result="$(python3 -m pytest tests/python/ -q 2>&1 | tail -n 3)"

# Criar .tmp-pr-body.md com resultado real
cat > .tmp-pr-body.md <<EOF
## Summary
<descrever o que o PR fecha>

## Verification
$pytest_result

## Changes
<listar arquivos e o que mudou>
EOF

# Passar para publish-changes ou fallback gh pr create
gh pr create --draft --base main --body-file .tmp-pr-body.md
```

---

### R6 — Squash merge só após CI verde — nunca antes

```bash
# Aguardar CI completar antes de merge
gh pr checks --watch

# Só após CI verde:
gh pr merge --squash --delete-branch \
  --subject "{type}(M###-M###): {slice title}" \
  --body "{descrição concisa do que foi fechado}"

# Verificar main após merge
git checkout main
git pull origin main
git log --oneline -5
```

---

### R7 — Abrir próximo milestone como planning limpo — nunca implementar no closeout

```bash
# Após merge confirmado:
git checkout -b gsd/M005/S01

# Criar estrutura
mkdir -p .gsd/milestones/M005/slices/S01/tasks

# Atualizar STATE.md com fase Planning
# Criar S01-PLAN.md antes de qualquer código

# NUNCA iniciar implementação no mesmo closeout do milestone anterior
```

---

## Resumo das regras em uma linha cada

```
R1 → Ler local e origin antes de implementar. Repo: github.com/karolak6612/remeres-map-editor-redux
R2 → Usar plugin GitHub: publish-changes | ci-debug | review-follow-up | github
R3 → gh auth status antes de qualquer publish-changes. Sem auth → sem PR.
R4 → Stage seletivo por escopo. Nunca git add -A. Commit por milestone.
R5 → PR body com $pytest_result real. Nunca hardcodar contagem de testes.
R6 → gh pr checks --watch antes do squash merge. CI verde obrigatório.
R7 → Próximo milestone começa como planning. Nunca implementar no closeout.
```


---

## Superpowers — Basic Workflow obrigatório

O Codex DEVE seguir este workflow em ordem. Cada skill ativa em um momento específico.
Nunca pular etapas. Nunca implementar sem design aprovado. Nunca mergear sem finishing.

---

### SP1 — brainstorming
**Ativa:** antes de escrever qualquer código.

```
use_skill("brainstorming")
```

- Refina ideias brutas através de perguntas
- Explora alternativas de design
- Apresenta design em seções para validação
- Salva documento de design antes de avançar

**Gate:** design aprovado pelo usuário → só então avançar para SP2.

---

### SP2 — using-git-worktrees
**Ativa:** após aprovação do design.

```
use_skill("using-git-worktrees")
```

- Cria workspace isolado em branch novo
- Roda setup do projeto no worktree
- Verifica baseline de testes limpo antes de implementar

**Gate:** worktree criado + testes baseline passando → avançar para SP3.

```bash
# Verificar baseline antes de avançar
python3 -m pytest tests/python/ -q
# Deve passar sem falhas no baseline
```

---

### SP3 — writing-plans
**Ativa:** com design aprovado.

```
use_skill("writing-plans")
```

- Quebra o trabalho em tasks de 2-5 minutos cada
- Cada task tem: paths exatos de arquivo, código completo, steps de verificação
- Salva plano antes de qualquer implementação

**Formato de task obrigatório:**
```
Task T##:
  Arquivo: pyrme/caminho/exato/arquivo.py
  O que fazer: descrição precisa
  Código: snippet completo, sem stubs
  Verificação: comando exato para confirmar que funciona
```

**Gate:** plano escrito e revisado → avançar para SP4.

---

### SP4 — subagent-driven-development ou executing-plans
**Ativa:** com plano aprovado.

```
use_skill("subagent-driven-development")
# ou
use_skill("executing-plans")
```

**subagent-driven-development:** despacha subagente fresco por task com dois estágios de review:
1. Conformidade com spec
2. Qualidade de código

**executing-plans:** executa em batches com checkpoints humanos entre cada batch.

**Regra:** usar `subagent-driven-development` para tasks complexas ou com dependências.
Usar `executing-plans` para tasks simples e sequenciais.

**Gate:** cada task passa pelos dois estágios de review antes do próximo começar.

---

### SP5 — test-driven-development
**Ativa:** durante implementação — em cada task.

```
use_skill("test-driven-development")
```

Ciclo obrigatório RED-GREEN-REFACTOR:

```
1. RED   → escrever teste que falha
           python3 -m pytest <test_file> -q → deve FALHAR

2. GREEN → escrever código mínimo para passar
           python3 -m pytest <test_file> -q → deve PASSAR

3. REFACTOR → limpar código sem quebrar teste
              python3 -m pytest <test_file> -q → ainda PASSA

4. COMMIT → só após RED-GREEN-REFACTOR completo
```

**CRÍTICO: qualquer código escrito antes do teste deve ser deletado.**
Não há exceção para esta regra.

---

### SP6 — requesting-code-review
**Ativa:** entre tasks — após cada task concluída.

```
use_skill("requesting-code-review")
```

- Revisa implementação contra o plano
- Reporta issues por severidade:
  - **Critical** → bloqueia o próximo task, corrigir agora
  - **Major** → corrigir antes do finishing
  - **Minor** → registrar, corrigir no refactor

**Gate:** zero issues Critical → avançar para próximo task.
Issues Major/Minor → registrar em `S##-CONTEXT.md` antes de avançar.

---

### SP7 — finishing-a-development-branch
**Ativa:** quando todos os tasks do slice estão completos.

```
use_skill("finishing-a-development-branch")
```

- Verifica suite completa de testes
- Apresenta opções: merge / PR / keep / discard
- Limpa worktree após decisão

**Sequência após finishing:**
```
1. finishing-a-development-branch → verifica + opções
2. use_skill("publish-changes")   → commit + push + PR (plugin GitHub)
3. use_skill("ci-debug")          → se CI vermelho
4. use_skill("review-follow-up")  → se PR receber comments
5. gh pr merge --squash           → após CI verde + review aprovado
6. Abrir próximo milestone como planning limpo
```

---

## Fluxo completo integrado — Superpowers + GSD + GitHub plugin

```
[GSD]         Ler STATE.md → identificar slice ativa
      ↓
[SP1]         brainstorming → design aprovado
      ↓
[SP2]         using-git-worktrees → worktree + baseline limpo
      ↓
[SP3]         writing-plans → plano com tasks 2-5min cada
      ↓
[SP4]         subagent-driven-development ou executing-plans
      ↓
[SP5]         test-driven-development → RED-GREEN-REFACTOR por task
      ↓
[SP6]         requesting-code-review → entre cada task
      ↓
[GSD]         T##-SUMMARY.md → marcar [x] → atualizar STATE.md
      ↓
[SP7]         finishing-a-development-branch → verificação final
      ↓
[GitHub]      publish-changes → PR aberto
      ↓
[GitHub]      ci-debug (se necessário) → review-follow-up (se necessário)
      ↓
[GitHub]      squash merge após CI verde
      ↓
[GSD]         abrir próximo milestone como planning limpo
```

---

## Regras de reforço Superpowers adicionadas

```
SP1 → brainstorming antes de qualquer código. Design aprovado = gate obrigatório.
SP2 → using-git-worktrees após design. Baseline limpo = gate obrigatório.
SP3 → writing-plans com tasks de 2-5min. Paths exatos + código completo.
SP4 → subagent-driven-development para complexo. executing-plans para sequencial.
SP5 → TDD obrigatório: RED primeiro. Código antes de teste = deletar.
SP6 → requesting-code-review entre tasks. Critical bloqueia. Sem exceção.
SP7 → finishing-a-development-branch antes de publish-changes. Sempre.
```
