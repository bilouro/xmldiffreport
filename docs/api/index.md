# API Reference

`xmldiffreport` is a small, typed library. The public surface is re-exported from
the top-level package:

```python
from xmldiffreport import load_recipe, parse_xml, diff_sources, render
```

To pick an output format programmatically, use the renderer factory:

```python
from xmldiffreport.report import get_renderer, list_formats

list_formats()                      # ['html', 'md']
html = get_renderer("html").render(report)
```

## Engine

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

## Report

::: xmldiffreport.report.base
    options:
      members:
        - DiffReport
        - Renderer
        - register
        - get_renderer
        - list_formats
