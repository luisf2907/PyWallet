@echo off
rem ============================================================
rem PyWallet - Script unificado para executar backend e frontend
rem ============================================================

rem Verificar se o ambiente virtual existe; se não, criá-lo e ativá-lo
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE (
    echo Ambiente virtual nao encontrado. Criando...
    python -m venv venv
    call venv\Scripts\activate.bat
)

rem Instalar as dependências (se ainda não tiverem sido instaladas)
echo Instalando dependencias...
pip install -r requirements.txt

rem Iniciar o projeto: o script run.py ja cuida de configurar a estrutura,
rem iniciar os servidores backend e frontend e abrir o navegador.
echo Iniciando o PyWallet...
python run.py

pause
