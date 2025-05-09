from ast import pattern
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from io import BytesIO
from time import sleep
try:
    from IndicesEstrutura import Indices
except ModuleNotFoundError:
    from .IndicesEstrutura import Indices
from bs4 import BeautifulSoup
from pdfminer import high_level
import re
import locale
import pandas as pd
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
import pdb


class SetoriaisMG(Indices):
    def __init__(self, data=None, read_only=True):
        """
        Inicializa a classe SetoriaisMG.

        Parameters:
        - data (str): Data no formato 'dd/mm/yyyy'. Se não fornecido, será o primeiro dia do mês atual.
        - read_only (bool): Indica se a instância será somente leitura.
        """        
        if data == None:
            data_temp = datetime(datetime.now().year, datetime.now().month, 1)
            data_nova = datetime.strftime(data_temp, "%d/%m/%Y")
            data = data_nova
        super().__init__(data=data, read_only=read_only, path="db/db_siduscon_mg.json")

    def _str_to_float(self, entrada):
        """
        Converte uma string formatada como número para um float.

        Parameters:
        - entrada (str): String representando um número.

        Returns:
        - float: Valor convertido.
        """        
        return float(entrada.replace('.', '').replace(',','.'))

    def _obter_link_pdf(self):
        """
        Obtém o link do PDF contendo os índices.

        Returns:
        - str: URL do PDF.
        """        
        mes_bruto = self.data.strftime("%B")
        mes = "marco" if mes_bruto == 'marÃ§o' else mes_bruto
        mes = mes.title()

        #
        url = "https://sinduscon-mg.org.br/cub/tabela-do-cub/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            page = requests.get(url, headers=headers)
            if page.status_code != 200:
                raise ConnectionError(f"Não foi possivel se conectar ao site codigo de retorno {page.status_code}")
        except Exception:
            raise ConnectionError("Não foi possivel se conectar ao site!")
        
        soup = BeautifulSoup(page.content, features="html.parser")

        item_s = soup.find_all(class_="item")
        for item in item_s:
            if item.find(class_="alinhatexto").text == str(self.data.year): #type: ignore
                
                for link in item.find_all('a'): #type: ignore
                    print(mes.lower() , link.get('href')) #type: ignore
                    if mes.lower() in (url:=link.get('href')): #type: ignore
                        return url
        #pdb.set_trace()            
        raise FileNotFoundError(f"O Indice desta Data ainda não existe!")
    
    def _extrair_indice_pdf(self):
        """
        Extrai os índices do PDF.

        Returns:
        - dict: Dicionário contendo os índices.
        """        
        pdf_from_url = requests.get(self._obter_link_pdf()) #type: ignore
        pdf_IO = BytesIO(pdf_from_url.content)
        pdf_text = high_level.extract_text(pdf_IO)

        return self._indices_siduscon_mg(pdf_text)


    def _indices_siduscon_mg(self, texto):
        """
        Extrai índices específicos do texto extraído do PDF.

        Parameters:
        - texto (str): Texto extraído do PDF.

        Returns:
        - dict: Dicionário contendo os índices específicos.
        """        
        #residencial
        parametro = r"PROJETOS - PADRÃO RESIDENCIAIS\n\n"
        parametro += r"PADRÃO BAIXO\n\n"
        parametro += r"PADRÃO NORMAL\n\n"
        parametro += r"PADRÃO ALTO\n\n"
        parametro += r"R-1\n\n"
        parametro += r"PP-4\n\n"
        parametro += r"R-8\n\n"
        parametro += r"PIS\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"R-1\n\n"
        parametro += r"PP-4\n\n"
        parametro += r"R-8\n\n"
        parametro += r"R-16\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"R-1\n\n"
        parametro += r"R-8\n\n"
        parametro += r"R-16\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)"

        dados = re.search(parametro, texto).group().split("\n\n") # type: ignore

        indices = {
            "PP-4-B" : self._str_to_float(dados[9]),
            "R-8-B" : self._str_to_float(dados[10]),
            "PP-4-N" : self._str_to_float(dados[17]),
            "R-8-N" : self._str_to_float(dados[18]),
            "R-16-N" : self._str_to_float(dados[19]),
            "R-8-A" : self._str_to_float(dados[24]),
            "R-16-A" : self._str_to_float(dados[25])
        }

        parametro = ""

        #comerciais
        #parametro = r"PROJETOS - PADRÃO COMERCIAIS CAL (Comercial Andares Livres) e CSL (Comercial Salas e Lojas)\n\n"
        parametro += r"PADRÃO NORMAL\n\n"
        parametro += r"PADRÃO ALTO\n\n"

        parametro += r"CAL-8\n\n"
        parametro += r"CSL-8\n\n"
        parametro += r"CSL-16\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"

        parametro += r"CAL-8\n\n"
        parametro += r"CSL-8\n\n"
        parametro += r"CSL-16\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)\n\n"
        parametro += r"([\d.,]+)"

        dados = re.search(parametro, texto).group().split("\n\n")# type: ignore

        indices['CSL-8-N'] = self._str_to_float(dados[6])
        indices['CSL-16-N'] = self._str_to_float(dados[7])
        indices['CSL-16-A'] = self._str_to_float(dados[13])


        # for key,value in indices.items():
        #     print(f"{key} = {value}")
        # print("####################################")
        
        return indices
        #import pdb; pdb.set_trace()
    
    def _calculo(self, dados_anterior, dados, novo=False):
        """
        Realiza cálculos com base nos índices.

        Parameters:
        - dados_anterior (dict): Dados anteriores para cálculos de variação.
        - dados (dict): Dados a serem atualizados ou criados.
        - novo (bool): Indica se é um novo conjunto de dados.

        Returns:
        - None
        """   
        
        #import pdb; pdb.set_trace()
        df = pd.DataFrame(self.arquivo)
        df = df[df['Mês Base'] == self.data.strftime('%Y-%m-%d')]
        if not df.empty:
            indices = df.iloc[0].to_dict()
            if (indices == 0) or (indices == ""):
                indices = indices = self._extrair_indice_pdf()
        else:
            indices = self._extrair_indice_pdf()

        PP_4_B = indices['PP-4-B']
        PP_4_B_VAR = round(((PP_4_B - dados_anterior['PP-4-B']) / dados_anterior['PP-4-B']) * 100, 3)
        
        R_8_B = indices['R-8-B']
        R_8_B_VAR = round(((R_8_B - dados_anterior['R-8-B']) / dados_anterior['R-8-B']) * 100, 3)

        PP_4_N = indices['PP-4-N']
        PP_4_N_VAR = round(((PP_4_N - dados_anterior['PP-4-N']) / dados_anterior['PP-4-N']) * 100, 3)

        R_8_N = indices['R-8-N']
        R_8_N_VAR = round(((R_8_N - dados_anterior['R-8-N']) / dados_anterior['R-8-N']) * 100, 3)

        R_16_N = indices['R-16-N']
        R_16_N_VAR = round(((R_16_N - dados_anterior['R-16-N']) / dados_anterior['R-16-N']) * 100, 3)

        R_8_A = indices['R-8-A']
        R_8_A_VAR = round(((R_8_A - dados_anterior['R-8-A']) / dados_anterior['R-8-A']) * 100, 3)

        R_16_A = indices['R-16-A']
        R_16_A_VAR = round(((R_16_A - dados_anterior['R-16-A']) / dados_anterior['R-16-A']) * 100, 3)

        CSL_8_N = indices['CSL-8-N']
        CSL_8_N_VAR = round(((CSL_8_N - dados_anterior['CSL-8-N']) / dados_anterior['CSL-8-N']) * 100, 3)

        CSL_16_N = indices['CSL-16-N']
        CSL_16_N_VAR = round(((CSL_16_N - dados_anterior['CSL-16-N']) / dados_anterior['CSL-16-N']) * 100, 3)

        CSL_16_A = indices['CSL-16-A']
        CSL_16_A_VAR = round(((CSL_16_A - dados_anterior['CSL-16-A']) / dados_anterior['CSL-16-A']) * 100, 3)



        if not novo:
            dados['Mês Base'] = datetime.strftime(self.data, "%Y-%m-%d")
            dados['PP-4-B'] = PP_4_B
            dados['PP-4-B_VAR'] = PP_4_B_VAR
            dados['R-8-B'] = R_8_B
            dados['R-8-B_VAR'] = R_8_B_VAR
            dados['PP-4-N'] = PP_4_N
            dados['PP-4-N_VAR'] = PP_4_N_VAR
            dados['R-8-N'] = R_8_N
            dados['R-8-N_VAR'] = R_8_N_VAR
            dados['R-16-N'] = R_16_N
            dados['R-16-N_VAR'] = R_16_N_VAR
            dados['R-8-A'] = R_8_A
            dados['R-8-A_VAR'] = R_8_A_VAR
            dados['R-16-A'] = R_16_A
            dados['R-16-A_VAR'] = R_16_A_VAR
            dados['CSL-8-N'] = CSL_8_N
            dados['CSL-8-N_VAR'] = CSL_8_N_VAR
            dados['CSL-16-N'] = CSL_16_N
            dados['CSL-16-N_VAR'] = CSL_16_N_VAR
            dados['CSL-16-A'] = CSL_16_A
            dados['CSL-16-A_VAR'] = CSL_16_A_VAR

        else:
            novos_dados: dict = {
            'Mês Base': datetime.strftime(self.data, "%Y-%m-%d"),
            }
            novos_dados['PP-4-B'] = PP_4_B
            novos_dados['PP-4-B_VAR'] = PP_4_B_VAR
            novos_dados['R-8-B'] = R_8_B
            novos_dados['R-8-B_VAR'] = R_8_B_VAR
            novos_dados['PP-4-N'] = PP_4_N
            novos_dados['PP-4-N_VAR'] = PP_4_N_VAR
            novos_dados['R-8-N'] = R_8_N
            novos_dados['R-8-N_VAR'] = R_8_N_VAR
            novos_dados['R-16-N'] = R_16_N
            novos_dados['R-16-N_VAR'] = R_16_N_VAR
            novos_dados['R-8-A'] = R_8_A
            novos_dados['R-8-A_VAR'] = R_8_A_VAR
            novos_dados['R-16-A'] = R_16_A
            novos_dados['R-16-A_VAR'] = R_16_A_VAR
            novos_dados['CSL-8-N'] = CSL_8_N
            novos_dados['CSL-8-N_VAR'] = CSL_8_N_VAR
            novos_dados['CSL-16-N'] = CSL_16_N
            novos_dados['CSL-16-N_VAR'] = CSL_16_N_VAR
            novos_dados['CSL-16-A'] = CSL_16_A
            novos_dados['CSL-16-A_VAR'] = CSL_16_A_VAR
            self.arquivo.append(novos_dados)


    
    # def _tratar_retorno(self, entrada):
    #     keys = ["Mês Base", "IPCA Mês", "Fator Composto"]
    #     return {chaves: entrada[chaves] for chaves in keys}

        
if __name__ == "__main__":
    # Exemplo de uso
    indice = SetoriaisMG("01/03/2025", read_only=True)

    print(f"\n\n\n{indice.resultado()}")
    #data = datetime.strptime(x['Mês Base'],"%Y-%m-%d")
    #print(data)
    #print(data - relativedelta(months=1))
    