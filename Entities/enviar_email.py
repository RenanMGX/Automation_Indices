from getpass import getuser
import json
import os
from getpass import getuser
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from time import sleep
from typing import Dict, List

class CheckIndiceList:
    def __init__(
            self,
            date: datetime,
            db_email:str = "db/db_email.json",
            db_setoriais_fin: str = "db/db_setoriais_fin.json",
            db_siduscon_mg: str = "db/db_siduscon_mg.json",
            db_siduscon_rj: str = "db/db_siduscon_rj.json",
            db_siduscon_sp: str = "db/db_siduscon_sp.json"
    ) -> None:
        """Metodo construtur da classe

        Args:
            date (datetime): data
            db_email (str, optional): caminho do arquivo. Defaults to "db/db_email.json".
            db_setoriais_fin (str, optional): caminho do arquivo. Defaults to "db/db_setoriais_fin.json".
            db_siduscon_mg (str, optional): caminho do arquivo. Defaults to "db/db_siduscon_mg.json".
            db_siduscon_rj (str, optional): caminho do arquivo. Defaults to "db/db_siduscon_rj.json".
            db_siduscon_sp (str, optional): caminho do arquivo. Defaults to "db/db_siduscon_sp.json".
        """
        
        self.date: datetime = date.replace(day=1).replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
        self.dateStr: str = self.date.strftime("%Y-%m-%d")

        self.__email_db_caminho: str = db_email
        self.__caminhos: dict = {
            "setoriais_fin" : db_setoriais_fin,
            "siduscon_mg" : db_siduscon_mg,
            "siduscon_rj" : db_siduscon_rj,
            "siduscon_sp" : db_siduscon_sp
        }
        
        self.indices_enviados: dict = self._verificarIndicesEnviados(self.__email_db_caminho)
        self.indices_finan_db: dict = self._consultarDB(self.__caminhos['setoriais_fin'], modulo="finan")
        self.indices_siduscon_mg_db: dict = self._consultarDB(self.__caminhos['siduscon_mg'], modulo="siduscon_mg")
        self.indices_siduscon_rj_db: dict = self._consultarDB(self.__caminhos['siduscon_rj'], modulo="siduscon_rj")
        self.indices_siduscon_sp_db: dict = self._consultarDB(self.__caminhos['siduscon_sp'], modulo="siduscon_sp")

        self.enviar_finan: dict = self._comparar(enviados=self.indices_enviados, db=self.indices_finan_db, modulo="finan")
        self.enviar_siduscon_mg: dict = self._comparar(enviados=self.indices_enviados, db=self.indices_siduscon_mg_db, modulo="siduscon_mg")
        self.enviar_siduscon_rj: dict = self._comparar(enviados=self.indices_enviados, db=self.indices_siduscon_rj_db, modulo="siduscon_rj")
        self.enviar_siduscon_sp: dict = self._comparar(enviados=self.indices_enviados, db=self.indices_siduscon_sp_db, modulo="siduscon_sp")

        
    def _verificarIndicesEnviados(self, caminho: str) -> dict:
        """verifica os indice que ja foram enviados para o mes informado,
        caso não encontrado ele criar um novo arquivo json


        Args:
            caminho (str): caminho do arquivo db

        Returns:
            dict: dicionario com a informação dos indices enviados
        """
        #cria um arquivo db_email.json caso não exista
        retornoDoZero: dict = {self.dateStr: {"finan": {}, "siduscon_mg": {}, "siduscon_rj": {}, "siduscon_sp": {}}}
        if not os.path.exists(caminho):
            with open(caminho, 'w')as _file:
                json.dump(retornoDoZero, _file)
            return retornoDoZero
        
        try:
            with open(caminho, 'r')as _file:
                arquivo: dict = json.load(_file)
        except json.decoder.JSONDecodeError:
            with open(caminho, 'w')as _file:
                json.dump(retornoDoZero, _file)
            return retornoDoZero

        retorno: dict = {key:value for key,value in arquivo.items() if key == self.dateStr}

        if not retorno:
            arquivo[self.dateStr] = {"finan": {}, "siduscon_mg": {}, "siduscon_rj": {}, "siduscon_sp": {}}
            with open(caminho, 'w')as _file:
                json.dump(arquivo, _file)

        return {key:value for key,value in arquivo.items() if key == self.dateStr}

    def _consultarDB(self, caminho: str, modulo:str) -> dict:
        if os.path.exists(caminho):
            with open(caminho, 'r')as _file:
                file: list = json.load(_file)
            try:
                dados_brutos: dict = [x for x in file if x['Mês Base'] == self.dateStr][0]
                mes: str = dados_brutos.pop('Mês Base')
            except IndexError:
                return {self.dateStr : {modulo: {}}}
            return {mes: {modulo: dados_brutos}}
        return {}
    
        
    def _comparar(self, enviados:dict, db:dict, modulo:str) -> dict:
        indices_add:list = []
        lista_add: dict = {modulo: {}}
        
        dicio_verificar: dict = db[self.dateStr][modulo]
        for key,value in dicio_verificar.items():
            if not key in enviados[self.dateStr][modulo]:
                lista_add[modulo][key] = value

        return lista_add
    
    def salvar(self, speak=False) -> bool:
        dados: Dict[str,dict] = {}
        lista_itens: List[dict] = [self.enviar_finan, self.enviar_siduscon_mg, self.enviar_siduscon_rj, self.enviar_siduscon_sp]
        altera = True       
        for item in lista_itens:
            key,value = list(item.keys())[0], list(item.values())[0]
            dados[key] = value
            if value:
                altera = False

        if altera:
            print("sem dados para salvar") if speak else None
            return False

        with open(self.__email_db_caminho, 'r')as _file:
            arquivo:dict = json.load(_file)

        for keys,values in dados.items():
                for key, value in values.items():
                    arquivo[self.dateStr][keys][key] = value


        with open(self.__email_db_caminho, 'w')as _file:
           json.dump(arquivo, _file)
        
        print("dados salvos") if speak else None
        return True
    
    def indices(self):
        return {self.dateStr : {"finan" : list(self.enviar_finan.values())[0], "siduscon_mg" : list(self.enviar_siduscon_mg.values())[0], "siduscon_rj" : list(self.enviar_siduscon_rj.values())[0], "siduscon_sp" : list(self.enviar_siduscon_sp.values())[0]}}


