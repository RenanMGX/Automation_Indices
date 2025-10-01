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
import pandas as pd

class IPCA(Indices):
    def __init__(self, data=None, read_only=True, *, force:bool=False):
        """
        Inicializa uma instância da classe IPCA.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        self.__force = force
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
        

        df = pd.DataFrame(self.arquivo)
        df = df[df['Mês Base'] == self.data.strftime('%Y-%m-%d')]
        if (not df.empty) and (not self.__force):
            IPCA_MES = df.iloc[0].to_dict()['IPCA Mês']
            VARIACAO_IPCA = df.iloc[0].to_dict()['Variação IPCA']
            VARIACAO_ACUM = df.iloc[0].to_dict()['Variação Acum.']
            INDICE_COMPOSTO = df.iloc[0].to_dict()['Indice Composto']
            FATOR_COMPOSTO = df.iloc[0].to_dict()['Fator Composto']
        else:
            #INDICE_IPCA = self._extrair_indice(433) / 100
            INDICE_IPCA = _INDICE if (_INDICE := (self._extrair_indice(433) / 100)) > 0 else 0
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
    
    
class IPCA_1(Indices):
    def __init__(self, data=None, read_only=True, *, force:bool=False):
        """
        Inicializa uma instância da classe IPCA.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        self.__force = force
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_ipca_1.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        #import pdb;pdb.set_trace()
        
        df = pd.DataFrame(self.arquivo)
        df = df[df['Mês Base'] == self.data.strftime('%Y-%m-%d')]
        if (not df.empty) and (not self.__force):
            IPCA_MES = df.iloc[0].to_dict()['IPCA Mês']
            INDICE_IPCA = df.iloc[0].to_dict()['Variação IPCA']
            VARIACAO_ACUM = df.iloc[0].to_dict()['Variação Acum.']
            INDICE_COMPOSTO = df.iloc[0].to_dict()['Indice Composto (IPCA + 1%)']
            FATOR_COMPOSTO = df.iloc[0].to_dict()['Fator Composto']
            VARIACAO_IPCA_1 = df.iloc[0].to_dict()['Variação IPCA + 1%']
            VARIACAO_IPCA = df.iloc[0].to_dict()['Variação IPCA.1']
            ACRESCIMO_IPCA = df.iloc[0].to_dict()['Acrescimo IPCA']
        else:
            #INDICE_IPCA = (self._extrair_indice(433) / 100) + 1
            INDICE_IPCA = _INDICE if (_INDICE := (self._extrair_indice(433) / 100) + 1) > 0 else 0
            IPCA_MES = dados_anterior['IPCA Mês'] * INDICE_IPCA
            VARIACAO_ACUM = INDICE_IPCA * dados_anterior['Variação Acum.']
            INDICE_COMPOSTO = INDICE_COMPOSTO if (INDICE_COMPOSTO := INDICE_IPCA + 0.01) > 1 else 1
            FATOR_COMPOSTO = dados_anterior['Fator Composto'] * INDICE_COMPOSTO
            VARIACAO_IPCA_1 = (FATOR_COMPOSTO / dados_anterior['Fator Composto'] - 1) * 100
            VARIACAO_IPCA = (IPCA_MES / dados_anterior['IPCA Mês'] - 1) * 100
            ACRESCIMO_IPCA = VARIACAO_IPCA_1 - VARIACAO_IPCA

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['IPCA Mês'] = IPCA_MES
            dados['Variação IPCA'] = INDICE_IPCA
            dados['Variação Acum.'] = VARIACAO_ACUM
            dados['Indice Composto (IPCA + 1%)'] = INDICE_COMPOSTO
            dados['Fator Composto'] = FATOR_COMPOSTO
            dados['Variação IPCA + 1%'] = VARIACAO_IPCA_1
            dados['Variação IPCA.1'] = VARIACAO_IPCA
            dados['Acrescimo IPCA'] = ACRESCIMO_IPCA
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'IPCA Mês': IPCA_MES,
                'Variação IPCA': INDICE_IPCA,
                'Variação Acum.': VARIACAO_ACUM,
                'Indice Composto (IPCA + 1%)': INDICE_COMPOSTO,
                'Fator Composto': FATOR_COMPOSTO,
                'Variação IPCA + 1%': VARIACAO_IPCA_1,
                'Variação IPCA.1': VARIACAO_IPCA,
                'Acrescimo IPCA': ACRESCIMO_IPCA
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
        #return entrada

if __name__ == "__main__":
    # Exemplo de uso
    indice = IPCA("01/09/2025", read_only=True, force=False).resultado()
    indice2 = IPCA_1("01/09/2025", read_only=True, force=False).resultado()
    #print(indice)
    import pandas as pd
    df = pd.DataFrame([indice, indice2])
    print(df)
    #df.to_excel("ipca_1.xlsx", index=False)
    # data = datetime.strptime(x['Mês Base'],"%Y-%m-%d")
    # print(data)
    # print(data - relativedelta(months=1))
