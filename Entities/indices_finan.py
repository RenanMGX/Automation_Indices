from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

from coleta.IndiceIPCA import IPCA, IPCA_1
from coleta.IndiceJuros import Juros_0_5, Juros_0_8, Juros_1
from coleta.IndiceINCC import INCC
from coleta.IndiceCDI import CDI
from coleta.poupas import Poupas12, Poupas15, Poupas28
from coleta.IndeceIGPM import IGPM, IGPM_0_50, IGPM_1

import pandas as pd


class FinanceiroImobme():
    def __init__(self, date):
        """
        Inicializa a classe FinanceiroImobme.

        Parameters:
            date (datetime): A data para a qual os índices financeiros serão calculados.
        """        
        try:
            
            self.date = datetime.strftime(date, "%d/%m/%Y")
        except TypeError:
            data_temp = datetime.strptime(date, "%d/%m/%Y")
            data_temp = data_temp.replace(day=1)
            self.date = data_temp.strftime("%d/%m/%Y")
        
        print(self.date)
        self.__dados = {'data' : self.date, 'indices':{}, 'errors' : {}}
    
    def montar_dados(self, read_only=True):
        """
        Coleta dados de vários índices financeiros para uma data específica.

        Parameters:
            read_only (bool): Se True, os índices são apenas lidos e não recalculados.

        Returns:
            dict: Dicionário contendo os índices financeiros e possíveis erros.
        """        
        #0,8% a.m.
        try:
            indice = Juros_0_8(self.date, read_only)
            self.__dados['indices'][r'0,8% a.m.'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors'][r'0,8% a.m.'] = str(error)

        #0,5% a.m.
        try:
            indice = Juros_0_5(self.date, read_only)
            self.__dados['indices'][r'0,5% a.m.'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors'][r'0,5% a.m.'] = str(error)

        #JUROS 1%
        try:
            indice = Juros_1(self.date, read_only)
            self.__dados['indices'][r'JUROS 1%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors'][r'JUROS 1%'] = str(error)

        #JUROS 0,5%
        try:
            indice = Juros_0_5(self.date, read_only)
            self.__dados['indices'][r'JUROS 0,5%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors'][r'JUROS 0,5%'] = str(error)

        #INCC
        try:
            indice = INCC(self.date, read_only)
            self.__dados['indices']['INCC'] = indice.resultado()['INCC']
        except Exception as error:
            self.__dados['errors']['INCC'] = str(error)
        
        #CDI
        try:
            indice = CDI(self.date, read_only)
            self.__dados['indices']['CDI'] = indice.resultado()['CDI']
        except Exception as error:
            self.__dados['errors']['CDI'] = str(error)

        #CDI 3% a.a.
        try:
            indice = CDI(self.date, read_only)
            self.__dados['indices'][r'CDI 3% a.a.'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors'][r'CDI 3% a.a.'] = str(error)

        #IPCA
        try:
            indice = IPCA(self.date, read_only)
            self.__dados['indices']['IPCA'] = indice.resultado()['IPCA Mês']
        except Exception as error:
            self.__dados['errors']['IPCA'] = str(error)

        #IPCA 12a.a.
        try:
            indice = IPCA(self.date, read_only)
            self.__dados['indices']['IPCA 12a.a.'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors']['IPCA 12a.a.'] = str(error)
            
        #IPCA 1%
        try:
            indice = IPCA_1(self.date, read_only)
            self.__dados['indices']['IPCA 1%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors']['IPCA 1%'] = str(error)
        
        #POUPA 12
        try:
            indice = Poupas12(self.date, read_only)
            self.__dados['indices']['POUPA 12'] = indice.resultado()['Acumulado']
        except Exception as error:
            self.__dados['errors']['POUPA 12'] = str(error)
        
        #POUPA 15
        try:
            indice = Poupas15(self.date, read_only)
            self.__dados['indices']['POUPA 15'] = indice.resultado()['Acumulado']
        except Exception as error:
            self.__dados['errors']['POUPA 15'] = str(error)
        
        #POUPA 28
        try:
            indice = Poupas28(self.date, read_only)
            self.__dados['indices']['POUPA 28'] = indice.resultado()['Acumulado']
        except Exception as error:
            self.__dados['errors']['POUPA 28'] = str(error)
        
        #IGPM
        try:
            indice = IGPM(self.date, read_only)
            self.__dados['indices']['IGPM'] = indice.resultado()['Valor']
        except Exception as error:
            self.__dados['errors']['IGPM'] = str(error)

        #IGPM 0,5%
        try:
            indice = IGPM_0_50(self.date, read_only)
            self.__dados['indices']['IGPM 0,5%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors']['IGPM 0,5%'] = str(error)

        #IGPM 1%
        try:
            indice = IGPM_1(self.date, read_only)
            self.__dados['indices']['IGPM 1%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            self.__dados['errors']['IGPM 1%'] = str(error)


        if self.__dados['errors'] == {}:
            del self.__dados['errors']
        if self.__dados['indices'] == {}:
            del self.__dados['indices']
        return self.__dados

    @staticmethod
    def indices_antecipados(temp_date, read_only=True):
           
        data_temp = datetime.strptime(temp_date, "%d/%m/%Y")
        data_temp = data_temp.replace(day=1)
        new_date = data_temp.strftime("%d/%m/%Y")
        
        dados = {'data' : new_date, 'indices':{}, 'errors' : {}}   
        #0,8% a.m.
        try:
            indice = Juros_0_8(new_date, read_only)
            dados['indices'][r'0,8% a.m.'] = indice.resultado()['Fator Composto']
        except Exception as error:
            dados['errors'][r'0,8% a.m.'] = str(error)

        #0,5% a.m.
        try:
            indice = Juros_0_5(new_date, read_only)
            dados['indices'][r'0,5% a.m.'] = indice.resultado()['Fator Composto']
        except Exception as error:
            dados['errors'][r'0,5% a.m.'] = str(error)

        #JUROS 1%
        try:
            indice = Juros_1(new_date, read_only)
            dados['indices'][r'JUROS 1%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            dados['errors'][r'JUROS 1%'] = str(error)

        #JUROS 0,5%
        try:
            indice = Juros_0_5(new_date, read_only)
            dados['indices'][r'JUROS 0,5%'] = indice.resultado()['Fator Composto']
        except Exception as error:
            dados['errors'][r'JUROS 0,5%'] = str(error)



        if dados['errors'] == {}:
            del dados['errors']
        if dados['indices'] == {}:
            del dados['indices']
        return dados

    

if __name__ == "__main__":
    data = datetime.strptime("14/03/2024", '%d/%m/%Y')
    indice = FinanceiroImobme("01/03/2024").montar_dados()
    print(indice)

    # data = (datetime.now() - relativedelta(months=1)).strftime('%d/%m/%Y')
    # #data = f"1/01/2024"
    # #data = (datetime.now() - relativedelta(months=1)).strftime("%d/%m/%Y")

    # # Instancia um objeto da classe FinanceiroImobme
    # indice = FinanceiroImobme(data)

    # # Coleta e imprime os dados financeiros para a data especificada
    # dados = indice.montar_dados(read_only=True)
            
    # df = pd.DataFrame(dados).replace(float("nan"), None)
    # #df.to_excel(f"{data.replace('/', '-')}.xlsx")
    # print(df)
    # #print(dados)

    #import pdb; pdb.set_trace()
