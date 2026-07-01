"""Testes do ETL. Rode da RAIZ do projeto com:  pytest

Estes testes cobrem a conversão de valores — função pura, testável
sem precisar do dataset real. Bom hábito: testar a lógica crítica.
"""
import pandas as pd

from src.etl import converter_valor


def test_converter_valor_formato_br():
    entrada = pd.Series(["1.234,56", "10,00", "1.000.000,00"])
    resultado = converter_valor(entrada).tolist()
    assert resultado == [1234.56, 10.00, 1000000.00]


def test_converter_valor_invalido_vira_nan():
    resultado = converter_valor(pd.Series(["abc", ""]))
    assert resultado.isna().all()
