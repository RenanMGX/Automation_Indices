import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from time import sleep

try:
    from IndicesEstrutura import Indices
except ModuleNotFoundError:
    from .IndicesEstrutura import Indices


class Juros_0_5(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe Juros_0_5.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_juros_0_5.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        JUROS_MES = 100
        VARIACAO_JUROS = 1 + round(JUROS_MES / dados_anterior['Juros Mês'] - 1, 4)
        VARIACAO_ACUM = VARIACAO_JUROS * dados_anterior['Variação Acum.']
        INDICE_COMPOSTO = VARIACAO_JUROS * (1 + 0.005)
        FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Juros Mês'] = JUROS_MES
            dados['Variação Juros'] = VARIACAO_JUROS
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto (JUROS 0,5%)'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
            
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'Juros Mês': JUROS_MES,
                'Variação Juros': VARIACAO_JUROS,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto (JUROS 0,5%)': INDICE_COMPOSTO,
                'Fator Composto': FATOR_COMPOSTO
            }
            self.arquivo.append(novos_dados)

    def _tratar_retorno(self, entrada):
        """
        Retorna um subconjunto específico dos dados de entrada.

        Args:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """
        keys = ["Mês Base", "Fator Composto"]
        return {chaves: entrada[chaves] for chaves in keys}

class Juros_0_8(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe Juros_0_8.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_juros_0_8.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        JUROS_MES = 100
        VARIACAO_JUROS = 1 + round(JUROS_MES / dados_anterior['Juros Mês'] - 1, 4)
        VARIACAO_ACUM = VARIACAO_JUROS * dados_anterior['Variação Acum.']
        INDICE_COMPOSTO = VARIACAO_JUROS * (1 + 0.008)
        FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Juros Mês'] = JUROS_MES
            dados['Variação Juros'] = VARIACAO_JUROS
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto (JUROS 0,8%)'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
            
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'Juros Mês': JUROS_MES,
                'Variação Juros': VARIACAO_JUROS,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto (JUROS 0,8%)': INDICE_COMPOSTO,
                'Fator Composto': FATOR_COMPOSTO
            }
            self.arquivo.append(novos_dados)

    def _tratar_retorno(self, entrada):
        """
        Retorna um subconjunto específico dos dados de entrada.

        Args:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """
        keys = ["Mês Base", "Fator Composto"]
        return {chaves: entrada[chaves] for chaves in keys}


class Juros_1(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe Juros_1.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_juros_1.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        JUROS_MES = 100
        VARIACAO_JUROS = 1 + round(JUROS_MES / dados_anterior['Juros Mês'] - 1, 4)
        VARIACAO_ACUM = VARIACAO_JUROS * dados_anterior['Variação Acum.']
        INDICE_COMPOSTO = VARIACAO_JUROS * (1 + 0.01)
        FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Juros Mês'] = JUROS_MES
            dados['Variação Juros'] = VARIACAO_JUROS
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto (JUROS 1%)'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
            
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'Juros Mês': JUROS_MES,
                'Variação Juros': VARIACAO_JUROS,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto (JUROS 1%)': INDICE_COMPOSTO,
                'Fator Composto': FATOR_COMPOSTO
            }
            self.arquivo.append(novos_dados)

    def _tratar_retorno(self, entrada):
        """
        Retorna um subconjunto específico dos dados de entrada.

        Args:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """
        keys = ["Mês Base", "Fator Composto"]
        return {chaves: entrada[chaves] for chaves in keys}


if __name__ == "__main__":
    # Exemplo de uso
    data = "01/06/2024"
    indice = [Juros_0_5(data, read_only=True), Juros_0_8(data, read_only=True), Juros_1(data, read_only=True)]

    for x in indice:
        print(x.resultado())
