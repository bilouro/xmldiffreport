# Contribuir

Contribuições são bem-vindas — bugs, novas recipes, docs e código.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Verificações (antes de um PR)

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Ou instala os hooks uma vez: `pre-commit install`.

## Adicionar uma recipe

1. Coloca um `<nome>.toml` em `src/xmldiffreport/recipes/`.
2. Declara a `key` natural por elemento, `ignore_attrs` e, opcionalmente, `unit`
   — ver [Escrever recipes](guide/recipes.md).
3. Acrescenta um pequeno exemplo **sintético** em `examples/<nome>/` e um teste.

## Adicionar um formato de saída (além de Markdown e HTML)

Os formatos são uma **strategy com registo**, por isso uma saída nova é uma única
classe auto-contida — sem mexer no motor, na CLI nem no harness. Exemplo completo:
um renderer **JSON**.

**1. Cria `src/xmldiffreport/report/json.py`:**

```python
"""JSON renderer."""
from __future__ import annotations

import json

from .base import DiffReport, Renderer, register


@register
class JsonRenderer(Renderer):
    format = "json"             # valor usado por --format / get_renderer
    file_extension = "json"     # usado no nome do ficheiro de saída

    def render(self, report: DiffReport) -> str:
        payload = {
            "generated_at": report.generated_at,
            "recipe": report.recipe_name,
            "sources": report.sources,
            "units": [
                {"id": u.ident, "tag": u.tag, "sources": u.sources}
                for u in report.units
            ],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)
```

**2. Regista-o** importando o módulo pelo *side-effect* em
`src/xmldiffreport/report/__init__.py`:

```python
from . import json as _json  # noqa: F401  (import pelo side-effect do @register)
```

**3. Pronto — fica ligado em todo o lado automaticamente:**

```bash
xmldiffreport examples/controlm -r controlm -f json -o report.json
# o formato também é inferido quando o -o acaba numa extensão conhecida
```

```python
from xmldiffreport.report import list_formats, get_renderer
list_formats()                       # ['html', 'json', 'md']
get_renderer("json").render(report)
```

**4. Acrescenta um teste** (`tests/test_report.py`):

```python
def test_json_output_is_valid():
    import json
    out = _report().render("json")
    data = json.loads(out)                      # tem de fazer parse
    assert data["recipe"] == "controlm"
    assert data["units"]                        # pelo menos uma unidade difere
```

**5. Documenta** — uma linha no README/CHANGELOG e, se justificar, uma nota nas
docs. Mantém o renderer sem dependências (só biblioteca-padrão).

É todo o contrato: herda de `Renderer`, define `format` + `file_extension`,
implementa `render(report: DiffReport) -> str`, e `@register`. O `DiffReport`
traz `units` (uma lista de `NodeDiff`), `sources` (os rótulos = caminhos),
`recipe_name` e `generated_at`. Ver a
[referência API](api/index.md) para a forma do `NodeDiff`.

## Diretrizes

- Mantém o core pequeno e sem dependências (só biblioteca-padrão).
- Prefere exprimir comportamento novo via **recipe** em vez de o codificar.
- Exemplos e testes só com dados **sintéticos** — nunca exports reais.
- Inclui testes para novas funcionalidades e correções.

## Docs

```bash
pip install -e ".[docs]"
mkdocs serve         # pré-visualização em http://127.0.0.1:8000
```

O site é bilingue (Inglês + Português) via `mkdocs-static-i18n`; acrescenta um
`*.pt.md` ao lado de uma página para a traduzir.

As diretrizes completas estão em
[`CONTRIBUTING.md`](https://github.com/bilouro/xmldiffreport/blob/main/CONTRIBUTING.md).
