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

class IPCA(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe IPCA.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_ipca.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        AO_ANO = 0.12
        AO_MES = ((1 + AO_ANO)**(1/12)-1)*100
        INDICE_IPCA = self._extrair_indice(433) / 100

        IPCA_MES = round(dados_anterior['IPCA Mês'] + (dados_anterior['IPCA Mês'] * INDICE_IPCA), 2)
        VARIACAO_IPCA = round((INDICE_IPCA) + 1, 4)
        VARIACAO_ACUM = VARIACAO_IPCA * dados_anterior['Variação IPCA']
        INDICE_COMPOSTO = VARIACAO_IPCA * (1 + (AO_MES / 100))
        FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['IPCA Mês'] = IPCA_MES
            dados['Variação IPCA'] = VARIACAO_IPCA
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'IPCA Mês': IPCA_MES,
                'Variação IPCA': VARIACAO_IPCA,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto': INDICE_COMPOSTO,
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
        keys = ["Mês Base", "IPCA Mês", "Fator Composto"]
        return {chaves: entrada[chaves] for chaves in keys}

if __name__ == "__main__":
    # Exemplo de uso
    indice = IPCA("01/12/2023", read_only=True)
    print(indice.resultado())
    # data = datetime.strptime(x['Mês Base'],"%Y-%m-%d")
    # print(data)
    # print(data - relativedelta(months=1))
