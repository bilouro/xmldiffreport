# API Reference

`xmldiffreport` is a small, typed library. The high-level entry point is `diff`:

```python
from xmldiffreport import diff

result = diff(["old.xml", "new.xml"], recipe="sitemap")   # a file, files, or dir(s)
print(result.render())          # Markdown — or result.render("html")
result.units                    # list[NodeDiff] — what differs
bool(result)                    # True if anything differs (handy for exit codes)
```

Lower-level pieces are also re-exported: `load_recipe`, `parse_xml`,
`gather_files`, `diff_sources`, `validate_recipe`. To pick a format by name, use
the renderer factory `get_renderer` / `list_formats`.

## High-level

::: xmldiffreport.diff

## Engine

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

## Report

::: xmldiffreport.report.base
    options:
      members:
        - DiffReport
        - Renderer
        - register
        - get_renderer
        - list_formats
