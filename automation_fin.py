import sys
sys.path.append("Entities")  # Adiciona o caminho do diretório "Entities" ao path do sistema
import os
from Entities.imobme_up import Crendenciais, BotImobme
from Entities.indices_finan import FinanceiroImobme
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from time import sleep
from shutil import copy2
from copy import deepcopy


class AutomationFin:
    def __init__(self, date, antecipar=False):
        """
        Inicializa a classe AutomationFin.

        Parâmetros:
        - date: data no formato datetime para a qual as operações serão realizadas.
        """
        try:
            self.date = datetime.strptime(date, "%d/%m/%Y")
        except ValueError:
            self.date = datetime.now()
        except TypeError:
            self.date = datetime.now()
        if antecipar:
            self.__indices = [
                r'0,8% a.m.',
                r'0,5% a.m.',
                r'JUROS 1%',
                r'JUROS 0,5%'
            ]
        else:
            self.__indices = [
                r'0,8% a.m.',
                r'0,5% a.m.',
                r'JUROS 1%',
                r'JUROS 0,5%',
                'INCC',
                'CDI',
                r'CDI 3% a.a.',
                'IPCA',
                'IPCA 12a.a.',
                'POUPA 12',
                'POUPA 15',
                'POUPA 28',
                'IGPM',
                'IGPM 0,5%',
                'IGPM 1%',
            ]

    def verificar_indices_do_mes(self, data):
        """
        Verifica os índices do mês e retorna uma lista dos índices aprovados ou pendentes.

        Parâmetros:
        - data: dados contendo informações dos índices.

        Retorna:
        - Lista dos índices verificados.
        """
        indices_verificados = []
        df = pd.DataFrame(data)
        for indice in self.__indices:
            df_indice_a = df[df['indice'] == indice]
            df_indice_a = df_indice_a[df_indice_a['data'] == self.date.strftime('%m/%Y')]
            df_indice_a = df_indice_a[df_indice_a['status'] == 'Aprovado']

            df_indice_p = df[df['indice'] == indice]
            df_indice_p = df_indice_p[df_indice_p['data'] == self.date.strftime('%m/%Y')]
            df_indice_p = df_indice_p[df_indice_p['status'] == 'Pendente']
            if (df_indice_p.empty) and (df_indice_a.empty):
                indices_verificados.append(indice)
                continue

        return indices_verificados
    
    def comparar_indices(self, date, pendentes, disponivel):
        """
        Compara índices pendentes com índices disponíveis e retorna uma lista de retorno.

        Parâmetros:
        - date: data associada aos índices.
        - pendentes: lista de índices pendentes.
        - disponivel: dicionário de índices disponíveis.

        Retorna:
        - Dicionário contendo data e índices correspondentes.
        """
        lista_de_retorno = {'data': date, 'indices': {}}
        for pendente in pendentes:
            if pendente in disponivel:
                lista_de_retorno['indices'][pendente] = disponivel[pendente]
        return lista_de_retorno
    
    def salvar_excel(self, indices, caminho="\\\\server008\\G\\ARQ_PATRIMAR\\WORK\\Indices", nome_arquivo="Indices Financeiros"):
        """
        Salva os índices em um arquivo Excel.

        Parâmetros:
        - indices: dicionário contendo data e índices.
        - caminho: caminho para o diretório do arquivo Excel.
        - nome_arquivo: nome do arquivo Excel.

        Retorna:
        - None
        """
        if not caminho[-1:] == "\\":
            caminho += "\\"
        if not nome_arquivo[-5:] == ".xlsx":
            nome_arquivo += ".xlsx"

        atual = {
            'data': [],
            'indice': [],
            'valor': []
        }

        historico = deepcopy(atual)

        for key, value in indices['indices'].items():
            atual['data'].append(indices['data'])
            atual['indice'].append(key)
            atual['valor'].append(value)
        try:
            for key, value in indices['errors'].items():
                atual['data'].append(indices['data'])
                atual['indice'].append(key)
                atual['valor'].append(value)
        except:
            pass
        
        atual = pd.DataFrame(atual)
        historico = pd.DataFrame(historico)

        try:
            arquivo_temp = "indices_temp.xlsx"
            copy2(caminho + nome_arquivo, arquivo_temp)
            df_temp = pd.read_excel(arquivo_temp, sheet_name=None)

            try:
                df_temp['Historico']
                historico = pd.concat([historico, df_temp['Historico']], ignore_index=True)
            except KeyError:
                pass

            data_atual = datetime.strptime(atual['data'].values[0], '%d/%m/%Y').replace(day=1)
            try:
                data_salva = datetime.strptime(df_temp['Atual']['data'].values[0], '%d/%m/%Y').replace(day=1)
            except TypeError:
                data_salva = datetime.fromisoformat(str(df_temp['Atual']['data'].values[0])).replace(day=1)

            if data_atual == data_salva:
                for x in range(5*60):
                    try:
                        with pd.ExcelWriter(caminho + nome_arquivo) as writer:
                            atual.to_excel(writer, sheet_name="Atual", index=False)
                            historico.to_excel(writer, sheet_name="Historico", index=False)
                            break
                    except PermissionError:
                        print("Arquivo está aberto, Favor fechar!")
                        sleep(1)
                    

            else:
                historico = pd.concat([historico, df_temp['Atual']], ignore_index=True)   
                for x in range(5*60):
                    try:
                        with pd.ExcelWriter(caminho + nome_arquivo) as writer:
                            atual.to_excel(writer, sheet_name="Atual", index=False)
                            historico.to_excel(writer, sheet_name="Historico", index=False)
                            break
                    except PermissionError:
                        print("Arquivo está aberto, Favor fechar!")
                        sleep(1)

        except FileNotFoundError:
            for x in range(5*60):
                try:
                    atual.to_excel(caminho + nome_arquivo, sheet_name='Atual', index=False)
                    break
                except PermissionError:
                    print("Arquivo está aberto, Favor fechar!")
                    sleep(1)
        finally:
            try:
                os.unlink(arquivo_temp)
            except:
                pass
        
