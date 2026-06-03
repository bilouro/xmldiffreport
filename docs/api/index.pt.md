# Referência API

O `xmldiffreport` é uma biblioteca pequena e tipada. A superfície pública é
reexportada a partir do package de topo:

```python
from xmldiffreport import load_recipe, parse_xml, diff_sources, render
```

Para escolher o formato de saída programaticamente, usa a factory de renderers:

```python
from xmldiffreport.report import get_renderer, list_formats

list_formats()                      # ['html', 'md']
html = get_renderer("html").render(report)
```

## Motor

::: xmldiffreport.core
    options:
      members:
        - load_recipe
        - parse_xml
        - identity
        - value_attrs
        - diff_group
        - diff_sources
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
