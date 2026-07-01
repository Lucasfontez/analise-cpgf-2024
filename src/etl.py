"""
ETL: lê os CSVs mensais do CPGF, limpa e consolida em um banco SQLite.

fluxo: data/raw/*.csv -> limpeza / padronização -> data/cpgf_2024.db

separa a PREPARAÇÃO do dado da ANÁLISE (que fica no notebook).
Roda no terminal:  python -m src.etl
"""
from __future__ import annotations

import glob
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from src import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def converter_valor(serie: pd.Series) -> pd.Series:
    """converte valor do formato brasileiro ('1.234,56' texto) para número (1234.56).

    o Portal traz os valores em padrão BR (ponto de milhar, vírgula decimal),
    que o Python não entende como número. É o ponto mais delicado do ETL
    toda a análise depende dessa coluna virar número para poder ser somada.

    ".str" é o acessador de texto do pandas, aplica a operação seguinte a
    todos os valores da coluna de uma vez. As trocas são encadeadas, na ordem:
    """
    return (
        serie.astype(str)
        .str.replace(".", "", regex=False)   # tira o ponto de milhar:  "1.234,56" -> "1234,56"
        .str.replace(",", ".", regex=False)  # vírgula decimal p/ ponto: "1234,56"  -> "1234.56"
        # .pipe(f) = aplica f ao resultado da cadeia; equivale a pd.to_numeric(...).
        # errors="coerce" = valor que não vira número vira NaN, em vez de quebrar.
        .pipe(pd.to_numeric, errors="coerce")
    )


def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """renomeia as colunas do padrão do Portal para snake_case (ver config.COLUNAS)."""
    df.columns = df.columns.str.strip()
    return df.rename(columns=config.COLUNAS)


def ler_csv(caminho: str) -> pd.DataFrame:
    """lê um CSV do Portal com o encoding e separador corretos, tudo como texto."""
    return pd.read_csv(
        caminho,
        sep=config.CSV_SEP,
        encoding=config.CSV_ENCODING,
        encoding_errors="replace",
        dtype=str,          # lê tudo como texto; a conversão de tipos vem no tratar()
        quotechar='"',
    )


def tratar(df: pd.DataFrame) -> pd.DataFrame:
    """limpa um arquivo: padroniza os nomes das colunas e converte os tipos numéricos."""
    df = padronizar_colunas(df)
    df["valor_transacao"] = converter_valor(df["valor_transacao"])
    df["ano_extrato"] = pd.to_numeric(df["ano_extrato"], errors="coerce")
    df["mes_extrato"] = pd.to_numeric(df["mes_extrato"], errors="coerce")
    return df


def executar() -> pd.DataFrame:
    """lê todos os CSVs de data/raw, limpa cada um e salva no SQLite."""
    arquivos = sorted(glob.glob(str(config.RAW_DIR / "*.csv")))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {config.RAW_DIR}. "
            "Baixe os 12 extratos do Portal da Transparência e coloque-os nessa pasta."
        )
    logger.info("%d arquivo(s) encontrado(s)", len(arquivos))

    partes: list[pd.DataFrame] = []
    for caminho in arquivos:
        bruto = ler_csv(caminho)
        tratado = tratar(bruto)
        # trava de qualidade: "assert <condição>" para o programa se a condição
        # for falsa. Aqui garante que nenhuma linha se perdeu na limpeza
        # (nº de linhas lidas == nº de linhas tratadas) — evita erro silencioso.
        assert len(bruto) == len(tratado), f"Divergência de linhas em {caminho}"
        partes.append(tratado)
        logger.info("OK %s — %d linhas", Path(caminho).name, len(tratado))

    # junta os 12 DataFrames (um por mês) num só, empilhando um sob o outro.
    # ignore_index=True renumera as linhas de 0 a N; sem isso, o índice de cada
    # mês recomeçaria do zero e haveria repetição.
    df = pd.concat(partes, ignore_index=True)

    logger.info("Consolidado: %d linhas, %d colunas", len(df), df.shape[1])
    logger.info("Nulos em valor_transacao: %d", int(df["valor_transacao"].isna().sum()))

    # salva o DataFrame como a tabela 'cpgf' no banco SQLite.
    # if_exists="replace" = recria a tabela do zero se ela já existir.
    # index=False = não grava o índice do pandas como uma coluna extra.
    conn = sqlite3.connect(config.DB_PATH)
    df.to_sql("cpgf", conn, if_exists="replace", index=False)
    conn.close()
    logger.info("SQLite salvo em %s (tabela 'cpgf')", config.DB_PATH)
    return df


# só executa se o arquivo for rodado direto (python -m src.etl); se for
# apenas importado, as funções ficam disponíveis mas nada roda sozinho.
if __name__ == "__main__":
    executar()