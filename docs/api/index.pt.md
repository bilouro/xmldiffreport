# Referência API

O `xmldiffreport` é uma biblioteca pequena e tipada. O ponto de entrada de alto
nível é o `diff`:

```python
from xmldiffreport import diff

result = diff(["old.xml", "new.xml"], recipe="sitemap")   # um ficheiro, vários, ou dir(s)
print(result.render())          # Markdown — ou result.render("html")
result.units                    # list[NodeDiff] — o que difere
bool(result)                    # True se algo difere (útil para exit codes)
```

Peças de baixo nível também são reexportadas: `load_recipe`, `parse_xml`,
`gather_files`, `diff_sources`, `validate_recipe`. Para escolher o formato pelo
nome, usa a factory `get_renderer` / `list_formats`.

## Alto nível

::: xmldiffreport.diff

## Motor

::: xmldiffreport.core
    options:
      members:
        - gather_files
        - load_recipe
        - parse_xml
        - identity
        - value_attrs
        - diff_group
        - diff_sources
        - validate_recipe
        - NodeDiff

## Relatório

::: xmldiffreport.report.base
    options:
      members:
        - DiffReport
        - Renderer
        - register
        - get_renderer
        - list_formats
