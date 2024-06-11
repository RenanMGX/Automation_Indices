import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import Dict

class IndiceNotFound(BaseException):
    def __init__(self, text):
        pass

class Indices():
    def __init__(self, data=datetime.now().strftime("%d/%m/%Y"), read_only=True, path=""):
        """
        Classe para lidar com índices econômicos.

        Args:
        - data (str): Data no formato '%d/%m/%Y'.
        - read_only (bool): Indica se os dados são apenas para leitura.
        - path (str): Caminho para o arquivo de dados.
        """
        self.db_path = path
        self.data = datetime.strptime(data, "%d/%m/%Y")
        self.data.replace(day=1)
        self.read_only = read_only
        
        with open("db_connection.json", 'r')as _file:
            self.__db_config = json.load(_file)
    
    @property
    def db_config(self):
        return self.__db_config

    def _ler_arquivo(self):
        """
        Lê o arquivo JSON com os dados.

        Returns:
        - dict: Dicionário contendo os dados.
        """
        with open(self.db_path, 'r', encoding="utf-8")as arqui:
            return json.load(arqui)
    
    def _gravar_arquivo(self, arquivo, encoding="utf-8"):
        """
        Grava os dados no arquivo JSON.

        Args:
        - arquivo (dict): Dicionário contendo os dados a serem gravados.
        - encoding (str): Codificação do arquivo.
        """
        with open(self.db_path, 'w')as arqui:
            json.dump(arquivo, arqui)
        
    def _extrair_indice(self, n_indice, timeout=5) -> float:
        """
        Extrai o valor de um índice econômico de uma API.

        Args:
        - n_indice (int): Número do índice.
        - timeout (int): Tempo máximo de tentativas de conexão.

        Returns:
        - float: Valor do índice.
        """
        data = datetime.strftime(self.data, "%d/%m/%Y")
        cont = 0
        while cont < timeout:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                indice_cdi = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{n_indice}/dados?formato=json&dataInicial={data}&dataFinal={data}", headers=headers)
                indice_cdi_dados = indice_cdi.json()[0]
                if data == indice_cdi_dados['data']:               
                    return float(indice_cdi_dados['valor'])
                else:
                    raise FileNotFoundError("O Indice desta Data ainda não existe!")

            except FileNotFoundError as error:
                raise FileNotFoundError(error)
            
            except:
                cont += 1
                sleep(1)

        raise TimeoutError("Tempo excedido! Não foi possível se conectar à API do BCB")

    def _extrair_indice_dias(self, n_indice, timeout=5) -> float:
        """
        Extrai os índices de todos os dias do mês e calcula a média.

        Args:
        - n_indice (int): Número do índice.
        - timeout (int): Tempo máximo de tentativas de conexão.

        Returns:
        - float: Média dos índices do mês.
        """
        #data = datetime.strftime(self.data, "%d/%m/%Y")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        indice_cdi = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{n_indice}/dados?formato=json", headers=headers)
        if indice_cdi.status_code == 200:
            indice_cdi_dados = indice_cdi.json()
            contador = 0
            valor_temp = []
            for indice in indice_cdi_dados:
                data_para_teste = datetime.strptime(indice['data'], "%d/%m/%Y")
                if (data_para_teste.month == self.data.month) and (data_para_teste.year == self.data.year):
                    contador += 1
                    valor_temp.append((float(indice['valor']) / 100) + 1)
            novo_valor_temp = 0.0
            for value in valor_temp:
                if novo_valor_temp == 0.0:
                    novo_valor_temp = value
                else:
                    novo_valor_temp *= value

            if novo_valor_temp:
                return (novo_valor_temp - 1) * 100
            else:
                raise FileNotFoundError("O Indice desta Data ainda não existe!")
        else:
            raise TimeoutError("Tempo excedido! Não foi possível se conectar à API do BCB")

    def _extrair_fgv(self, pesquisa, caminho_click):
        """
        Extrai dados de uma tabela da FGV usando Selenium.

        Args:
        - pesquisa (str): Termo de pesquisa na FGV.
        - caminho_click (str): Caminho XPath para clicar.

        Returns:
        - float: Valor do índice.
        """
        tabela = None
        with webdriver.Chrome()as navegador:
            navegador.get("https://extra-ibre.fgv.br/autenticacao_produtos_licenciados/?ReturnUrl=%2fautenticacao_produtos_licenciados%2flista-produtos.aspx")
            sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="ctl00_content_hpkGratuito"]').click()
            sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="txtBuscarSeries"]').clear()
            navegador.find_element(By.XPATH, '//*[@id="txtBuscarSeries"]').send_keys(pesquisa)
            navegador.find_element(By.XPATH, '//*[@id="txtBuscarSeries"]').send_keys(Keys.RETURN)
            sleep(2)
            navegador.find_element(By.XPATH, caminho_click).click()
            sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="butBuscarSeriesOK"]').click()
            sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="cphConsulta_rbtSerieHistorica"]').click()
            sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="cphConsulta_butVisualizarResultado"]').click()
            sleep(2)
            navegador.get("https://extra-ibre.fgv.br/IBRE/sitefgvdados/VisualizaConsultaFrame.aspx")
            sleep(2)
            tabela = navegador.find_element(By.XPATH, '//*[@id="xgdvConsulta_DXMainTable"]/tbody').text.split("\n")
        tabela.pop(0)
        tabela.pop(0)

        for indice in tabela:
            try:
                data = datetime.strptime(indice.split(" ")[0], "%m/%Y")
                valor = float(indice.split(" ")[1].replace(",", "."))
                if (data.month == self.data.month) and (data.year == self.data.year):
                    return valor
            except:
                continue
        
        raise FileNotFoundError("O Indice desta Data ainda não existe!")

    def valor_inpc(self):
        """
        Obtém o valor do índice INPC.

        Returns:
        - float: Valor do índice INPC.
        """
        return self._extrair_fgv(pesquisa="INPC", caminho_click='//*[@id="dlsSerie_chkSerieEscolhida_1"]')

    def valor_igp_di(self):
        """
        Obtém o valor do índice IGP-DI.

        Returns:
        - float: Valor do índice IGP-DI.
        """
        return self._extrair_fgv(pesquisa="IGP DI", caminho_click='//*[@id="dlsSerie_chkSerieEscolhida_3"]')

    def valor_igp_m(self):
        """
        Obtém o valor do índice IGP-M.

        Returns:
        - float: Valor do índice IGP-M.
        """
        return self._extrair_fgv(pesquisa="IGP-M", caminho_click='//*[@id="dlsSerie_chkSerieEscolhida_3"]')

    def _calculo(self, dados_anterior, dados="", novo=False):
        """
        Realiza um cálculo.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        print(dados)
        print(dados_anterior)
        print("#" * len(str(dados_anterior)))
        
    def resultado(self) -> dict:
        """
        Calcula o resultado com base nos dados existentes.
        
        Returns:
        - dict: Resultado do cálculo.
        """
        self.arquivo:list = self._ler_arquivo()
        key_data = list(self.arquivo[0].keys())[0]

        anterior:dict = {}
        existe:bool = False
        contador = 1
        for dados in self.arquivo:
            ano = datetime.strptime(dados[key_data], '%Y-%m-%d').year
            mes = datetime.strptime(dados[key_data], '%Y-%m-%d').month
            
            if (ano == self.data.year) and (mes == self.data.month):
                if contador == 1:
                    return self._tratar_retorno(dados)
                existe = True
                self._calculo(dados=dados, dados_anterior=anterior)
                break

            anterior = dados
            contador += 1
        if not existe:
            if not (self.data - relativedelta(months=1)).month == datetime.strptime(anterior[key_data], '%Y-%m-%d').month:
                raise ValueError("Dados do Indice Inexistentes!")
            self._calculo(dados=dados, dados_anterior=anterior, novo=True)
        
        if not self.read_only:
            self._gravar_arquivo(self.arquivo)

        for dados in self.arquivo:
            ano = datetime.strptime(dados[key_data], '%Y-%m-%d').year
            mes = datetime.strptime(dados[key_data], '%Y-%m-%d').month
            if (ano == self.data.year) and (mes == self.data.month):
                result:dict = self._tratar_retorno(dados)
                return result
        raise Exception("sem dados a serem divulgados")
    
    def _tratar_retorno(self, entrada) -> dict:
        """
        Trata o resultado antes de retorná-lo.

        Args:
        - entrada (dict): Dados de entrada.

        Returns:
        - dict: Dados tratados.
        """
        return entrada
        
if __name__ == "__main__":
    indice = Indices()

    prestult = indice.resultado()
    
    #data = datetime.strptime(x['Mês Base'],"%Y-%m-%d")
    #print(data)
    #print(data - relativedelta(months=1))
