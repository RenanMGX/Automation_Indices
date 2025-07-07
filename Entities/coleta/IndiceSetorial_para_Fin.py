import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import sleep
import pandas as pd

try:
    from IndicesEstrutura import Indices
except ModuleNotFoundError:
    from .IndicesEstrutura import Indices


class IndicesFinSetoriais(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe IndicesFinSetoriais.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_setoriais_fin.json")

    def consultar_db(self, db, param_mes='Mês Base'):
        """
        Consulta o banco de dados.

        Args:
        - db (str): Nome do banco de dados.
        - param_mes (str): Nome do parâmetro de mês (opcional, padrão: 'Mês Base').

        Returns:
        - dict: Dados correspondentes ao mês na instância.
        """
        with open(f"db/{db}", 'r')as files:
            file = json.load(files)

        file = [line for line in file if line[param_mes] == self.data.strftime('%Y-%m-%d')][0]
        return file

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        df = pd.DataFrame(self.arquivo)

        df_mes = df[df['Mês Base'] == self.data.strftime('%Y-%m-%d')]            
            
        try:
            if df_mes.empty:
                IPCA = self.consultar_db("db_ipca.json")['IPCA Mês']
                IPCA_VAR = ((IPCA / dados_anterior['IPCA']) - 1) * 100
            else:
                indice = str(df_mes['IPCA'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    IPCA = float(indice)
                    IPCA_VAR = float(df_mes['IPCA_VAR'].iloc[0])
                else:
                    IPCA = self.consultar_db("db_ipca.json")['IPCA Mês']
                    IPCA_VAR = ((IPCA / dados_anterior['IPCA']) - 1) * 100
        except:
            IPCA = ""
            IPCA_VAR = ""
            
        
            
        try:
            if df_mes.empty:
                INPC = self.valor_inpc()
                INPC_VAR = ((INPC / dados_anterior['INPC']) - 1) * 100
            else:
                indice = str(df_mes['INPC'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    INPC = float(indice)
                    INPC_VAR = float(df_mes['INPC_VAR'].iloc[0])
                else:
                    INPC = self.valor_inpc()
                    INPC_VAR = ((INPC / dados_anterior['INPC']) - 1) * 100
        except:
            INPC = ""
            INPC_VAR = ""
                        
        
        
        try:
            if df_mes.empty:
                INCC = self.consultar_db("db_incc.json")['INCC']
                INCC_VAR = ((INCC / dados_anterior['INCC']) - 1) * 100
                try:
                    INCC_DEZEMBRO_ANTERIOR = df[df['Mês Base'] == (
                        (self.data - relativedelta(years=1)).replace(month=12)).strftime('%Y-%m-%d')]['INCC'].values[0]
                    INCC_VAR_ANO = ((INCC / INCC_DEZEMBRO_ANTERIOR) - 1) * 100
                except:
                    INCC_VAR_ANO = ""

                try:
                    INCC_ANO_ANTERIOR = df[df['Mês Base'] == (
                        (self.data - relativedelta(years=1))).strftime('%Y-%m-%d')]['INCC'].values[0]
                    INCC_VAR_12_MESES = ((INCC / INCC_ANO_ANTERIOR) - 1) * 100
                except:
                    INCC_VAR_12_MESES = ""
                
            else:
                indice = str(df_mes['INCC'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    INCC = float(indice)
                    INCC_VAR = float(df_mes['INCC_MES_VAR'].iloc[0])
                    INCC_VAR_ANO = float(df_mes['INCC_ANO_VAR'].iloc[0])
                    INCC_VAR_12_MESES = float(df_mes['INCC_12_MESES_VAR'].iloc[0])
                else:
                    INCC = self.consultar_db("db_incc.json")['INCC']
                    INCC_VAR = ((INCC / dados_anterior['INCC']) - 1) * 100
            
                    try:
                        INCC_DEZEMBRO_ANTERIOR = df[df['Mês Base'] == (
                            (self.data - relativedelta(years=1)).replace(month=12)).strftime('%Y-%m-%d')]['INCC'].values[0]
                        INCC_VAR_ANO = ((INCC / INCC_DEZEMBRO_ANTERIOR) - 1) * 100
                    except:
                        INCC_VAR_ANO = ""

                    try:
                        INCC_ANO_ANTERIOR = df[df['Mês Base'] == (
                            (self.data - relativedelta(years=1))).strftime('%Y-%m-%d')]['INCC'].values[0]
                        INCC_VAR_12_MESES = ((INCC / INCC_ANO_ANTERIOR) - 1) * 100
                    except:
                        INCC_VAR_12_MESES = ""
                    
        except:
            INCC = ""
            INCC_VAR = ""
            INCC_VAR_ANO = ""
            INCC_VAR_12_MESES = ""
            
        try:
            if df_mes.empty:
                CDI_VAR = self._extrair_indice_dias(12)
                CDI = dados_anterior['CDI'] * (1 + CDI_VAR / 100)
            else:
                indice = str(df_mes['CDI_VAR'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    CDI_VAR = float(indice)
                    CDI = float(df_mes['CDI'].iloc[0])
                else:
                    CDI_VAR = self._extrair_indice_dias(12)
                    CDI = dados_anterior['CDI'] * (1 + CDI_VAR / 100)
        except:
            CDI_VAR = ""
            CDI = ""
            
                
            
        try:
            if df_mes.empty:
                IGP_DI = self.valor_igp_di()
                IGP_DI_VAR = ((IGP_DI / dados_anterior['IGP DI']) - 1) * 100
            else:
                indice = str(df_mes['IGP DI'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    IGP_DI = float(indice)
                    IGP_DI_VAR = float(df_mes['IGP DI_VAR'].iloc[0])
                else:
                    IGP_DI = self.valor_igp_di()
                    IGP_DI_VAR = ((IGP_DI / dados_anterior['IGP DI']) - 1) * 100
        except:
            IGP_DI = ""
            IGP_DI_VAR = ""
            
            
        try:
            if (df_mes.empty) or ((indice:=str(df_mes['IGP-M'].iloc[0])) != "nan"):
                IGP_M = float(indice)
                IGP_M_VAR = float(df_mes['IGP-M_VAR'].iloc[0])
            else:
                IGP_M = self.valor_igp_m()
                IGP_M_VAR = ((IGP_M / dados_anterior['IGP-M']) - 1) * 100
        except:
            IGP_M = ""
            IGP_M_VAR = ""
            
        try:
            if df_mes.empty:
                IGP_M = self.valor_igp_m()
                IGP_M_VAR = ((IGP_M / dados_anterior['IGP-M']) - 1) * 100
            else:
                indice = str(df_mes['IGP-M'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    IGP_M = float(indice)
                    IGP_M_VAR = float(df_mes['IGP-M_VAR'].iloc[0])
                else:
                    IGP_M = self.valor_igp_m()
                    IGP_M_VAR = ((IGP_M / dados_anterior['IGP-M']) - 1) * 100
        except:
            IGP_M = ""
            IGP_M_VAR = ""
            
            
            
        try:
            if df_mes.empty:
                SALARIO_MIN = self._extrair_indice(1619)
            else:
                indice = str(df_mes['SALARIO MINIMO'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    SALARIO_MIN = float(indice)
                else:
                    SALARIO_MIN = self._extrair_indice(1619)
        except:
            SALARIO_MIN = ""
            
            
            
            
                        
        try:
            if df_mes.empty:
                POUPA_VAR = self._extrair_indice(25)
            else:
                indice = str(df_mes['POUP_VAR'].iloc[0])
                if (indice != "nan") and (indice != ""):
                    POUPA_VAR = float(indice)
                else:
                    POUPA_VAR = self._extrair_indice(25)
        except:
            POUPA_VAR = ""
            
            
            
            
            
            
            
            
            
            







        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['IPCA'] = IPCA
            dados['IPCA_VAR'] = IPCA_VAR
            dados['INPC'] = INPC
            dados['INPC_VAR'] = INPC_VAR
            dados['INCC'] = INCC
            dados['INCC_MES_VAR'] = INCC_VAR
            dados['INCC_ANO_VAR'] = INCC_VAR_ANO
            dados['INCC_12_MESES_VAR'] = INCC_VAR_12_MESES
            dados['CDI'] = CDI
            dados['CDI_VAR'] = CDI_VAR
            dados['IGP DI'] = IGP_DI
            dados['IGP DI_VAR'] = IGP_DI_VAR
            dados['IGP-M'] = IGP_M
            dados['IGP-M_VAR'] = IGP_M_VAR
            dados['SALARIO MINIMO'] = SALARIO_MIN
            dados['POUP_VAR'] = POUPA_VAR
        else:
            novos_dados: dict = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d")
            }
            novos_dados['IPCA'] = IPCA
            novos_dados['IPCA_VAR'] = IPCA_VAR
            novos_dados['INPC'] = INPC
            novos_dados['INPC_VAR'] = INPC_VAR
            novos_dados['INCC'] = INCC
            novos_dados['INCC_MES_VAR'] = INCC_VAR
            novos_dados['INCC_ANO_VAR'] = INCC_VAR_ANO
            novos_dados['INCC_12_MESES_VAR'] = INCC_VAR_12_MESES
            novos_dados['CDI'] = CDI
            novos_dados['CDI_VAR'] = CDI_VAR
            novos_dados['IGP DI'] = IGP_DI
            novos_dados['IGP DI_VAR'] = IGP_DI_VAR
            novos_dados['IGP-M'] = IGP_M
            novos_dados['IGP-M_VAR'] = IGP_M_VAR
            novos_dados['SALARIO MINIMO'] = SALARIO_MIN
            novos_dados['POUP_VAR'] = POUPA_VAR
            self.arquivo.append(novos_dados)

    def resultado(self):
        """
        Retorna o resultado do cálculo.

        Returns:
        - dict: Dados calculados.
        """
        return super().resultado()


if __name__ == "__main__":
    # Exemplo de uso
    indice = IndicesFinSetoriais(f"01/06/2025", read_only=True)
    print(indice.resultado())
