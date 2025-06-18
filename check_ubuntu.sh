#!/bin/bash
# Script de diagnóstico para verificar a configuração do Ubuntu para PyWallet

echo "===== Diagnóstico de Sistema para PyWallet ====="
echo ""

# Verifica a versão do Ubuntu
echo "1. Verificando versão do Ubuntu:"
if [ -f "/etc/lsb-release" ]; then
    cat /etc/lsb-release
    echo "✓ Ubuntu detectado"
else
    echo "⚠️ Não foi possível detectar o Ubuntu"
fi
echo ""

# Verifica a versão do Python
echo "2. Verificando versão do Python:"
python3 --version
if [ $? -eq 0 ]; then
    PY_VERSION=$(python3 -c 'import sys; print(sys.version_info.major * 100 + sys.version_info.minor)')
    if [ $PY_VERSION -ge 310 ]; then
        echo "✓ Python 3.10+ encontrado"
    else
        echo "⚠️ Versão do Python é inferior a 3.10. Considere atualizar."
    fi
else
    echo "⚠️ Python3 não encontrado. Por favor, instale com 'sudo apt install python3'"
fi
echo ""

# Verifica o Node.js
echo "3. Verificando Node.js:"
if command -v node &> /dev/null; then
    node --version
    echo "✓ Node.js encontrado"
else
    echo "⚠️ Node.js não encontrado. Instale com 'sudo apt install nodejs npm'"
fi
echo ""

# Verifica dependências do sistema necessárias para pacotes Python comuns
echo "4. Verificando dependências do sistema:"
DEPS="build-essential python3-dev libssl-dev libffi-dev"
for pkg in $DEPS; do
    dpkg -s $pkg &> /dev/null
    if [ $? -eq 0 ]; then
        echo "✓ $pkg está instalado"
    else
        echo "⚠️ $pkg não está instalado. Considere instalar com 'sudo apt install $pkg'"
    fi
done
echo ""

# Verifica o Tailscale
echo "5. Verificando Tailscale:"
if command -v tailscale &> /dev/null; then
    tailscale version
    echo "✓ Tailscale encontrado"
    echo "Status do Tailscale:"
    tailscale status
else
    echo "⚠️ Tailscale não encontrado. Instale seguindo as instruções em https://tailscale.com/download/linux"
fi
echo ""

# Verifica se o diretório do PyWallet existe e tem as permissões corretas
echo "6. Verificando permissões do diretório PyWallet:"
if [ -d "$PWD" ]; then
    ls -la $PWD | head -5
    if [ -f "$PWD/run_dev.sh" ]; then
        if [ -x "$PWD/run_dev.sh" ]; then
            echo "✓ run_dev.sh tem permissão de execução"
        else
            echo "⚠️ run_dev.sh não tem permissão de execução. Execute 'chmod +x run_dev.sh'"
        fi
    else
        echo "⚠️ run_dev.sh não encontrado no diretório atual"
    fi
else
    echo "⚠️ Diretório atual não é acessível"
fi
echo ""

# Verifica o serviço systemd
echo "7. Verificando serviços systemd (requer sudo):"
if [ -f "/etc/systemd/system/pywallet.service" ]; then
    echo "✓ pywallet.service encontrado"
    echo "Para verificar o status: sudo systemctl status pywallet.service"
else
    echo "⚠️ pywallet.service não encontrado em /etc/systemd/system/"
fi

if [ -f "/etc/systemd/system/tailscale-funnel.service" ]; then
    echo "✓ tailscale-funnel.service encontrado"
    echo "Para verificar o status: sudo systemctl status tailscale-funnel.service"
else
    echo "⚠️ tailscale-funnel.service não encontrado em /etc/systemd/system/"
fi
echo ""

echo "===== Diagnóstico completo ====="
echo ""
echo "Se tudo estiver marcado com ✓, seu sistema está pronto para executar PyWallet."
echo "Para quaisquer itens marcados com ⚠️, siga as recomendações indicadas."
echo ""
echo "Para iniciar o PyWallet manualmente: ./run_dev.sh"
echo "Para iniciar o serviço systemd: sudo systemctl start pywallet.service"