if __name__ == "__main__":
    # Configuração da data
    dateBrute = (datetime.now() - relativedelta(months=1)).replace(day=1)
    date = dateBrute.strftime('%d/%m/%Y')
    #date = "01/02/2024"

    
    # Carregamento de credenciais
    credencial = Crendenciais(mod='prd')
    login = credencial.load()['login']
    senha = credencial.load()['pass']
    url = credencial.load()['url']

    # Inicialização da automação financeira
    auto = AutomationFin(date)

    # Carregamento dos índices disponíveis
    indice_finan = FinanceiroImobme(date)
    indice_disponivel = indice_finan.montar_dados(read_only=False)
    # indice_disponivel = {'data': date, 'indices': {r'0,8% a.m.': 160.01894193006328, ...}}
    auto.salvar_excel(indices=indice_disponivel)

    # Inicialização do bot para verificar índices
    bot = BotImobme(user=login, password=senha, url=url)
    dados = bot.verificar_indices()
    
    
    for mes in range(3):
        data = dateBrute + relativedelta(months=mes+1)
        data = data.strftime('%d/%m/%Y')
        
        indice_antecipado = FinanceiroImobme.indices_antecipados(data, read_only=False)
        
        auto_antecipado = AutomationFin(data, antecipar=True)
        indices_pendentes_antecipado = auto_antecipado.verificar_indices_do_mes(dados)
        if not indices_pendentes_antecipado:
            print("nenhum indice para antecipar!")
            continue
        
        indices_para_subir_antecipado = auto_antecipado.comparar_indices(date=data, pendentes=indices_pendentes_antecipado, disponivel=indice_antecipado['indices'])
        bot.execute(indices=indice_antecipado)


    # Verificação dos índices pendentes
    indices_pendentes = auto.verificar_indices_do_mes(dados)
    if not indices_pendentes:
        print("nenhum indice para faltante!")
        sys.exit()

    # Comparação e execução dos índices pendentes
    indices_para_subir = auto.comparar_indices(date=date, pendentes=indices_pendentes, disponivel=indice_disponivel['indices'])
    bot.execute(indices=indices_para_subir)
        
    bot.navegador.quit()
    print(indices_para_subir)
    
    
    
    #import pdb; pdb.set_trace()
