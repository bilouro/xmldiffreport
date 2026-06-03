# Como se compara e quando usar cada

O `xmldiffreport` não tenta substituir todas as ferramentas de diff de XML —
ocupa um nicho específico: **N-way, alinhado por chave, guiado por recipe e
report-first**. Esta página é um mapa honesto do panorama para escolheres a
ferramenta certa.

## Num relance

| Ferramenta | Tipo | Vias | Estratégia de match | Saída | Melhor para |
|---|---|---|---|---|---|
| **xmldiffreport** | estrutural | **N (2+)** | chave natural declarada (recipe) | relatório Markdown / HTML | rever o que mudou entre patches/ambientes pendentes |
| `diff` / `git diff` | texto | 2 | linha-a-linha | diff unificado | mudanças de linha em XML já normalizado |
| [`xmldiff`](https://pypi.org/project/xmldiff/) | estrutural | 2 | algorítmico (heurístico) | edit script / XML patched | produzir um *patch* que transforma A em B |
| Altova DiffDog / Oxygen | estrutural (GUI) | 2 | algorítmico + algumas chaves | lado-a-lado interativo | merge visual manual de dois documentos |
| DeltaXML | estrutural | 2 | chaves + heurística | delta XML | empresa, XML orientado a documento, contrato de suporte |
| BMC Control-M compare / AAPI+git | domínio | 2 | específico da ferramenta | GUI / texto | dentro do produto Control-M ou do seu JSON/YAML em git |

## As alternativas, e quando recorrer a elas

### `diff` / `git diff`
Comparação de texto linha-a-linha. **Usa quando** o XML já está canonizado (ordem
de atributos estável, sem campos voláteis) e só queres o delta textual. **Evita
quando** os exports têm atributos voláteis (`VERSION`, timestamps, ids) ou
reordenam filhos — vai reportar ruído que não é mudança real.

### `xmldiff` (Python)
Excelente tree-diff que produz um **edit script** (insert/delete/update/move) ou
um documento patched. **Usa quando** o objetivo é *transformar* um documento
noutro (aplicar um patch). **Limitações para o nosso caso:** só 2-way; casa nós
com o algoritmo dele — não dá para dizer "casa `<JOB>` por `JOBNAME`"; a saída é um
script, não um artefacto de revisão humana.

### Altova DiffDog / Oxygen (GUI)
Diff/merge visual lado-a-lado, maduro e interativo. **Usa quando** está um humano
à frente de dois ficheiros a resolver diferenças à mão, sobretudo XML de
documento/conteúdo misto. **Limitações:** 2-way, GUI (pouco amigo de CI), e
configuras ignores/chaves por sessão em vez de uma recipe reutilizável e
versionada.

### DeltaXML (comercial)
A referência para comparação de XML de documento, com forte matching por
similaridade e chaves configuráveis. **Usa quando** precisas de matching
enterprise de documentos sem chave, contrato de suporte, e comparação 2-way à
escala. **Limitações para o nosso caso:** comercial/licenciado; 2-way; ainda
constróis a tua camada de relatório.

### BMC Control-M (compare interno / Automation API + git)
O Control-M compara *versões* de jobs na UI, e muitas equipas exportam o JSON/YAML
da **Automation API** e fazem `git diff`. **Usa quando** vives dentro do produto
ou adotaste AAPI-as-code. **Limitações:** o compare interno não é uma matriz
folder/job/atributo; o git-diff do JSON/YAML continua a ser linha-a-linha e 2-way.

## Guia de decisão

**Escolhe o `xmldiffreport` quando:**

- Precisas de comparar **3+ ficheiros ao mesmo tempo** (ex. o mesmo folder em
  `uat`, `bench` e `prod`) e ver uma coluna por fonte.
- Queres um **relatório Markdown/HTML pronto a rever**, não um edit script nem uma GUI.
- Consegues descrever a identidade de forma declarativa com uma **recipe** (uma
  chave estável por elemento) — Control-M, sitemaps, POMs e a maioria dos
  dialectos de config/export servem.
- Queres um **gate de CI**: saída não-zero em conflito.
- O ruído de atributos voláteis/reordenação está a estragar um diff de texto.

**Recorre a outra coisa quando:**

- Precisas de **aplicar um patch** / produzir um edit script → `xmldiff`.
- Um humano quer **fazer merge interativo de dois ficheiros** → DiffDog / Oxygen.
- Precisas de **matching heurístico de documentos sem chave** à escala enterprise,
  com contrato → DeltaXML.
- O XML já está normalizado e só queres **mudanças de linha** → `git diff`.

Em resumo: o `xmldiffreport` é a ferramenta para *“diz-me, entre estes N exports,
o que mudou de facto ao nível folder/job/atributo e marca as colisões”* — não para
merge interativo nem geração de patches.
