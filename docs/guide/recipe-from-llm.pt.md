# Gerar uma recipe com um LLM

Escrever uma recipe à mão é simples quando conheces a
[mini-linguagem de chaves](recipes.md), mas podes deixar um modelo de linguagem
fazer a primeira versão: colas um prompt seguido de uma amostra do teu XML e o
modelo devolve uma recipe `.toml` pronta a usar.

## Caminho rápido: `xmldiffreport-recipe scaffold`

O package traz um prompt validado e um helper que lhe injecta o teu XML:

```bash
xmldiffreport-recipe scaffold sample.xml > prompt.txt
```

O `prompt.txt` passa a conter as instruções completas **mais o teu XML** — cola
num LLM capaz (ChatGPT, Gemini, …) e ele devolve a recipe. Ficheiro grande? Basta
um excerto representativo; usa `--max-bytes` para limitar o que é injectado:

```bash
xmldiffreport-recipe scaffold sample.xml --max-bytes 8000 > prompt.txt
```

Sem ficheiro, imprime só o prompt, para colares o XML tu mesmo:

```bash
xmldiffreport-recipe scaffold
```

## O que o prompt pede ao modelo

- `defaults.unit` — o contentor repetido que representa uma unidade lógica de mudança.
- `[elements.<TAG>] key` — a identidade natural por elemento, usando a
  [mini-linguagem de chaves](recipes.md#the-key-mini-language).
- `defaults.ignore_attrs` — atributos voláteis (versões, timestamps, ids,
  utilizador/host, contadores).
- `inline = true` — elementos cujo significado está nos filhos.

O modelo é instruído a devolver **apenas** uma recipe TOML e a nunca inventar
atributos que não estejam na amostra.

## Validar o resultado: `xmldiffreport-recipe validate`

Verifica sempre o ficheiro gerado antes de confiar nele:

```bash
xmldiffreport-recipe validate my-dialect.toml
# ✓ my-dialect.toml: valid recipe        (exit 0)
# ✗ my-dialect.toml: 2 problem(s)        (exit 1)
#   - [elements.JOB] invalid key token(s): ['JOBNAME']   # devia ser "@JOBNAME"
#   - unknown key in [defaults]: 'unite'
```

O validador não tem dependências e espelha o **JSON Schema** distribuído. Obtém o
schema (ou o seu caminho) diretamente da CLI — sem teres de vasculhar o
`site-packages`:

```bash
xmldiffreport-recipe schema          # imprime o JSON Schema (envia p/ ficheiro / editor / CI)
xmldiffreport-recipe schema --path   # imprime a localização em disco
xmldiffreport-recipe list            # lista as recipes embutidas
xmldiffreport-recipe show controlm   # imprime uma recipe embutida (para ler / copiar)
```

## Depois é só usar

```bash
xmldiffreport ./os-teus-dados --recipe ./my-dialect.toml -o report.md
```

Se funcionar bem, considera contribuí-la como recipe embutida — ver
[Contribuir](../contributing.md).
