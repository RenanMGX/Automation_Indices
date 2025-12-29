import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import Dict, Literal
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from credenciais import Credential

def formatar_data(date:datetime) -> str:

    # Define o fuso horário -03:00
    tz = timezone(timedelta(hours=-3))

    # Cria um datetime com o fuso horário
    dt = datetime(date.year, date.month, 1, 0, 0, 0, tzinfo=tz)

    # Formata no padrão desejado
    formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Ajusta para incluir o ":" no offset (ex.: -03:00)
    formatted_date = formatted_date[:-2] + ":" + formatted_date[-2:]
    
    return formatted_date

class IndiceNotFound(BaseException):
    def __init__(self, text):
        pass

class Indices():
    def __init__(self, data=datetime.now().strftime("%d/%m/%Y"), read_only=True, path="", *, show_all:bool=False):
        """
        Classe para lidar com índices econômicos.

        Args:
        - data (str): Data no formato '%d/%m/%Y'.
        - read_only (bool): Indica se os dados são apenas para leitura.
        - path (str): Caminho para o arquivo de dados.
        """
        self.show_all = show_all
        self.db_path = path
        self.data = datetime.strptime(data, "%d/%m/%Y")
        self.data.replace(day=1)
        self.read_only = read_only
        
        self.__db_config:dict = Credential('MYSQL_DB').load()
    
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
        data_inicial = datetime.strftime((self.data - relativedelta(months=2)), "%d/%m/%Y")
        data_final = datetime.strftime((self.data + relativedelta(months=2)), "%d/%m/%Y")
        #print(data_final)
        
        indice_cdi = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{n_indice}/dados?formato=json&dataInicial={data_inicial}&dataFinal={data_final}", headers=headers)
        if indice_cdi.status_code == 200:
            indice_cdi_dados = indice_cdi.json()
            contador = 0
            valor_temp = []
            #print(indice_cdi_dados)
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
            #navegador.find_element(By.XPATH, '//*[@id="ctl00_content_hpkGratuito"]').click()
            crd:dict = Credential('FVG').load()
            navegador.find_element(By.ID, 'b4-Input1').send_keys(crd['login'])
            navegador.find_element(By.ID, 'b4-Input_Password').send_keys(crd['password'])
            navegador.find_element(By.ID, 'b4-Botao_Entrar').click()
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
    
    def _extrair_indice_ipea(self, *, sercodigo:Literal['IGP12_INCC12', 'PRECOS12_INPC12', 'IGP12_IGPDI12', 'IGP12_IGPM12']|str, date:datetime):
        reqUrl = f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{sercodigo}')"

        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
        }

        payload = ""

        response = requests.request("GET", reqUrl, data=payload,  headers=headersList)

        if response.status_code == 200:
            dados = response.json()['value']
            if not dados:
                raise Exception("Nenhum dado retornado pela API do IPEA.")
            df = pd.DataFrame(dados)
            df = df[df["VALDATA"] == formatar_data(date)]
            return float(df['VALVALOR'].values[0])
        else:
            raise Exception(f"Erro ao conectar na API do IPEA\n{response.status_code} - {response.reason}\n{response.text}")
        

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
            self._calculo(dados=dados, dados_anterior=anterior, novo=False)
        
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
