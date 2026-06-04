# Instalação e Quickstart

## Instalar

```bash
pip install xmldiffreport
```

Requer **Python 3.11+** (usa o `tomllib` da biblioteca-padrão). A ferramenta
**não tem dependências de terceiros**.

## O teu primeiro diff

A forma mais simples compara dois ficheiros que já tens — sem opções, sem
conceitos:

```bash
xmldiffreport old.xml new.xml -o report.md
```

Abre o `report.md`: uma **tabela-resumo** de cada elemento que difere, e depois um
**detalhe N-way** — uma coluna por ficheiro. Passa mais ficheiros para mais
colunas. O código de saída é **`1` quando há diferenças** (útil em CI), `0` caso
contrário.

!!! tip "Experimenta sem preparar nada"
    Clonaste o repo? Corre nos exemplos sintéticos incluídos:
    ```bash
    xmldiffreport examples/sitemap/old/sitemap.xml \
                  examples/sitemap/new/sitemap.xml --recipe sitemap
    ```
    A pasta `examples/` vem **no repo**, não no pacote pip.

## Entradas: ficheiros e/ou diretórios

O `xmldiffreport` aceita ficheiros e/ou diretórios como argumentos:

=== "Ficheiros explícitos"

    ```bash
    xmldiffreport a.xml b.xml c.xml --recipe controlm
    ```

=== "Um diretório (recursivo)"

    ```bash
    xmldiffreport ./dump --recipe controlm
    # cada *.xml sob ./dump vira uma fonte, rotulada pelo caminho
    ```

=== "Mistura"

    ```bash
    xmldiffreport baseline.xml ./candidatos --recipe controlm
    ```

Cada ficheiro é uma **fonte**; uma **unidade** (ex. um `SMART_FOLDER` do
Control-M) é reportada quando aparece em **2+ ficheiros** e difere. Guia completo:
[Inputs e organização dos ficheiros](../guide/inputs.md).

## Escolher uma recipe

Uma **recipe** ensina o motor sobre um dialecto XML. Embutidas:

- `--recipe controlm` — exports BMC Control-M.
- `--recipe sitemap` — `sitemap.xml`.
- `--recipe generic` — sem conhecimento de dialecto (a omissão).

Também podes passar o caminho para o teu próprio `.toml` — ver
[Escrever recipes](../guide/recipes.md).

## Opções da CLI

```text
xmldiffreport [paths...] [-r RECIPE] [-o OUT] [-f FORMAT]

  paths             ficheiros .xml e/ou diretórios (diretórios varridos recursivamente)
  -r, --recipe      nome de recipe embutida ou caminho .toml (default: generic)
  -o, --out         ficheiro de saída (default: reports/YYYYMMDD_HH_MM.<ext>)
  -f, --format      formato de saída: md (default) ou html
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
