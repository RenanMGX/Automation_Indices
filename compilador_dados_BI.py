import os
import json
from numpy import record
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from getpass import getuser

class CompiladorBI:
    def __init__(self, arquivos):
        """
        Inicializa o CompiladorBI.

        Parameters:
            arquivos (str or list): Uma lista de caminhos dos arquivos ou um único caminho.
        """        
        self.arquivos = arquivos if type(arquivos) == list else [arquivos] if type(arquivos) == str else None

    def _carregar_dados(self):
        """
        Carrega os dados dos arquivos.

        Raises:
            ValueError: Se arquivos não for uma lista.

        Returns:
            list: Lista contendo os dados carregados de cada arquivo.
        """        
        if self.arquivos == None:
            raise ValueError("apenas listas são permitidas!")
        
        dados = []
        for arquivo in self.arquivos:
            with open(arquivo, 'r', encoding='utf-8')as file:
                dados.append(json.load(file))
        return dados
    
    def tratar_setoriais(self):
        """
        Trata os dados referentes a índices setoriais.

        Returns:
            list: Lista formatada com os dados tratados.
        """        
        dados = self._carregar_dados()

        dados_finais = [['Data','Indice', "Valor", "VAR"]]

        for base in dados:
            for linhas in base:
                #print(list(linhas.keys()))
                data = linhas['Mês Base']
                del linhas['Mês Base']
                #colunas = [x for x in list(linhas.keys()) if not "_VAR" in x]
                linha = list(linhas.values())
                
                for key,value in linhas.items():
                    if "_VAR" in key:
                        try:
                            dados_finais.append([data, key.replace("_VAR", ""), linha.pop(0), linha.pop(0)])
                        except:
                            pass

        return dados_finais

    def tratar_financeiro(self):
        """
        Trata os dados referentes a índices financeiros.

        Returns:
            list: Lista formatada com os dados tratados.
        """        
        dados = self._carregar_dados()

        dados_finais = [['Data','Indice', "Valor", "VAR", "ANO_VAR", "12_MESES_VAR"]]

        for base in dados:
            for linhas in base:
                #print(list(linhas.keys()))
                data = linhas['Mês Base']
                del linhas['Mês Base']
                #colunas = [x for x in list(linhas.keys()) if not "_VAR" in x]
                linha = list(linhas.values())
                
                for key,value in linhas.items():
                    if "INCC" == key:
                        try:
                            dados_finais.append([data, key, linha.pop(0), linha.pop(0), linha.pop(0), linha.pop(0)])
                            continue
                        except:
                            pass
                    if "INCC_MES_VAR" == key:
                        continue
                    if "INCC_ANO_VAR" == key:
                        continue
                    if "INCC_12_MESES_VAR" == key:
                        continue
                    if "SALARIO MINIMO" == key:
                        try:
                            dados_finais.append([data, key, linha.pop(0)])
                            continue
                        except:
                            pass

                    if "POUP_VAR" == key:
                        try:
                            dados_finais.append([data, key.replace("POUP_VAR", "POUPANÇA"), linha.pop(0)])
                            continue
                        except:
                            pass

                    elif "_VAR" in key:
                        try:
                            dados_finais.append([data, key.replace("_VAR", ""), linha.pop(0), linha.pop(0)])
                            continue
                        except:
                            pass

        return dados_finais

def compilador_fabric_setoriais(entrada, saida):
    """
    Compila índices setoriais a partir de arquivos JSON e salva em um novo arquivo JSON.

    Parameters:
        entrada (list): Lista de caminhos dos arquivos de entrada.
        saida (str): Caminho do arquivo de saída.

    Returns:
        None
    """    
    bot = CompiladorBI(entrada)

    dados = bot.tratar_setoriais()

    df = pd.DataFrame(dados).replace(float("nan"), None)
    df.columns = df.iloc[0]
    df = df[1:]
    df.to_json(saida, date_format="iso", index=False, orient="records")

def compilador_fabric_financeiro(entrada, saida):
    """
    Compila índices financeiros a partir de arquivos JSON e salva em um novo arquivo JSON.

    Parameters:
        entrada (list): Lista de caminhos dos arquivos de entrada.
        saida (str): Caminho do arquivo de saída.

    Returns:
        None
    """    
    bot = CompiladorBI(entrada)

    dados = bot.tratar_financeiro()

    df = pd.DataFrame(dados).replace(float("nan"), None).replace("", None)
    df.columns = df.iloc[0]
    df = df[1:]
    df.to_json(saida, date_format="iso", index=False, orient="records")


if __name__ == "__main__":

    # Exemplo de uso para compilar índices setoriais
    compilador_fabric_setoriais(entrada=["db/db_siduscon_mg.json", "db/db_siduscon_rj.json", "db/db_siduscon_sp.json"], saida=f"C:/Users/{getuser()}/OneDrive - PATRIMAR ENGENHARIA S A/Documentos - RPA/RPA - Dados/Indices/indices.json")

    # Exemplo de uso para compilar índices financeiros
    compilador_fabric_financeiro(entrada=["db/db_setoriais_fin.json"], saida=f"C:/Users/{getuser()}/OneDrive - PATRIMAR ENGENHARIA S A/Documentos - RPA/RPA - Dados/Indices/indices_financeiros.json")

