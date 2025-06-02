import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import sys
from indices_finan import FinanceiroImobme
from datetime import datetime, timedelta
from .credenciais import Credential
import os
from typing import Union
        
class BotImobme():
    def __init__(self, user, password, url):
        """
        Inicializa a classe BotImobme.

        Parameters:
        - user (str): Nome de usuário.
        - password (str): Senha.
        - url (str): URL do site.
        """        
        try:
            self.navegador = webdriver.Chrome()
            self.navegador.maximize_window()
            self.__url:str = url
            self.navegador.get(self.__url)
            sleep(2)
        except Exception as error:
            print(type(error))

        self.roteiro_script = {}
        self.roteiro_script['logar_no_site'] = [
            {'action' : self.escrever, 'kargs' : {'target' : '//*[@id="login"]', 'input' : user}}, #escreve o usuario no campo do usuario
            {'action' : self.escrever, 'kargs' : {'target' : '//*[@id="password"]', 'input' : password}}, #escreve o senha no campo da senha
            {'action' : self.clicar, 'kargs' : {'target' : '//*[@id="btnLogin"]'}}, #clica no botão logar
            {'action' : self.clicar, 'kargs' : {'target' : '/html/body/div[2]/div[3]/div/button[1]/span'}}, #se o usuario já estiver logado clica logoff
            {'action' : self.finalizador_de_emergencia, 'kargs' : {'target' : '/html/body/div[1]/div/div/div/div[2]/form/div/ul/li', 'verific' : {"regra" : "in", "texto": "Senha Inválida"}}}, # faz uma verificação se o login ou a senha está correta caso está incorreto ele encerra todo o script para não bloquear a conta
            {'action' : self.finalizar, 'kargs' : {'target' : '//*[@id="login"]', 'exist' : False}} # se não achar o campo do login ele finaliza o roteiro
        ]
        self.roteiro_script['ir_ate_aba_indice'] = [
            {'action' : self.clicar, 'kargs' : {'target' : '//*[@id="Menu"]/ul/li[5]/a/i'}}, # clicar no icone dos relatorios
            {'action' : self.clicar, 'kargs' : {'target' : '//*[@id="Menu"]/ul/li[5]/div/ul/li[2]/a'}}, # clica no botão gerar relatorios
            {'action' : self.finalizar, 'kargs' : {'target' : '//*[@id="ddlTipoIndice_chosen"]/a', 'exist' : True}} # finaliza o roteiro se achar a lista dos relatorios
        ]
        self.roteiro_script['ir_ate_indice_valores'] = [
            {'action' : self.clicar, 'kargs' : {'target' : '//*[@id="AgreementTabs"]/li[2]/a'}}, # clicar no icone dos relatorios
            {'action' : self.finalizar, 'kargs' : {'target' : '//*[@id="txtVariacao"]', 'exist' : True}} # finaliza o roteiro se achar a lista dos relatorios
        ]
    

    def verificar_indices(self):
        """
        Verifica os índices do site e retorna os dados.

        Returns:
        - dict: Dados dos índices.
        """        
        self.navegador.get(self.__url)

        self.roteiro(self.roteiro_script['logar_no_site'])
        sleep(1)

        # self.roteiro(self.roteiro_script['ir_ate_aba_indice'])
        # sleep(1)

        # self.roteiro(self.roteiro_script['ir_ate_indice_valores'])
        # sleep(1)
        
        self.load_page('Indice/Aprovacao')

        dados = {'indice': [], 'data' : [], 'status' : []}
        linhas = self.navegador.find_element(By.XPATH, '//*[@id="tblIndiceAprovacao"]/tbody').text.split('\n')
        
        for num in range(int((len(linhas) / 2)), int((len(linhas) * 1.20))):
            try:
                indice = self.navegador.find_element(By.XPATH, f'//*[@id="{num}"]/td[1]').text
                data = self.navegador.find_element(By.XPATH, f'//*[@id="{num}"]/td[2]').text[3:]
                status = self.navegador.find_element(By.XPATH, f'//*[@id="{num}"]/td[4]').text

                dados['indice'].append(indice)
                dados['data'].append(data)
                dados['status'].append(status)

            except Exception as error:
                continue
        
        return dados

        #import pdb; pdb.set_trace()

    def execute(self, indices):
        """
        Executa um roteiro de ações no navegador.

        Parameters:
        - indices (list): Lista de ações a serem executadas.

        Returns:
        - None
        """        
        if not indices['indices']:
            return
        
        #self.roteiro(self.roteiro_script['logar_no_site'])
        #import pdb; pdb.set_trace()
        self.load_page('Indice/Aprovacao')
        
        # self.roteiro(self.roteiro_script['ir_ate_aba_indice'])
        # sleep(1)

        # self.roteiro(self.roteiro_script['ir_ate_indice_valores'])
        # sleep(1)

        clicou = False
        for key,indice in indices['indices'].items():
            
            if not clicou:
                self.navegador.find_element(By.XPATH, '//*[@id="ddlIndiceBase_chosen"]/a').click()
                clicou = True
            contador = 0

            #categoria = self.navegador.find_element(By.XPATH, f'//*[@id="ddlIndiceBase_chosen_o_{1}"]').text
            for numero in range(100):
                try:
                    categoria = self.navegador.find_element(By.XPATH, f'//*[@id="ddlIndiceBase_chosen_o_{numero}"]').text
                    if categoria == key:
                        clicou = False
                        print(key)
                        self.roteiro(
                            [
                            {'action' : self.esperar, 'kargs' : {'segundos' : 1}},
                            {'action' : self.clicar, 'kargs' : {'target' : f'//*[@id="ddlIndiceBase_chosen_o_{numero}"]'}},
                            {'action' : self.esperar, 'kargs' : {'segundos' : 1}},
                            {'action' : self.limpar, 'kargs' : {'target' : '//*[@id="txtDataIndice"]'}},
                            {'action' : self.escrever, 'kargs' : {'target' : '//*[@id="txtDataIndice"]', 'input' : indices['data'].replace('/', '')}}, 
                            {'action' : self.limpar, 'kargs' : {'target' : '//*[@id="txtValorIndice"]'}}, 
                            {'action' : self.escrever, 'kargs' : {'target' : '//*[@id="txtValorIndice"]', 'input' : float(indice)}},
                            {'action' : self.esperar, 'kargs' : {'segundos' : 3}},
                            {'action' : self.clicar, 'kargs' : {'target' : '//*[@id="AddNovo"]'}},
                            {'action' : self.esperar, 'kargs' : {'segundos' : 2}},
                            {'action' : self.clicar, 'kargs' : {'target' : '/html/body/div[4]/div[3]/div/button[1]'}},
                            {'action' : self.clicar, 'kargs' : {'target' : '/html/body/div[4]/div[3]/div/button'}},
                            {'action' : self.finalizador_controlado, 'kargs' : ""}
                        ]
                        )
                        break
                except Exception as error:
                    #print(error)
                    pass
                    #print(type(error))
            sleep(5)
        sleep(10)
            

    
    def roteiro(self, roteiro, emergency_break=5*60):
        """
        Executa um roteiro de ações.

        Parameters:
        - roteiro (list): Lista de ações a serem executadas.
        - emergency_break (int): Tempo limite para o script.

        Returns:
        - None
        """        
        contador = 0
        while True:
            for evento in roteiro:
                print(evento['kargs'])
                eventos = evento['action'](evento['kargs'])
                if eventos == "saida":
                    #print("saindo")
                    return
                elif eventos == "emergencia":
                    print("saida de Emergencia")
                    sys.exit()
            
            if contador <= emergency_break:
                contador += 1
            else:
                print("saida de Emergencia")
                sys.exit()
            sleep(1)

    def clicar(self, argumentos):
        try:
            target = self.navegador.find_element(By.XPATH, argumentos['target'])
            target.click()
        except:
            pass
 
    def limpar(self, argumentos):
        try:
            target = self.navegador.find_element(By.XPATH, argumentos['target'])
            target.clear()
        except:
            pass
    
    def esperar(self, argumentos):
        sleep(argumentos['segundos'])

    def debug_click(self, argumentos):
        try:
            target = self.navegador.find_element(By.XPATH, argumentos['target'])
            return "saida"
        except:
            return "saida"

    def escrever(self, argumentos):
        try:
            target = self.navegador.find_element(By.XPATH, argumentos['target'])
            target.send_keys(argumentos['input'])
        except:
            pass
    
    def finalizar(self, argumentos):
        '''
        explicando o termo "exist"
        True: ele vai finalizar a execução se o target for encontrado
        False: ele vai finalizar a execução caso não encontre mais o target 
        '''
        try:
            self.navegador.find_element(By.XPATH, argumentos['target'])
            if argumentos['exist'] == True:
                return "saida"
        except:
            if argumentos['exist'] == False:
                return "saida"
    
    def finalizador_de_emergencia(self, argumentos):
        try:
            target = self.navegador.find_element(By.XPATH, argumentos['target'])
            if argumentos['verific']['regra'] == "in":
                if argumentos['verific']['texto'] in target.text:
                    print(target.text)
                    return  "emergencia"
        except:
            pass

    def finalizador_controlado(self, argumentos):
        return "saida"
    
    def salvar(self, argumentos):
        try:
            target = self.navegador.find_element(By.XPATH, argumentos['target'])
            self.temp_variable = target.text
        except:
            pass
        
    def load_page(self, endpoint:str):
        if not endpoint.endswith('/'):
            endpoint += '/'
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
            
        url = self.__url.replace('Autenticacao/Login', '')
        url = os.path.join(url, endpoint)
        print(f"Carregando página: {url}...          ")  
        self.navegador.get(url)
        
    def esperar_carregamento(self, *, initial_wait:Union[int, float]=1):
        sleep(initial_wait)
        while self.navegador.find_element(By.ID, 'feedback-loader').text == 'Carregando':
            print("Aguardando carregar página...                ", end='\r')
            sleep(1)
        print(end='\r')


if __name__ == "__main__":
    crd:dict = Credential('IMOBME_PRD').load()

    #indices_objetc = FinanceiroImobme("01/11/2023")
    #indices = indices_objetc.montar_dados()
    indices = {'data': '01/10/2024', 'indices': {r'0,8% a.m.': 160.01894193006328, r'0,5% a.m.': 134.21394552729424, 'JUROS 1%': 1067.7927314845247, 'JUROS 0,5%': 134.21394552729424, 'INCC': 1085.0009694, 'CDI': 5968.075764000001, r'CDI 3% a.a.': 1.4556048546535414, 'IPCA': 6735.55, 'IPCA 12a.a.': 166.987285142438, 'POUPA 12': 2.037414751035864, 'POUPA 15': 2.0178751753723887, 'POUPA 28': 2.0186285609530903, 'IGPM': 1191.0094278748784, 'IGPM 0,5%': 1277.7373850627594, 'IGPM 1%': 4245.994763027435}}
    #print(indices)

    #for key,value in indices['indices'].items():
    #    print(f"'{key}'")


    bot = BotImobme(user=crd['login'], password=crd['password'], url=crd['url'])
    print(bot.execute(indices))
    #bot.execute(indices=indices)


    #input("esperando: ")

