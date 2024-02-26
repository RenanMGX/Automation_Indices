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


class IGPM(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe IGPM.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_igpm.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        INDICE = INDICE if (INDICE := self._extrair_indice(189)) > 0 else 0
        VALOR = dados_anterior['Valor'] * (1 + INDICE / 100)

        if not novo:
            dados['Data'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Valor'] = round(VALOR, 6)
            dados['Variação (%)'] = INDICE
        else:
            novos_dados = {
                'Data': datetime.strftime(self.data, "%Y-%m-%d"),
                'Valor': round(VALOR, 6),
                'Variação (%)': INDICE
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
        keys = ["Data", "Valor"]
        return {chaves: entrada[chaves] for chaves in keys}


class IGPM_0_50(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe IGPM_0_50.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_igpm_0_50.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        INDICE = (self._extrair_indice(189) / 100) + 1
        IGPM_MES = dados_anterior['IGPM Mês'] * INDICE
        VARIACAO_ACUM = INDICE * dados_anterior['Variação Acum.']
        INDICE_COMPOSTO = INDICE_COMPOSTO if (INDICE_COMPOSTO := INDICE * (1 + 0.005)) > 1 else 1
        FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO
        VARIACAO_IGPM_0_5 = (FATOR_COMPOSTO / dados_anterior['Fator Composto'] - 1) * 100
        VARIACAO_IGPM = (IGPM_MES / dados_anterior['IGPM Mês'] - 1) * 100
        ACRESCIMO_IGPM = VARIACAO_IGPM_0_5 - VARIACAO_IGPM

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['IGPM Mês'] = IGPM_MES
            dados['Variação IGPM'] = INDICE
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto (IGPM + 0,5%)'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
            dados['Variação IGPM + 0,5%'] = VARIACAO_IGPM_0_5
            dados['Variação IGPM.1'] = VARIACAO_IGPM
            dados['Acrescimo IGPM'] = ACRESCIMO_IGPM
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'IGPM Mês': IGPM_MES,
                'Variação IGPM': INDICE,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto (IGPM + 0,5%)': INDICE_COMPOSTO,
                'Fator Composto': FATOR_COMPOSTO,
                'Variação IGPM + 0,5%': VARIACAO_IGPM_0_5,
                'Variação IGPM.1': VARIACAO_IGPM,
                'Acrescimo IGPM': ACRESCIMO_IGPM
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


class IGPM_1(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe IGPM_1.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_igpm_1.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        INDICE = (self._extrair_indice(189) / 100) + 1
        IGPM_MES = dados_anterior['IGPM Mês'] * INDICE
        VARIACAO_ACUM = INDICE * dados_anterior['Variação Acum.']
        INDICE_COMPOSTO = INDICE_COMPOSTO if (INDICE_COMPOSTO := INDICE * (1 + 0.01)) > 1 else 1
        FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO
        VARIACAO_IGPM_1 = (FATOR_COMPOSTO / dados_anterior['Fator Composto'] - 1) * 100
        VARIACAO_IGPM = (IGPM_MES / dados_anterior['IGPM Mês'] - 1) * 100
        ACRESCIMO_IGPM = VARIACAO_IGPM_1 - VARIACAO_IGPM

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['IGPM Mês'] = IGPM_MES
            dados['Variação IGPM'] = INDICE
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto (IGPM + 1%)'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
            dados['Variação IGPM + 1%'] = VARIACAO_IGPM_1
            dados['Variação IGPM.1'] = VARIACAO_IGPM
            dados['Acrescimo IGPM'] = ACRESCIMO_IGPM
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'IGPM Mês': IGPM_MES,
                'Variação IGPM': INDICE,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto (IGPM + 1%)': INDICE_COMPOSTO,
                'Fator Composto': FATOR_COMPOSTO,
                'Variação IGPM + 1%': VARIACAO_IGPM_1,
                'Variação IGPM.1': VARIACAO_IGPM,
                'Acrescimo IGPM': ACRESCIMO_IGPM
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
    data = "01/12/2023"
    indice = [IGPM(data, read_only=True), IGPM_0_50(data, read_only=True), IGPM_1(data, read_only=True)]

    for x in indice:
        print(x.resultado())