@echo off
REM Prophit/PyWallet - Ambiente de Desenvolvimento Portátil e Completo

REM Muda para a pasta do script
cd /d %~dp0

echo ===============================
echo  Prophit - Ambiente Dev Completo
echo ===============================

REM Verificar se o ambiente virtual existe; se não, criar e ativar
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE (
    echo Ambiente virtual nao encontrado. Criando...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Instalar dependências do backend
pip install -r requirements.txt

REM Instalar dependências do frontend React
cd frontend-react
if exist node_modules (
    echo Dependencias do React ja instaladas.
) else (
    echo Instalando dependencias do React...
    npm install
)
cd ..

REM Iniciar o backend
start cmd /k "cd /d %~dp0 && python run.py"

REM Espera o backend subir
timeout /t 5

REM Iniciar o frontend React
start cmd /k "cd /d %~dp0frontend-react && npm run dev"

echo.
echo Servidores de desenvolvimento rodando!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
