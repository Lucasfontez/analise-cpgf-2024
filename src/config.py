"""Configurações centrais do projeto: caminhos e constantes.

A ideia deste arquivo é reunir num lugar só tudo que é "ajuste" do projeto
(onde ficam as pastas, como ler os CSVs, como renomear as colunas). Assim,
nenhum caminho fica escrito solto no meio do código.
"""
from pathlib import Path

# Descobre a raiz do projeto de forma automática, sem caminho fixo:
#   __file__  -> o caminho deste próprio arquivo (config.py)
#   .resolve() -> transforma em caminho absoluto e completo
#   .parent.parent -> sobe dois níveis (de src/ para a raiz do projeto)
ROOT = Path(__file__).resolve().parent.parent

# Pastas de dados. O operador "/" do pathlib junta caminhos
# (ex.: ROOT / "data" vira ".../projeto/data").
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw" # onde ficam os 12 csv originais do Portal

# Caminho do banco SQLite gerado pelo ETL. Centralizar aqui garante que
# quem ESCREVE (etl.py) e quem LÊ (o notebook) usem exatamente o mesmo caminho.
DB_PATH = DATA_DIR / "cpgf_2024.db"

# Saídas do projeto (gráficos exportados).
OUTPUTS_DIR = ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"

# Parâmetros de leitura dos CSVs do Portal da Transparência.
CSV_ENCODING = "windows-1252" # encoding padrão dos arquivos do governo (acentos)
CSV_SEP = ";" # o separador de colunas é ponto-e-vírgula, não vírgula

# Dicionário que traduz o nome "feio" de cada coluna no Portal (à esquerda)
# para um nome limpo em snake_case (à direita). Usado no etl.py para renomear.
COLUNAS = {
    "CÓDIGO ÓRGÃO SUPERIOR": "codigo_orgao_superior",
    "NOME ÓRGÃO SUPERIOR": "nome_orgao_superior",
    "CÓDIGO ÓRGÃO": "codigo_orgao",
    "NOME ÓRGÃO": "nome_orgao",
    "CÓDIGO UNIDADE GESTORA": "codigo_unidade_gestora",
    "NOME UNIDADE GESTORA": "nome_unidade_gestora",
    "ANO EXTRATO": "ano_extrato",
    "MÊS EXTRATO": "mes_extrato",
    "CPF PORTADOR": "cpf_portador",
    "NOME PORTADOR": "nome_portador",
    "CNPJ OU CPF FAVORECIDO": "cnpj_cpf_favorecido",
    "NOME FAVORECIDO": "nome_favorecido",
    "TRANSAÇÃO": "transacao",
    "DATA TRANSAÇÃO": "data_transacao",
    "VALOR TRANSAÇÃO": "valor_transacao",
}

# Cria as pastas caso ainda não existam (roda ao importar o módulo).
# exist_ok=True evita erro se a pasta já estiver lá; é seguro rodar sempre.
for _d in (RAW_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)