# Harness de uso

O repositório separa a **ferramenta** do **teu uso**:

```
src/xmldiffreport/   a ferramenta instalável (motor, recipes, CLI) — genérica
usage/               um harness guiado por config para correr nos TEUS ficheiros
```

A ferramenta em `src/` não sabe nada das tuas pastas. A pasta `usage/` é a fina
camada que adaptas.

## Configurar

```bash
cp usage/config.example.toml usage/config.toml
```

```toml
# usage/config.toml  (caminhos relativos a ESTE ficheiro)
recipe = "controlm"
report_dir = "reports"
format = "md"            # "md" ou "html"
# applied_env = "prod"   # opcional

[environments]
uat   = "/data/ctm/uat"      # ex.: onde descarregas os anexos do Jira
bench = "/data/ctm/bench"
prod  = "/data/ctm/prod"
```

## Correr

```bash
python usage/collect.py
# escreve usage/reports/YYYYMMDD_HH_MM.<ext>
```

O `collect.py` recolhe todos os `*.xml` de cada pasta de ambiente, corre o diff e
escreve um relatório com timestamp em `report_dir`. Código de saída `1` se houver
conflito.

## Um fluxo Control-M típico

1. Cada patch (um JIRA) leva os `SMART_FOLDER` alterados como anexo XML.
2. Descarregas os anexos para pastas por ambiente (`uat/`, `bench/`, …); `prod/`
   tem os recentemente aplicados.
3. Corres o `collect.py` antes de promover um patch.
4. Lês o relatório:
    - **⚠️ CONFLICT** — dois patches pendentes tocam no mesmo folder/job →
      resolve antes de promover.
    - **ℹ️ INFO** — um patch pendente sobrepõe-se a algo já em `prod` → confirma
      que partiu do estado atual de produção.

## Privacidade

`usage/config.toml`, `usage/reports/` e qualquer `*.xml` colocado sob `usage/`
estão **fora do git** — os teus caminhos e dados reais nunca são commitados.
