#!/bin/bash

# Script de instalação manual para PyWallet no Fedora
# Útil quando a instalação automática falha

echo "======================================================="
echo "  Instalação Manual do PyWallet para Fedora Linux      "
echo "======================================================="
echo ""

# Instalar dependências do sistema sem assumir acesso root
echo "Instalando dependências do sistema..."
echo "Por favor, digite sua senha quando solicitado:"
sudo dnf install -y python3 python3-pip python3-devel gcc \
    sqlite-devel libffi-devel openssl-devel

# Atualizar pip no ambiente do usuário
echo "Atualizando pip..."
pip3 install --user --upgrade pip setuptools wheel

# Cria diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p instance
mkdir -p uploads
mkdir -p templates

echo "Instalando dependências Python essenciais primeiro..."
pip3 install --user numpy==1.24.4
pip3 install --user pandas==2.0.3
pip3 install --user Werkzeug==2.2.3

echo "Instalando Flask e dependências relacionadas..."
pip3 install --user flask==2.2.5
pip3 install --user flask-cors==3.0.10
pip3 install --user flask-sqlalchemy==3.0.5

echo "Instalando yfinance..."
pip3 install --user yfinance==0.2.36

echo "Instalando demais dependências..."
pip3 install --user -r requirements.txt

echo ""
echo "======================================================="
echo "Instalação manual concluída!"
echo ""
echo "Para iniciar o PyWallet:"
echo "  python3 run.py"
echo ""
echo "O aplicativo estará disponível em:"
echo "  http://localhost:8000"
echo ""
echo "Se encontrar erros, tente:"
echo "  1. Verificar se há mensagens de erro específicas"
echo "  2. Instalar manualmente componentes faltantes:"
echo "     pip3 install --user [nome-do-componente]"
echo "======================================================="