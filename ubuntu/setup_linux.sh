#!/bin/bash
# Script para configurar permissões corretas em um ambiente Linux

# Muda para a pasta do script
cd "$(dirname "$0")"

echo "Configurando permissões para ambiente Linux..."

# Torna scripts shell executáveis
chmod +x *.sh 2>/dev/null
echo "  ✓ Scripts shell configurados como executáveis"

# Garante que a pasta de logs existe e tem permissões corretas
mkdir -p backend/logs
chmod -R 755 backend/logs
echo "  ✓ Pasta de logs configurada"

# Garante que a pasta de uploads existe e tem permissões corretas
mkdir -p uploads
chmod -R 755 uploads
echo "  ✓ Pasta de uploads configurada"

# Garante que a pasta instance existe
mkdir -p instance
chmod -R 755 instance
echo "  ✓ Pasta instance configurada"

echo "Configuração de permissões concluída com sucesso!"
echo "Você pode agora executar o aplicativo com ./run_dev.sh"
