import sys
sys.path.append("Entities")
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import xlwings as xw
from getpass import getuser
from Entities.coleta.IndiceSidusconMG import SetoriaisMG
from Entities.coleta.IndiceSidusconRJ import SetoriaisRJ
from Entities.coleta.IndiceSidusconSP import SetoriaisSP
from Entities.coleta.IndiceSetorial_para_Fin import IndicesFinSetoriais
import compilador_dados_BI
from Entities.dependencies.logs import Logs, traceback

def date_creation(date):
    """
    Cria uma data baseada no mês anterior ou na data fornecida.

    Parameters:
        date (str or None): Uma string representando a data no formato "%d/%m/%Y" ou None para usar o mês anterior.

    Returns:
        datetime: Objeto datetime representando a data resultante.
    """    
    try:
        date_temp = datetime.strptime(date, "%d/%m/%Y")
    except:
        date_temp = datetime.now() - relativedelta(months=1)
    
    return date_temp.replace(day=1).replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)

class PlanilhaIndiceSetorial:
    def __init__(self, date):
        """
        Inicializa a classe PlanilhaIndiceSetorial.

        Parameters:
            date (datetime): Data para a qual os índices serão registrados na planilha.
        """        
        self._date = date

    def _indice_siduscon_mg(self):
        """
        Obtém os índices de SetoriaisMG para a data especificada.

        Returns:
            list: Lista contendo os índices obtidos.
        """        
        with open("db\\db_siduscon_mg.json", 'r')as arqui:
            siduscon_mg = json.load(arqui)

        for indice in siduscon_mg:
            if indice['Mês Base'] == self._date.strftime("%Y-%m-%d"):
                indices = indice
                break

        try:
            siduscon_mg = list(indices.values())
            siduscon_mg.pop(0)
            del indices
        except:
            siduscon_mg = []
            for x in range(19):
                siduscon_mg.append("")
        
        return siduscon_mg
    
    def _indice_siduscon_sp(self):
        """
        Obtém os índices de SetoriaisSP para a data especificada.

        Returns:
            list: Lista contendo os índices obtidos.
        """        
        with open("db\\db_siduscon_sp.json", 'r')as arqui:
            siduscon_sp = json.load(arqui)

        for indice in siduscon_sp:
            if indice['Mês Base'] == self._date.strftime("%Y-%m-%d"):
                indices = indice
                break

        try:
            siduscon_sp = list(indices.values())
            siduscon_sp.pop(0)
            del indices
        except:
            siduscon_sp = []
            for x in range(2):
                siduscon_sp.append("")
        
        return siduscon_sp
    
    def _indice_siduscon_rj(self):
        """
        Obtém os índices de SetoriaisRJ para a data especificada.

        Returns:
            list: Lista contendo os índices obtidos.
        """        
        with open("db\\db_siduscon_rj.json", 'r')as arqui:
            siduscon_rj = json.load(arqui)

        for indice in siduscon_rj:
            if indice['Mês Base'] == self._date.strftime("%Y-%m-%d"):
                indices = indice
                break

        try:
            siduscon_rj = list(indices.values())
            siduscon_rj.pop(0)
            del indices
        except:
            siduscon_rj = []
            for x in range(2):
                siduscon_rj.append("")
        
        return siduscon_rj

    def salvar(self, modelo='planilhas\\modelo_indices.xlsx'):
        """
        Salva os índices na planilha de modelo especificada.

        Parameters:
            modelo (str): Caminho do modelo da planilha.

        Returns:
            None
        """        
        app = xw.App(visible=False)
        with app.books.open(modelo) as wb:
            setoriais = wb.sheets[wb.sheet_names.index('ÍNDICES SETORIAIS')]
            demo = wb.sheets[wb.sheet_names.index('demo')]
            
            ultima_linha = setoriais.range('A65536').end('up').row + 1
            
            for linha_data in setoriais.range(f'A6:A{ultima_linha}'):
                if linha_data.value == self._date:
                    ultima_linha = linha_data.address.split('$')[-1]
            
            demo.range('A1:Y1').copy()
            setoriais.range(f'A{ultima_linha}:Y{ultima_linha}').paste()
            setoriais.range(f'A{ultima_linha}').value = self._date
            setoriais.range(f'B{ultima_linha}:U{ultima_linha}').value = self._indice_siduscon_mg()
            setoriais.range(f'V{ultima_linha}:W{ultima_linha}').value = self._indice_siduscon_sp()
            setoriais.range(f'X{ultima_linha}:Y{ultima_linha}').value = self._indice_siduscon_rj()

            wb.save()

        try:
            app.quit()
        except:
            pass    

if __name__ == "__main__":
    import os
    try:
        date = date_creation(datetime.now())

        
        error_resgat = ""
        # Coleta os índices de SetoriaisMG, SetoriaisRJ, SetoriaisSP, e IndicesFinSetoriais para a data especificada
        try:
            SetoriaisMG(data=date.strftime("%d/%m/%Y"), read_only=False).resultado()
        except Exception as error:
            print(f"{type(error)} - {error}")
            error_resgat = error
            
        try:
            SetoriaisRJ(data=date.strftime("%d/%m/%Y"), read_only=False).resultado()
        except Exception as error:
            print(f"{type(error)} - {error}")
            error_resgat = error

        try:
            SetoriaisSP(data=date.strftime("%d/%m/%Y"), read_only=False).resultado()
        except Exception as error:
            print(f"{type(error)} - {error}")
            error_resgat = error

        try:
            IndicesFinSetoriais(data=date.strftime("%d/%m/%Y"), read_only=False).resultado()
        except Exception as error:
            print(f"{type(error)} - {error}")
            error_resgat = error


        # Compila os índices setoriais e financeiros em arquivos JSON
        compilador_dados_BI.compilador_fabric_setoriais(entrada=["db/db_siduscon_mg.json", "db/db_siduscon_rj.json", "db/db_siduscon_sp.json"], saida=f"C:/Users/{getuser()}/PATRIMAR ENGENHARIA S A/RPA - Documentos/RPA - Dados/Indices/indices.json")
        compilador_dados_BI.compilador_fabric_financeiro(entrada=["db/db_setoriais_fin.json"], saida=f"C:/Users/{getuser()}/PATRIMAR ENGENHARIA S A/RPA - Documentos/RPA - Dados/Indices/indices_financeiros.json")
        
        if error_resgat:
            raise Exception(f"foi executado mas com 1 ou mais errors:\n{type(error_resgat)} -> {error_resgat}")
        
        Logs().register(status='Concluido', description="Automação dos Indices Setorias foi concluida!")
    except Exception as err:
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())