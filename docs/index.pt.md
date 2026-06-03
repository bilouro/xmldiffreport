# xmldiffreport

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "xmldiffreport",
  "alternateName": ["xml diff report", "diff de XML N-way", "diff estrutural de XML"],
  "applicationCategory": "DeveloperApplication",
  "applicationSubCategory": "Ferramenta de diff/comparação de XML",
  "operatingSystem": "Cross-platform",
  "programmingLanguage": "Python",
  "softwareVersion": "0.1.0",
  "license": "https://opensource.org/licenses/MIT",
  "url": "https://bilouro.github.io/xmldiffreport/pt/",
  "downloadUrl": "https://pypi.org/project/xmldiffreport/",
  "codeRepository": "https://github.com/bilouro/xmldiffreport",
  "inLanguage": "pt",
  "description": "Diff estrutural e semântico de XML, N-way, que gera relatórios em Markdown e HTML, guiado por recipes por dialecto (Control-M, sitemaps, e mais).",
  "author": {
    "@type": "Person",
    "name": "Victor Bilouro",
    "url": "https://github.com/bilouro"
  },
  "keywords": "diff xml, comparar xml, diff estrutural, diff semântico, diff n-way, control-m, sitemap, relatório markdown, relatório html, python"
}
</script>

[![PyPI version](https://img.shields.io/pypi/v/xmldiffreport.svg?style=flat-square)](https://pypi.org/project/xmldiffreport/)
[![Python versions](https://img.shields.io/pypi/pyversions/xmldiffreport.svg?style=flat-square)](https://pypi.org/project/xmldiffreport/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://github.com/bilouro/xmldiffreport/blob/main/LICENSE)

**Diff estrutural e semântico de XML, N-way, que produz relatórios em Markdown legíveis — guiado por recipes por dialecto.**

O `xmldiffreport` compara **dois ou mais** ficheiros XML ao mesmo tempo e diz-te
*o que mudou de facto* — elemento a elemento, atributo a atributo — em vez de um
diff de texto linha-a-linha ruidoso. Alinha os elementos por uma **chave natural**
(não pela posição), ignora **atributos voláteis** e escreve um **relatório
Markdown** limpo.

Nasceu para detetar conflitos entre patches de jobs **BMC Control-M** ao longo de
`test → uat → bench → prod`, e generalizou-se num motor guiado por recipes que
funciona com qualquer dialecto XML (exports Control-M, sitemaps, POMs, …).

## Quickstart

```bash
pip install xmldiffreport
```

```bash
# Comparar patches Control-M espalhados por pastas de ambiente
xmldiffreport examples/controlm --recipe controlm -o report.md
```

```python
from xmldiffreport import load_recipe, parse_xml, diff_sources, render

recipe = load_recipe("controlm")
sources = [
    ("uat",   "uat:patch-b.xml",   parse_xml("uat/patch-b.xml")),
    ("bench", "bench:patch-a.xml", parse_xml("bench/patch-a.xml")),
    ("prod",  "prod:hotfix-c.xml", parse_xml("prod/hotfix-c.xml")),
]
print(render(diff_sources(recipe, sources), ["uat", "bench", "prod"], 3, "controlm"))
```

## Porquê não um diff normal?

Um diff de texto sobre XML mente — atributos voláteis (`VERSION`,
`CREATION_TIME`, `JOBISN`), filhos reordenados e a ordem dos atributos criam
falsas diferenças. O `xmldiffreport` é **estrutural**, **N-way** (3+ ficheiros de
uma vez) e gera um relatório pronto a rever.

## Próximos passos

- [Começar](getting-started/index.md) — instalar e correr o primeiro diff.
- [Como funciona](guide/how-it-works.md) — o modelo do motor e as regras de conflito.
- [Escrever recipes](guide/recipes.md) — ensinar-lhe um novo dialecto XML.
- [Harness de uso](guide/usage.md) — correr nas tuas pastas de ambiente.
- [Referência API](api/index.md) — a API da biblioteca.
