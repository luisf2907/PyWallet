#!/bin/bash
# Script para instalar todas as dependências necessárias no Ubuntu

# Verifica se está sendo executado como root/sudo
if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root (use sudo)"
  exit 1
fi

echo "===== Instalando dependências para PyWallet no Ubuntu ====="
echo ""

# Atualiza os repositórios
echo "Atualizando repositórios..."
apt update

# Instala Python e ferramentas de desenvolvimento
echo "Instalando Python e ferramentas de desenvolvimento..."
apt install -y python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev

# Verifica a versão do Python
echo "Verificando versão do Python:"
python3 --version

# Instala o Node.js usando NodeSource para versão mais recente
echo "Instalando Node.js v20.x (LTS)..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Verifica as versões
echo "Verificando versões do Node.js e npm:"
node --version
npm --version

# Instala o Tailscale se não estiver instalado
if ! command -v tailscale &> /dev/null; then
    echo "Instalando Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "Tailscale já está instalado."
    tailscale version
fi

# Cria diretórios necessários com permissões apropriadas
mkdir -p /home/prophit/Documents/PyWallet/backend/logs
mkdir -p /home/prophit/Documents/PyWallet/uploads
mkdir -p /home/prophit/Documents/PyWallet/instance

# Configura permissões apropriadas
echo "Configurando permissões..."
chown -R prophit:prophit /home/prophit/Documents/PyWallet
chmod +x /home/prophit/Documents/PyWallet/*.sh

echo ""
echo "===== Instalação completa! ====="
echo "O sistema está pronto para executar PyWallet."
echo ""
echo "Próximos passos:"
echo "1. Execute o script de diagnóstico para verificar a configuração:"
echo "   ./check_ubuntu.sh"
echo ""
echo "2. Inicie o PyWallet:"
echo "   ./run_dev.sh"
echo ""
echo "3. Ou configure e inicie os serviços systemd:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable pywallet.service tailscale-funnel.service"
echo "   sudo systemctl start pywallet.service tailscale-funnel.service"
