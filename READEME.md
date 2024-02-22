# Descrição do Programa de Automação Financeira

## Resumo

Este programa faz parte de um sistema de automação financeira projetado para gerenciar, verificar e atualizar índices financeiros e setoriais relacionados ao mercado imobiliário. Utiliza diversas bibliotecas Python para manipulação de dados, interações web, e operações de arquivo, visando automatizar tarefas repetitivas e melhorar a eficiência de processos financeiros.

## Módulos e Arquivos

O sistema é composto por vários módulos Python, cada um responsável por uma tarefa específica dentro do processo de automação. O arquivo `automation_fin.py` atua como o ponto de entrada do programa, coordenando as operações entre os diferentes componentes. Outros arquivos, como `backup_db_indices.py`, `compilador_dados_BI.py`, `enviar_email.py`, entre outros, fornecem funcionalidades adicionais, incluindo backup de dados, compilação de informações para Business Intelligence (BI), envio de e-mails, e atualização de índices financeiros e setoriais.

## Funcionalidades Principais

- **Inicialização e Configuração**: O programa inicia configurando o ambiente, incluindo a adição de diretórios necessários ao path do sistema e a importação de módulos relevantes.
- **Gestão de Índices Financeiros**: Centraliza a gestão de diversos índices financeiros, como CDI, IPCA, IGPM, entre outros. Inclui verificação de índices do mês, comparação de índices pendentes com disponíveis, e atualização de registros em um arquivo Excel.
- **Automação Web**: Utiliza bots para interagir com sites e plataformas online, automatizando a coleta de dados financeiros e a execução de tarefas relacionadas à verificação e atualização de índices.
- **Backup e Segurança**: Implementa rotinas de backup para garantir a segurança dos dados processados e compilados pelo sistema.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal do sistema.
- **Pandas**: Biblioteca para manipulação e análise de dados.
- **Selenium**: Ferramenta para automação de navegadores web.
- **Excel**: Utilizado para armazenar e gerenciar dados financeiros em formato tabular.

## Como Usar

1. **Configuração Inicial**: Configure o ambiente Python e instale as dependências necessárias.
2. **Execução**: Inicie o programa através do arquivo `automation_fin.py`, certificando-se de que todas as credenciais e configurações específicas estão corretas.
3. **Monitoramento e Manutenção**: Acompanhe a execução do programa e realize manutenções periódicas para garantir a atualização contínua dos índices e o correto funcionamento da automação.
