#!/bin/bash
# Script para atualizar o Node.js para uma versão compatível com o Vite

# Verifica se está sendo executado como root/sudo
if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root (use sudo)"
  exit 1
fi

echo "===== Atualizando Node.js para versão 20.x LTS ====="
echo ""

# Remove versões antigas do Node.js se existirem
echo "Removendo versões antigas do Node.js (se existirem)..."
apt remove -y nodejs nodejs-legacy npm 2>/dev/null
apt autoremove -y 2>/dev/null

# Instala o curl se não estiver instalado
if ! command -v curl &> /dev/null; then
    echo "Instalando curl..."
    apt update
    apt install -y curl
fi

# Adiciona o repositório NodeSource para Node.js 20.x
echo "Adicionando repositório NodeSource..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

# Instala o Node.js da fonte NodeSource
echo "Instalando Node.js 20.x..."
apt install -y nodejs

# Verifica a instalação
echo ""
echo "Verificando a instalação:"
node --version
npm --version

echo ""
echo "===== Node.js atualizado com sucesso! ====="
echo "Agora você pode executar o PyWallet com ./run_dev.sh"
