# Harness de uso

O repositório separa a **ferramenta** do **teu uso**:

```
src/xmldiffreport/   a ferramenta instalável (motor, recipes, CLI) — genérica
usage/               um harness guiado por config para correr nos TEUS ficheiros
```

A ferramenta em `src/` não sabe nada das tuas pastas. A pasta `usage/` é a fina
camada que adaptas — útil quando preferes guardar caminhos e opções num ficheiro
em vez de os escrever na linha de comandos.

## Configurar

```bash
cp usage/config.example.toml usage/config.toml
```

```toml
# usage/config.toml  (caminhos relativos a ESTE ficheiro)
recipe = "controlm"
report_dir = "reports"
format = "md"                # ou "html"

# Ficheiros e/ou diretórios a comparar (diretórios são varridos recursivamente).
inputs = [
    "/data/ctm/uat",
    "/data/ctm/bench",
    "/data/ctm/prod",
]
```

## Correr

```bash
python usage/collect.py
# escreve usage/reports/YYYYMMDD_HH_MM.md
```

O `collect.py` recolhe todos os `*.xml` dos `inputs` listados, corre o diff e
escreve um relatório com timestamp em `report_dir`. Código de saída `1` se houver
diferenças.

## Um fluxo Control-M típico

1. Cada patch (um JIRA) leva os `SMART_FOLDER` alterados como anexo XML.
2. Descarregas os anexos para pastas (uma por fonte — ex. `uat/`, `bench/`,
   `prod/`) e listas essas pastas em `inputs`.
3. Corres o `collect.py` antes de promover um patch.
4. O relatório mostra cada folder que aparece em 2+ ficheiros e difere, uma coluna
   por ambiente (o label do diretório pai — os caminhos completos são listados uma
   vez no bloco Sources do topo). Sabes qual fonte é qual, por isso decides o que é
   uma colisão a bloquear e o que é esperado.

## Privacidade

`usage/config.toml`, `usage/reports/` e qualquer `*.xml` colocado sob `usage/`
estão **fora do git** — os teus caminhos e dados reais nunca são commitados.
