# Dicionário de Dados — CPGF 2024

Documentação das colunas do dataset de Cartões de Pagamento do Governo Federal (CPGF), referente ao exercício de 2024.

- **Fonte:** [Portal da Transparência — Governo Federal](https://portaldatransparencia.gov.br/)
- **Granularidade:** 1 linha = 1 transação de cartão corporativo
- **Volume:** 141.048 registros · 15 colunas
- **Período:** Janeiro a Dezembro de 2024

---

## Colunas

| # | Coluna (padronizada) | Origem (Portal) | Tipo | Descrição |
|---|---|---|---|---|
| 1 | `codigo_orgao_superior` | CÓDIGO ÓRGÃO SUPERIOR | texto/int | Código do órgão superior (ex.: ministério) ao qual a unidade está vinculada |
| 2 | `nome_orgao_superior` | NOME ÓRGÃO SUPERIOR | texto | Nome do órgão superior. Dimensão principal de agregação do projeto |
| 3 | `codigo_orgao` | CÓDIGO ÓRGÃO | texto/int | Código do órgão/entidade vinculada ao órgão superior |
| 4 | `nome_orgao` | NOME ÓRGÃO | texto | Nome do órgão/entidade |
| 5 | `codigo_unidade_gestora` | CÓDIGO UNIDADE GESTORA | texto/int | Código da Unidade Gestora (UG) responsável pela execução |
| 6 | `nome_unidade_gestora` | NOME UNIDADE GESTORA | texto | Nome da Unidade Gestora |
| 7 | `ano_extrato` | ANO EXTRATO | int | Ano de referência do extrato. Constante = 2024 neste recorte |
| 8 | `mes_extrato` | MÊS EXTRATO | int | Mês de referência do extrato (1–12). Base da análise de sazonalidade |
| 9 | `cpf_portador` | CPF PORTADOR | texto | CPF do portador do cartão, **mascarado** pelo Portal (`***.NNN.NNN-**`) |
| 10 | `nome_portador` | NOME PORTADOR | texto | Nome do servidor portador do cartão. Pode vir como `Sigiloso` |
| 11 | `cnpj_cpf_favorecido` | CNPJ OU CPF FAVORECIDO | texto | CNPJ (completo) ou CPF (mascarado) de quem recebeu o pagamento |
| 12 | `nome_favorecido` | NOME FAVORECIDO | texto | Nome/razão social do favorecido. Pode vir como `Sigiloso`, `NAO SE APLICA` ou `SEM INFORMACAO` |
| 13 | `transacao` | TRANSAÇÃO | texto | Tipo da transação (compra presencial, saque, sigilosa, etc.) — ver domínio abaixo |
| 14 | `data_transacao` | DATA TRANSAÇÃO | texto → data | Data da transação. **No CSV original vem como texto** — recomenda-se parse para `datetime` |
| 15 | `valor_transacao` | VALOR TRANSAÇÃO | float | Valor da transação em R$. Origem em formato BR (`1.234,56`), convertido para float no ETL |

---

## Domínios e valores especiais

### `transacao` — tipos observados
| Valor original | Significado |
|---|---|
| `COMPRA A/V - R$ - APRES` | Compra presencial à vista, em reais |
| `Informações protegidas por sigilo` | **Transação sigilosa** — tipo não divulgado publicamente |
| `SAQUE CASH/ATM BB` | Saque em caixa eletrônico (Banco do Brasil) |
| `COMPRA A/V - INT$ - APRES` | Compra presencial à vista, em moeda estrangeira |
| `SAQUE - INT$ - APRES` | Saque internacional |
| `COMP A/V-SOL DISP C/CLI-R$ ANT VENC` | Compra antecipada |

### Os dois conceitos de "sigilo" (não confundir)
O dataset tem **duas formas distintas** de sigilo, que precisam ser tratadas e narradas separadamente:

1. **Sigilo de transação** → `transacao = 'Informações protegidas por sigilo'`. É o tipo da operação que está oculto. Representa ~43,9% do valor total.
2. **Sigilo de identificação** → `nome_portador = 'Sigiloso'` ou `nome_favorecido = 'Sigiloso'`. Aqui a operação aparece, mas a pessoa/empresa está oculta.

Um mesmo registro pode ter um, outro, ambos ou nenhum. Misturar os dois leva a contagens erradas.

### Marcadores de ausência de dado
- `NAO SE APLICA` (em `nome_favorecido`): geralmente associado a saques, onde não há favorecido nominal.
- `SEM INFORMACAO` (em `nome_favorecido`): ausência de registro do favorecido no sistema.
- Decisão de projeto: **mantidos** como categorias válidas (representam a própria lacuna de transparência), e não tratados como nulo.

---

## Observações de qualidade

| Tema | Nota |
|---|---|
| **Encoding** | CSVs originais em `windows-1252` (padrão do Portal). Ler com esse encoding evita corrupção de acentos |
| **Separador** | `;` como delimitador de campo; `,` como separador decimal (formato BR) |
| **`valor_transacao`** | Conversão `1.234,56 → 1234.56`; valores não numéricos viram `NaN` via `errors='coerce'` |
| **`data_transacao`** | Não parseada na versão original — converter para `datetime` destrava análises por dia da semana, fim de mês, etc. |
| **Duplicatas** | Não há ID único de transação. Linhas idênticas podem ser transações legítimas distintas — remoção pode eliminar dado válido. Avaliar via chave composta antes de qualquer `drop_duplicates` |
| **CPF mascarado** | `cpf_portador` não permite identificação individual completa — adequado para análise agregada, não para rastreio nominal |

---

## Proveniência

- **Coleta:** download dos 12 extratos mensais (CSV) na seção CPGF do Portal da Transparência.
- **Processamento:** padronização de nomes de colunas, conversão de tipos e consolidação em arquivo único (`cpgf_2024.parquet`).
- **Atualização da fonte:** mensal, conforme prazos de divulgação do Governo Federal.
