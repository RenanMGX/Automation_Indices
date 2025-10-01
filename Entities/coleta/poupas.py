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


class Poupas12(Indices):
    def __init__(self, data=None, read_only=True, *, force:bool=False):
        """
        Inicializa a classe PoupasBase.

        Parameters:
        - data (str): Data no formato 'dd/mm/yyyy'. Se não fornecido, será o primeiro dia do mês atual.
        - read_only (bool): Indica se a instância será somente leitura.
        """     
        self.__force = force   
        if data == None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/poupas_12.json")

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Realiza cálculos com base no índice extraído.

        Parameters:
        - dados_anterior (dict): Dados anteriores para cálculos de variação.
        - dados (dict): Dados a serem atualizados ou criados.
        - novo (bool): Indica se é um novo conjunto de dados.

        Returns:
        - None
        """    
        
        df = pd.DataFrame(self.arquivo)
        df = df[df['Data'] == self.data.strftime('%Y-%m-%d')]
        if (not df.empty) and (not self.__force):
            INDICE = df.iloc[0].to_dict()['%']
        else:
            #INDICE = self._extrair_indice(196)
            INDICE = _INDICE if (_INDICE := self._extrair_indice(196)) > 0 else 0
            
        #INDICE = self._extrair_indice(196)
        ACUMULADO = dados_anterior['Acumulado']*((INDICE / 100)+1)
        VAR_PORCENTO = ACUMULADO/dados_anterior['Acumulado']-1


        if not novo:
            dados['Data'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Poupa'] = 12
            dados['%'] = INDICE
            dados['Acumulado'] = ACUMULADO
            dados['Fator Composto'] = VAR_PORCENTO
        else:
            novos_dados = {
            'Data': datetime.strftime(self.data, "%Y-%m-%d"),
            'Poupa': 12,
            '%': INDICE,
            'Acumulado': ACUMULADO,
            'Fator Composto': VAR_PORCENTO
            }
            self.arquivo.append(novos_dados)

    def _tratar_retorno(self, entrada):
        """
        Seleciona chaves específicas do retorno.

        Parameters:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """        
        keys = ["Data", "Acumulado"]
        return {chaves: entrada[chaves] for chaves in keys}

class Poupas15(Indices):
    def __init__(self, data=None, read_only=True, *, force:bool=False):
        """
        Inicializa a classe PoupasBase.

        Parameters:
        - data (str): Data no formato 'dd/mm/yyyy'. Se não fornecido, será o primeiro dia do mês atual.
        - read_only (bool): Indica se a instância será somente leitura.
        """    
        self.__force = force            
        if data == None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/poupas_15.json")


    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Realiza cálculos com base no índice extraído.

        Parameters:
        - dados_anterior (dict): Dados anteriores para cálculos de variação.
        - dados (dict): Dados a serem atualizados ou criados.
        - novo (bool): Indica se é um novo conjunto de dados.

        Returns:
        - None
        """       
        
        df = pd.DataFrame(self.arquivo)
        df = df[df['Data'] == self.data.strftime('%Y-%m-%d')]
        if not df.empty:
            INDICE = df.iloc[0].to_dict()['%']
        else:
            #INDICE = self._extrair_indice(196)
            INDICE = _INDICE if (_INDICE := self._extrair_indice(196)) > 0 else 0
         
        #INDICE = self._extrair_indice(196)
        ACUMULADO = dados_anterior['Acumulado']*((INDICE / 100)+1)
        VAR_PORCENTO = ACUMULADO/dados_anterior['Acumulado']-1

        if not novo:
            dados['Data'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Poupa'] = 15
            dados['%'] = INDICE
            dados['Acumulado'] = ACUMULADO
            dados['Fator Composto'] = VAR_PORCENTO
        else:
            novos_dados = {
            'Data': datetime.strftime(self.data, "%Y-%m-%d"),
            'Poupa': 15,
            '%': INDICE,
            'Acumulado': ACUMULADO,
            'Fator Composto': VAR_PORCENTO
            }
            self.arquivo.append(novos_dados)

    def _tratar_retorno(self, entrada):
        """
        Seleciona chaves específicas do retorno.

        Parameters:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """        
        keys = ["Data", "Acumulado"]
        return {chaves: entrada[chaves] for chaves in keys}

class Poupas28(Indices):
    def __init__(self, data=None, read_only=True, *, force:bool=False):
        """
        Inicializa a classe PoupasBase.

        Parameters:
        - data (str): Data no formato 'dd/mm/yyyy'. Se não fornecido, será o primeiro dia do mês atual.
        - read_only (bool): Indica se a instância será somente leitura.
        """   
        self.__force = force             
        if data == None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/poupas_28.json")


    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Realiza cálculos com base no índice extraído.

        Parameters:
        - dados_anterior (dict): Dados anteriores para cálculos de variação.
        - dados (dict): Dados a serem atualizados ou criados.
        - novo (bool): Indica se é um novo conjunto de dados.

        Returns:
        - None
        """        


        df = pd.DataFrame(self.arquivo)
        df = df[df['Data'] == self.data.strftime('%Y-%m-%d')]
        if (not df.empty) and (not self.__force):
            INDICE = df.iloc[0].to_dict()['%']
        else:
            #INDICE = self._extrair_indice(196)
            INDICE = _INDICE if (_INDICE := self._extrair_indice(196)) > 0 else 0
        
        ACUMULADO = dados_anterior['Acumulado']*((INDICE / 100)+1)
        VAR_PORCENTO = ACUMULADO/dados_anterior['Acumulado']-1

        if not novo:
            dados['Data'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['Poupa'] = 28
            dados['%'] = INDICE
            dados['Acumulado'] = ACUMULADO
            dados['Fator Composto'] = VAR_PORCENTO
        else:
            novos_dados = {
            'Data': datetime.strftime(self.data, "%Y-%m-%d"),
            'Poupa': 28,
            '%': INDICE,
            'Acumulado': ACUMULADO,
            'Fator Composto': VAR_PORCENTO
            }
            self.arquivo.append(novos_dados)

    def _tratar_retorno(self, entrada):
        """
        Seleciona chaves específicas do retorno.

        Parameters:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """        
        keys = ["Data", "Acumulado"]
        return {chaves: entrada[chaves] for chaves in keys}

if __name__ == "__main__":
    # Exemplo de uso
    data = "01/03/2025"
    indice = [Poupas12(data, read_only=True, force=True),Poupas15(data, read_only=True, force=True),Poupas28(data, read_only=True, force=True)]

    for x in indice:
        print(x.resultado())