import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
from typing import List, Tuple


try:
    from IndicesEstrutura import Indices
except ModuleNotFoundError:
    from .IndicesEstrutura import Indices


class INCC(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa uma instância da classe INCC.

        Args:
        - data (str): Data no formato "dd/mm/yyyy" (opcional, padrão: primeiro dia do mês atual).
        - read_only (bool): Indica se a instância deve ser somente leitura (opcional, padrão: True).
        """
        if data is None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_incc.json")

    def valor_incc(self):
        """
        Extrai o valor do INCC de uma fonte web específica.

        Returns:
        - float: Valor do INCC do mês atual.
        """
        tabela = None
        with webdriver.Chrome() as navegador:
            navegador.get("https://extra-ibre.fgv.br/autenticacao_produtos_licenciados/?ReturnUrl=%2fautenticacao_produtos_licenciados%2flista-produtos.aspx")
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="ctl00_content_hpkGratuito"]').click()
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="dlsCatalogoFixo_imbOpNivelUm_1"]').click() #1
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="dlsCatalogoFixo_imbOpNivelDois_4"]').click() #2
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="dlsMovelCorrente_imbOpCorrente_0"]').click() #3
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="dlsMovelCorrente_imbOpCorrente_0"]').click() #4
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="dlsMovelCorrente_imbIncluiItem_0"]').click() #5
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="butCatalogoMovelFecha"]').click() #6
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="cphConsulta_rbtSerieHistorica"]').click() #7
            sleep(1)
            navegador.find_element(By.XPATH, '//*[@id="cphConsulta_butVisualizarResultado"]').click() #8
            sleep(1)
            navegador.get("https://extra-ibre.fgv.br/IBRE/sitefgvdados/VisualizaConsultaFrame.aspx")
            sleep(1)
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

        raise FileNotFoundError("O índice desta data ainda não existe!")


    def registrar_db(self, *, valor, var) -> None:
        with open("db_connection.json", 'r')as _file:
            db_config = json.load(_file)
        
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']            
        )
        
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM incc WHERE mes='{self.data}'")
        resultado:list = cursor.fetchall()
        
        
        #import pdb;pdb.set_trace()
        if (resultado):
            #if not self.read_only:
            print(resultado)
            if resultado[0][1] == valor:
                return
            else:
                cursor.execute(f"UPDATE incc SET valor={valor},variacao={var}  WHERE mes='{self.data}'")
                connection.commit()
                print(f"atualizado")
                return
        else:
            cursor.execute(f"INSERT INTO incc (valor, variacao, mes) VALUES ({valor}, {var}, '{self.data}')")
            connection.commit()
            print("Indice Criado")
        
        connection.close()

    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Calcula os novos valores com base nos dados anteriores.

        Args:
        - dados_anterior (dict): Dados anteriores.
        - dados (dict): Dados atuais.
        - novo (bool): Indica se é um novo cálculo.
        """
        
        
        VALOR_INCC = self.valor_incc()
        
        INDICE = self._extrair_indice(192)
        
        if not self.read_only:
            self.registrar_db(valor=VALOR_INCC, var=INDICE)

        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['INCC'] = VALOR_INCC
            dados['INCC MÊS'] = INDICE
        else:
            novos_dados = {
                'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
                'INCC': VALOR_INCC,
                'INCC MÊS': INDICE
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
        keys = ["Mês Base", "INCC"]
        return {chaves: entrada[chaves] for chaves in keys}

if __name__ == "__main__":
    # Exemplo de uso
    indice = INCC("01/02/2024", read_only=False)
    print(indice.resultado())
