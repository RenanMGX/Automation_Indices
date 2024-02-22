import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import pandas as pd
from io import BytesIO
from time import sleep
try:
    from IndicesEstrutura import Indices
except ModuleNotFoundError:
    from .IndicesEstrutura import Indices
from pdfminer import high_level
import re
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

class SetoriaisRJ(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa a classe SetoriaisRJ.

        Parameters:
        - data (str): Data no formato 'dd/mm/yyyy'. Se não fornecido, será o primeiro dia do mês atual.
        - read_only (bool): Indica se a instância será somente leitura.
        """        
        if data == None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_siduscon_rj.json")

    def _str_to_float(self, entrada:str):
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
        Obtém o arquivo PDF contendo os índices do site.

        Returns:
        - str: Texto extraído do arquivo PDF.
        """
        caminho_download = f"{os.getcwd()}\\download_indice_rj"
        if caminho_download[-1] != "\\":
            caminho_download += "\\"
        if not os.path.exists(caminho_download):
            os.makedirs(caminho_download)
        for arquivo in os.listdir(caminho_download):
            os.unlink(caminho_download + arquivo)

        prefs = {"download.default_directory" : caminho_download}
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", prefs)

        url = "http://www.cub.org.br/cub-m2-estadual/RJ/"
        with webdriver.Chrome(options=chrome_options) as NAVEGADOR:
            NAVEGADOR.get(url)

            NAVEGADOR.find_element(By.XPATH, '//*[@id="uf"]').click()
            NAVEGADOR.find_element(By.XPATH, '//*[@id="uf"]/option[18]').click()

            sleep(1)

            ano_s = NAVEGADOR.find_element(By.ID, 'ano')
            ano_s = ano_s.find_elements(By.TAG_NAME, 'option')

            for ano in ano_s:
                if ano.text == str(self.data.year):
                    ano.click()
            
            mes_s = NAVEGADOR.find_element(By.ID, 'mes')
            mes_s = mes_s.find_elements(By.TAG_NAME, 'option')
            for mes in mes_s:
                if mes.get_attribute('value') == str(self.data.month):
                    mes.click()

            NAVEGADOR.find_element(By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div[1]/div[2]/div/form/input[2]').click()
            sleep(1)

            if NAVEGADOR.find_element(By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div[1]/div[1]').text == "Erro: Relatório ainda não foi publicado":
                raise FileNotFoundError("O Indice desta Data ainda não existe!")

            for x in range(5*60):
                if len(os.listdir(caminho_download)) > 0:
                    sleep(2)
                    break
                sleep(1)

        if len(os.listdir(caminho_download)) > 0:
            for arquivo in os.listdir(caminho_download):
                arquivo_pdf = high_level.extract_text(caminho_download + arquivo)
                os.unlink(caminho_download + arquivo)
        else:
            os.rmdir(caminho_download)
            raise FileNotFoundError("Arquivo não encontrado")
        os.rmdir(caminho_download)

        return arquivo_pdf
    
    def _extratir_indice(self):
        """
        Extrai o índice específico do texto extraído do PDF.

        Returns:
        - dict: Dicionário contendo o índice extraído.
        """        
        texto = self._obter_arquivo()

        parametro = r"R-1\n\n"
        parametro += r"R-8\n\n"
        parametro += r"R-16\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)"

        dados = re.search(parametro, texto).group().split("\n\n")# type: ignore

        indices = {
            "R-16-A RJ" : self._str_to_float(dados[5]),
        }

        # for key,value in indices.items():
        #     print(f"{key} = {value}")
        # print("####################################")
        return indices
        #import pdb; pdb.set_trace()

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
        indice = self._extratir_indice()
        

        R_16_N_RJ = indice['R-16-A RJ']
        R_16_N_RJ_VAR = round(((R_16_N_RJ - dados_anterior['R-16-A RJ']) / dados_anterior['R-16-A RJ']) * 100, 2)

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['R-16-A RJ'] = R_16_N_RJ
            dados['R-16-A RJ_VAR'] = R_16_N_RJ_VAR

        else:
            novos_dados: dict = {
            'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
            }
            novos_dados['R-16-A RJ'] = R_16_N_RJ
            novos_dados['R-16-A RJ_VAR'] = R_16_N_RJ_VAR
            self.arquivo.append(novos_dados)


    
    # def _tratar_retorno(self, entrada):
    #     keys = ["Mês Base", "R-16-A RJ", "R-16-A RJ_VAR"]
    #     return {chaves: entrada[chaves] for chaves in keys}

        
if __name__ == "__main__":
    # Exemplo de uso
    indice = SetoriaisRJ("01/01/2024", read_only=True)

    print(f"\n\n\n{indice.resultado()}")
    #data = datetime.strptime(x['Mês Base'],"%Y-%m-%d")
    #print(data)
    #print(data - relativedelta(months=1))
    