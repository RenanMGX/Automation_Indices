import os
from datetime import datetime
from shutil import copy2
from getpass import getuser
from Entities.dependencies.logs import Logs, traceback


def backup(caminho_destino="\\\\server008\\G\\ARQ_PATRIMAR\\WORK\\DB-Indices-RPA\\"):
    """
    Realiza o backup dos arquivos de um diretório para outro.

    O diretório de origem é obtido pelo caminho atual (os.getcwd()) acrescido de '\\db\\'.
    O diretório de destino é definido como '\\\\server008\\G\\ARQ_PATRIMAR\\WORK\\DB-Indices-RPA\\'.
    Para cada arquivo no diretório de origem, uma cópia é feita para o diretório de destino.

    Returns:
        None
    """    
    caminho_origem = f'{os.getcwd()}\\db\\'
    for arquivo in os.listdir(caminho_origem):
        copy2(caminho_origem + arquivo, caminho_destino)
        


def registro(status, *, descri=""):
    """
    Registra o status de uma operação em um arquivo CSV de registro.

    Parameters:
        status (int): O status da operação (0 para concluído, 1 para erro).
        descri (str): Uma descrição opcional do erro.

    Returns:
        None
    """    
    date = datetime.now()
    date = date.strftime('%d/%m/%Y')

    # Mapeamento dos índices de status
    # 0 = Concluido , 1 = Error
    index = ['Concluido!', 'Error!']

    arquivo = 'registro_backup.csv'

    # Criação do arquivo de registro se não existir
    if not os.path.exists(arquivo):
        with open(arquivo, 'a') as arqui:
            arqui.write("data;status;descriçao\n")

    with open(arquivo, 'a') as arqui:
        arqui.write(f"{date};{index[status]};{descri}\n")

if __name__ == "__main__":
    try:
        # Tenta realizar o backup e registra como concluído em caso de sucesso
        backup()
        registro(0, descri="Backup para WORK")
        backup(f"C:\\Users\\{getuser()}\\PATRIMAR ENGENHARIA S A\\RPA - Documentos\\RPA - Dados\\Indices\\json\\backup indices")
        registro(0, descri="Backup para Sharepoint")
    
        Logs().register(status='Concluido', description="Automação do BackUP dos indices foi Finalizado!")
    except Exception as err:
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
