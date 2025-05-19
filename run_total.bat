@echo off
rem ============================================================
rem Prophit - Script unificado para executar backend e frontend
rem ============================================================

rem Muda para a pasta do script
cd /d %~dp0

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

rem Iniciar o projeto: o script run.py cuida de tudo
python run.py

pause
