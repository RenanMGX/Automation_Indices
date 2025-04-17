import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from IndicesEstrutura import Indices
import requests
from time import sleep
import calendar
import pandas as pd

class CDI(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe CDI.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_cdi.json")
    
    
    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        
        #trava para que o indice não seja extraido antes do dia 5 do mes atual
        if (datetime.now().day <= 6) and ((self.data.month == (datetime.now() - relativedelta(months=1)).month)):
            raise ValueError("O Indice desta Data ainda não existe!")
        
        # Taxa de CDI ao ano e ao mês
        AO_ANO = 0.03
        AO_MES = ((1 + AO_ANO)**(1/12)-1)*100
        

        # Índice CDI mensal
        df = pd.DataFrame(self.arquivo)
        df = df[df['Mês'] == self.data.strftime('%Y-%m-%d')]
        if not df.empty:
            INDICE_CDI = df.iloc[0].to_dict()
            S_CDI = INDICE_CDI['CDI %']
            INDICE_CDI_JUROS = INDICE_CDI['Indice (CDI + Juros) %']
            FATOR_COMPOSTO = INDICE_CDI['Fator Composto']
        else:
            INDICE_CDI = self._extrair_indice_dias(12)

            # Cálculo do CDI acumulado
            S_CDI = dados_anterior['CDI'] * (1 + INDICE_CDI / 100)
        
            # Índice CDI com juros
            INDICE_CDI_JUROS = (AO_MES + INDICE_CDI) / 100

            # Fator composto para o próximo mês
            FATOR_COMPOSTO = dados_anterior['Fator Composto'] * (1 + INDICE_CDI_JUROS)
            
            

        if not novo:
            dados['Mês'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['CDI'] = round(S_CDI, 2)
            dados['CDI %'] = round(S_CDI, 6)
            dados['Juros (a.m.) %'] = AO_MES
            dados['Indice (CDI + Juros) %'] = INDICE_CDI_JUROS
            dados['Fator Composto'] = round(FATOR_COMPOSTO, 6)
        else:
            novos_dados = {
                'Mês' : datetime.strftime(self.data, "%Y-%m-%d"),
                'CDI' : round(S_CDI, 2),
                'CDI %' : round(S_CDI, 6),
                'Juros (a.m.) %' : AO_MES,
                'Indice (CDI + Juros) %' : INDICE_CDI_JUROS,
                'Fator Composto' : round(FATOR_COMPOSTO, 6)
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
        keys = ["Mês", "CDI", "Fator Composto"]
        return {chaves: entrada[chaves] for chaves in keys}

if __name__ == "__main__":
    # Exemplo de uso
    #data = (datetime.now() - relativedelta(months=0)).strftime("%d/%m/%Y")
    indice = CDI("01/03/2025", read_only=True)
    resultado = indice.resultado()
    print(resultado)