# função auxiliar do 
def _find_element(browser:webdriver.Chrome, parameter, target:str, timeout:int=60, force_error=False):
    for x in range(timeout):
        try:
            element = browser.find_element(parameter, target)
            print(f"found -> {target}")
            return element
        except:
            print(f"not found -> {target}")
            sleep(1)
    if force_error:    
        raise Exception(f"'{target}' not found")
    else:
        return browser.find_element(By.TAG_NAME, 'html')

class SendEmail(CheckIndiceList):
    def __init__(self, date:datetime, db_email:str = "db/db_email.json") -> None:
        super().__init__(date, db_email)

        self.__options = ChromeOptions()
        self.__options.add_argument(f"--user-data-dir=C:\\Users\\{getuser()}\\AppData\\Local\\Google\\Chrome")
        
        self.indices_diponiveis:dict = self.indices()
        
    def criar_mensagem_financeiro(self) -> str:
        indices_finan: Dict[str,float] = self.indices_diponiveis[self.dateStr]['finan']
        
        mensagem_fin:str = ""
        for key,value in indices_finan.items():
            try:
                value = float(value)
                value = round(value, 2)
            except ValueError:
                continue
            if (key == "INCC_ANO_VAR") or (key == "INCC_12_MESES_VAR"):
                continue
            key = key.replace("INCC_MES_VAR", "INCC_VAR")
            mensagem_fin += f"      {key}: {str(value).replace('.', ',')}\n\n"
        
        if mensagem_fin == "":
            return ""
        
        mensagem:str = f"""
Prezados Colaboradores,

Esperamos que este e-mail encontre vocês bem. Como parte do nosso compromisso em mantê-los informados sobre as principais movimentações do mercado financeiro, estamos enviando a atualização mensal dos índices financeiros coletados por nosso robô.

Segue abaixo a lista dos índices financeiros divulgados com a data base '{self.date.strftime('%d/%m/%Y')}':

{mensagem_fin}Este e-mail é gerado automaticamente e enviado apenas para fins informativos. Por favor, não responda a este e-mail, pois não poderemos receber ou responder mensagens enviadas a esta caixa postal.
"""
        return mensagem
    
    def criar_mensagem_setoriais(self) -> str:
        indices_siduscon_mg: Dict[str,float] = self.indices_diponiveis[self.dateStr]["siduscon_mg"]
        indices_siduscon_rj: Dict[str,float] = self.indices_diponiveis[self.dateStr]["siduscon_rj"]
        indices_siduscon_sp: Dict[str,float] = self.indices_diponiveis[self.dateStr]["siduscon_sp"]
        
        
        mensagem_setorial:str = ""
        #MG
        for key,value in indices_siduscon_mg.items():
            try:
                value = float(value)
                value = round(value, 2)
            except ValueError:
                continue
            if (key == "INCC_ANO_VAR") or (key == "INCC_12_MESES_VAR"):
                continue
            key = key.replace("INCC_MES_VAR", "INCC_VAR")
            mensagem_setorial += f"     {key}: {str(value).replace('.', ',')}\n\n"
            
        #RJ
        for key,value in indices_siduscon_rj.items():
            try:
                value = float(value)
                value = round(value, 2)
            except ValueError:
                continue
            if (key == "INCC_ANO_VAR") or (key == "INCC_12_MESES_VAR"):
                continue
            key = key.replace("INCC_MES_VAR", "INCC_VAR")
            mensagem_setorial += f"     {key}: {str(value).replace('.', ',')}\n\n"

        #SP
        for key,value in indices_siduscon_sp.items():
            try:
                value = float(value)
                value = round(value, 2)
            except ValueError:
                continue
            if (key == "INCC_ANO_VAR") or (key == "INCC_12_MESES_VAR"):
                continue
            key = key.replace("INCC_MES_VAR", "INCC_VAR")
            mensagem_setorial += f"     {key}: {str(value).replace('.', ',')}\n\n"
            
        if mensagem_setorial == "":
            return ""
        
        mensagem:str = f"""
Prezados Colaboradores,

Esperamos que este e-mail encontre vocês bem. Como parte do nosso compromisso em mantê-los informados sobre as principais movimentações do mercado financeiro, estamos enviando a atualização mensal dos índices financeiros coletados por nosso robô.

Segue abaixo a lista dos índices setoriais divulgados com a data base '{self.date.strftime('%d/%m/%Y')}':

{mensagem_setorial}Este e-mail é gerado automaticamente e enviado apenas para fins informativos. Por favor, não responda a este e-mail, pois não poderemos receber ou responder mensagens enviadas a esta caixa postal.
"""
        return mensagem

    def iniciar(self, speak=False) -> None:
        msg_fin: str = self.criar_mensagem_financeiro()
        msg_setor: str =self.criar_mensagem_setoriais()
        
        if (msg_fin == "") and (msg_setor == ""):
            print("sem indicies para publicar!") if speak else None
            return
        
        with webdriver.Chrome(options=self.__options)as navegador:
            navegador.get(r"https://www.microsoft.com/pt-pt/microsoft-365/outlook/email-and-calendar-software-microsoft-outlook/")

            #navegador.find_element(By.ID, 'mectrl_headerPicture').click()
            _find_element(navegador, By.ID, 'mectrl_headerPicture').click() #clicar en entrar no email
            
            _find_element(navegador, By.ID, 'i0116').send_keys('rpa@patrimar.com.br') #digitar email
            _find_element(navegador, By.ID, 'i0116').send_keys(Keys.RETURN) # apertar Enter
            
            cont: int = 0
            while _find_element(navegador, By.XPATH, '//*[@id="loginHeader"]/div').text != "Insira a senha": #esperar pela senha
                if cont >= 5*60:
                    raise TimeoutError("não foi possivel fazer login, campo senha não apareceu")
                else:
                    cont += 1
                sleep(1)
                       
            _find_element(navegador, By.ID, 'i0118').send_keys("@utomation#24#") # digita senha
            _find_element(navegador, By.ID, 'i0118').send_keys(Keys.RETURN) # apertar Enter
            
            _find_element(navegador, By.ID, 'idBtn_Back').click() # clica em "não" para continuar conectado
            
            
            
            # Indices Financeiros
            if msg_fin != "":
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/div/div/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div/div/span/button[1]/span/span[1]/span').click() # clica em "Novo Email"
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys("renan.oliveira@patrimar.com.br;") # digita lista de email para enviar
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys(Keys.RETURN) # apertar Enter
                # _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys("mariana.paiva@patrimar.com.br;") # digita lista de email para enviar
                # _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys(Keys.RETURN) # apertar Enter
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[2]/div[2]/div/div/div/input').send_keys("Atualização Mensal dos Índices Financeiros") # digita titulo
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[4]/div/div[1]/div').send_keys(msg_fin) # digita conteudo
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[2]/div[1]/div/span/button[1]', force_error=True).click() # clica em enviar
            
            
            #_find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div[1]/div[2]/div/a/span').click() # clica em "Outlook"
            
            
            # Indices Setoriais
            if msg_setor != "":
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/div/div/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div/div/span/button[1]/span/span[1]/span').click() # clica em "Novo Email"
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys("renan.oliveira@patrimar.com.br;") # digita lista de email para enviar
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys(Keys.RETURN) # apertar Enter
                # _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys("mariana.paiva@patrimar.com.br;") # digita lista de email para enviar
                # _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[1]/div/div[4]/div/div/div[1]').send_keys(Keys.RETURN) # apertar Enter
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[3]/div[2]/div[2]/div/div/div/input').send_keys("Atualização Mensal dos Índices Setoriais") # digita titulo
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[4]/div/div[1]/div').send_keys(msg_setor) # digita conteudo
                _find_element(navegador, By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[3]/div[1]/div/div/div/div[2]/div[1]/div/span/button[1]', force_error=True).click() # clica em enviar
            
            if (msg_fin != "") or (msg_setor != ""):
                self.salvar(speak=True)
            sleep(5)
            

if __name__ == "__main__":
    bot: SendEmail = SendEmail(datetime.now() - relativedelta(months=1))

    #print(f"\n{bot.indices()}")
    #bot.salvar(speak=True)
    print(f"\n{bot.iniciar(speak=True)}")
    #print(f"\n\nSalvar : {email.salvar()}")

    #print(f"\nindices_enviados : {email.indices_enviados}\nindices_encontrados_fin : {email.indices_finan_db}")



    
