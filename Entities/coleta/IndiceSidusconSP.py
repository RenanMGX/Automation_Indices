import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import pandas as pd
from time import sleep
try:
    from IndicesEstrutura import Indices
except ModuleNotFoundError:
    from .IndicesEstrutura import Indices
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

class SetoriaisSP(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa a classe SetoriaisSP.

        Parameters:
        - data (str): Data no formato 'dd/mm/yyyy'. Se não fornecido, será o primeiro dia do mês atual.
        - read_only (bool): Indica se a instância será somente leitura.
        """        
        if data == None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_siduscon_sp.json")

    def _str_to_float(self, entrada):
        """
        Converte uma string formatada como número para um float.

        Parameters:
        - entrada (str): String representando um número.

        Returns:
        - float: Valor convertido.
        """        
        return float(entrada.replace('.', '').replace(',','.'))

    def _obter_arquivo(self):
        """
        Obtém o arquivo Excel contendo os índices do site.

        Returns:
        - DataFrame: Pandas DataFrame contendo os dados do arquivo Excel.
        """        
        caminho = f"{os.getcwd()}\\download_indice_rj"
        if caminho[-1] != "\\":
            caminho += "\\"

        if not os.path.exists(caminho):
            os.makedirs(caminho)

        for arquivo in os.listdir(caminho):
            os.unlink(caminho + arquivo)

        prefs = {"download.default_directory" : caminho}    
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", prefs)

        url = "https://sindusconsp.com.br/servicos/cub/"
        with webdriver.Chrome(options=chrome_options) as NAVEGADOR:
            try:
                NAVEGADOR.get(url)
                sleep(1)
                NAVEGADOR.find_element(By.XPATH, '//*[@id="codewidget-4"]/div/div/div/div[2]/div[1]/div/div/a').click()
            except:
                raise ConnectionAbortedError("Site do Siduscon SP está inacessivel")
            
            for x in range(5*60):
                if len(os.listdir(caminho)) > 0:
                    sleep(1)
                    break
                sleep(1)
            sleep(2)
        if len(os.listdir(caminho)) > 0:
            for arquivo in os.listdir(caminho):
                df = pd.read_excel(caminho + arquivo)
                os.unlink(caminho + arquivo)
        else:
            os.rmdir(caminho)
            raise FileNotFoundError("Arquivo não encontrado")
        os.rmdir(caminho)

        return df
    
    def _extratir_indice(self):
        """
        Extrai o índice específico do DataFrame obtido do arquivo Excel.

        Returns:
        - float: Índice extraído.
        """        
        df = self._obter_arquivo()

        coluna = df.columns.to_list()
        df = df[[coluna[0], coluna[8]]]
        #data = "1/2023"
        #data = datetime.strptime(data, '%m/%Y')

        coluna = df.columns.to_list()
        try:
            indice = round(df[df[coluna[0]] == self.data][coluna[1]].tolist()[0], 2)
        except:
            indice = "Indice desta data não existe"
            raise FileNotFoundError("Indice desta data não existe")
        
        return indice 


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
        df = df[df['Mês Base'] == self.data.strftime('%Y-%m-%d')]
        if not df.empty:
            indice = df.iloc[0].to_dict()['R-16-N SP']
            if (indice == 0) or (indice == ""):
                indice = self._extratir_indice()
        else:
            indice = self._extratir_indice()
        
        R_16_N_SP = indice
        R_16_N_SP_VAR = round(((R_16_N_SP - dados_anterior['R-16-N SP']) / dados_anterior['R-16-N SP']) * 100, 2)

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['R-16-N SP'] = R_16_N_SP
            dados['R-16-N SP_VAR'] = R_16_N_SP_VAR

        else:
            novos_dados = {
            'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
            }
            novos_dados['R-16-N SP'] = R_16_N_SP # type: ignore
            novos_dados['R-16-N SP_VAR'] = R_16_N_SP_VAR
            self.arquivo.append(novos_dados)


    
    # def _tratar_retorno(self, entrada):
    #     keys = ["Mês Base", "IPCA Mês", "Fator Composto"]
    #     return {chaves: entrada[chaves] for chaves in keys}

        
if __name__ == "__main__":
    # Exemplo de uso
    indice = SetoriaisSP("01/04/2025", read_only=True)

    print(f"\n\n\n{indice.resultado()}")
    #data = datetime.strptime(x['Mês Base'],"%Y-%m-%d")
    #print(data)
    #print(data - relativedelta(months=1))
    