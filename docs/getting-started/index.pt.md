# Instalação e Quickstart

## Instalar

```bash
pip install xmldiffreport
```

Requer **Python 3.11+** (usa o `tomllib` da biblioteca-padrão). A ferramenta
**não tem dependências de terceiros**.

## O teu primeiro diff

O repositório traz exemplos sintéticos que podes correr de imediato:

```bash
# Uma pasta cujas subpastas são ambientes (test/ uat/ bench/ prod/)
xmldiffreport examples/controlm --recipe controlm -o report.md
```

Abre o `report.md`: uma **tabela-resumo** de cada unidade que difere, e depois um
**detalhe N-way** por elemento — uma coluna por ficheiro.

O código de saída do processo é **`1` quando há conflito** (útil em CI), `0` caso
contrário.

## Formatos de entrada

O `xmldiffreport` aceita ficheiros e/ou pastas como argumentos:

=== "Ambientes em subpastas"

    ```bash
    xmldiffreport ./environments --recipe controlm -o report.md
    # environments/uat/*.xml, environments/bench/*.xml, ...
    ```

    Cada subpasta é um **ambiente**; cada `(ambiente, ficheiro)` é uma **fonte**.
    Dois ficheiros no *mesmo* ambiente também são comparados.

=== "Uma única pasta"

    ```bash
    xmldiffreport ./uat --recipe controlm
    # o nome da pasta ("uat") passa a ser o ambiente
    ```

=== "Ficheiros explícitos"

    ```bash
    xmldiffreport a.xml b.xml c.xml --recipe controlm
    ```

## Escolher uma recipe

Uma **recipe** ensina o motor sobre um dialecto XML. Embutidas:

- `--recipe controlm` — exports BMC Control-M.
- `--recipe sitemap` — `sitemap.xml`.
- `--recipe generic` — sem conhecimento de dialecto (a omissão).

Também podes passar o caminho para o teu próprio `.toml` — ver
[Escrever recipes](../guide/recipes.md).

## Opções da CLI

```text
xmldiffreport [paths...] [-r RECIPE] [-o OUT] [-f FORMAT] [--applied-env ENV]

  paths             ficheiros .xml ou pastas (ambientes em subpastas)
  -r, --recipe      nome de recipe embutida ou caminho .toml (default: generic)
  -o, --out         ficheiro de saída (default: reports/YYYYMMDD_HH_MM.<ext>)
  -f, --format      formato de saída: md (default) ou html
  --applied-env     sobrepõe o ambiente "já aplicado" da recipe (→ INFO)
```

## Formatos de saída

O relatório é gerado através de uma *strategy* extensível, por isso o mesmo diff
pode sair em vários formatos:

```bash
xmldiffreport examples/controlm -r controlm -f html -o report.html
# o formato também é inferido pela extensão do -o (.html → html)
```

Formatos embutidos: **`md`** (Markdown, default) e **`html`** (página autónoma,
sem assets externos). Acrescentar mais (ex. JSON) é uma só classe — ver
[Contribuir](../contributing.md).

A seguir: [Como funciona](../guide/how-it-works.md).
