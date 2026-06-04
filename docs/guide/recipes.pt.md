# Escrever recipes

Uma **recipe** é um pequeno ficheiro TOML que ensina o motor genérico sobre um
dialecto XML. O motor mantém-se igual; tudo o que é específico do dialecto vive
aqui.

!!! tip "Deixa um LLM rascunhar"
    Podes gerar uma primeira recipe a partir de uma amostra do teu XML — ver
    [Gerar uma recipe com um LLM](recipe-from-llm.md).

## Anatomia

```toml
name = "controlm"

[defaults]
unit = "SMART_FOLDER"           # a unidade de comparação (default: filhos da raiz)
unordered = true                # filhos casados por chave, não por ordem
ignore_attrs = [                # atributos voláteis nunca geram diff
    "VERSION", "JOBISN", "CREATION_TIME", "LAST_UPLOAD", "..."
]

[elements.JOB]
key = ["@JOBNAME"]

[elements.OUTCOND]
key = ["@NAME"]                 # ODATE / SIGN são comparados como atributos

[elements.ON]                   # sem chave clara → sintetiza-se uma
key = ["@CODE", "*kinds"]
inline = true                   # trata os filhos (DOACTION, …) como pseudo-atributos
```

## A mini-linguagem da chave

Uma `key` é uma lista de tokens, juntos por `|`. A primeira combinação não-vazia
identifica o elemento entre os irmãos.

| Token | Significado |
|---|---|
| `@ATTR` | valor do atributo `ATTR` |
| `#text` | o texto do próprio elemento |
| `*tag` | o nome da tag (usar para **singletons** comparados pelo texto) |
| `child:TAG@ATTR` | um atributo de um filho |
| `child:TAG#text` | o texto de um filho (ex. `<loc>` do sitemap) |
| `*kinds` | resumo dos tipos de filhos / ações `DOACTION` (para elementos sem chave como `<ON>`) |

Se uma tag **não** tiver entrada, o motor recorre a `@NAME`, depois `#text`,
depois um composto de todos os atributos.

### Exemplos

```toml
# Uma condição com chave NAME; os outros atributos são comparados
[elements.INCOND]
key = ["@NAME"]                 # ODATE, AND_OR ficam comparáveis

# Um <url> de sitemap identificado pelo texto do filho <loc>
[elements.url]
key = ["child:loc#text"]

# Singletons comparados pelo texto (identidade = a própria tag)
[elements.lastmod]
key = ["*tag"]

# Um <ON STMT="*" CODE="NOTOK"> sem chave estável → CODE + ações
[elements.ON]
key = ["@CODE", "*kinds"]       # ex. "NOTOK|RERUN"
inline = true
```

## Elementos `inline`

Alguns elementos (como o `<ON>` do Control-M) levam o significado nos filhos
(`DOACTION`, `DOMAIL`, `DOOUTPUT`). Marcá-los `inline = true` dobra esses filhos
em pseudo-atributos, por isso uma mudança como *“a ação RERUN foi removida”*
aparece numa só linha em vez de uma sub-secção encaixada.

## Recipes embutidas

=== "controlm"

    Exports BMC Control-M: `DEFTABLE → SMART_FOLDER → JOB → INCOND / OUTCOND /
    QUANTITATIVE / CONTROL / ON`. Unit = `SMART_FOLDER`, com uma lista
    `ignore_attrs` ampla para metadados de versão/criação.

=== "sitemap"

    `sitemap.xml`: unit = `url`, identificado pelo texto do `<loc>`;
    `<lastmod>` / `<priority>` / `<changefreq>` comparados pelo texto.

=== "generic"

    Sem conhecimento de dialecto: as unidades são os filhos da raiz; a identidade
    recorre a `@NAME` / `#text`. É a omissão quando `--recipe` não é passado.

## Usar uma recipe própria

Guarda o teu `.toml` onde quiseres e passa o caminho:

```bash
xmldiffreport ./data --recipe ./meu-dialecto.toml -o report.md
```

Para a contribuir como embutida, coloca-a em `src/xmldiffreport/recipes/` e
acrescenta um exemplo sintético + teste (ver [Contribuir](../contributing.md)).
