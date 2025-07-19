#!/bin/bash
# Script para verificar a saúde do PyWallet

echo "======================================"
echo " PyWallet - Verificação de Saúde"
echo "======================================"

# Verifica se o backend está rodando
BACKEND_PID=$(pgrep -f "python.*app.py")
if [ -n "$BACKEND_PID" ]; then
    echo "✅ Backend rodando (PID: $BACKEND_PID)"
    
    # Verifica uso de CPU e memória do processo
    CPU_MEM=$(ps -p $BACKEND_PID -o pid,pcpu,pmem,etime --no-headers)
    echo "📊 Uso de recursos: $CPU_MEM"
    
    # Verifica número de threads
    THREADS=$(ps -p $BACKEND_PID -o nlwp --no-headers)
    echo "🧵 Threads ativas: $THREADS"
    
    # Verifica portas abertas
    PORTS=$(netstat -tlnp 2>/dev/null | grep $BACKEND_PID | awk '{print $4}' | cut -d: -f2)
    echo "🌐 Portas abertas: $PORTS"
    
else
    echo "❌ Backend NÃO está rodando!"
fi

echo ""

# Verifica logs recentes
echo "📋 Logs recentes (últimas 10 linhas):"
echo "--------------------------------------"
if [ -f "backend/logs/terminal_log.txt" ]; then
    tail -10 backend/logs/terminal_log.txt
else
    echo "Arquivo de log não encontrado"
fi

echo ""

# Verifica se há erros no log
echo "🚨 Verificando erros recentes:"
echo "-------------------------------"
if [ -f "backend/logs/terminal_log.txt" ]; then
    ERROR_COUNT=$(grep -i -E "(error|exception|traceback|failed)" backend/logs/terminal_log.txt | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "⚠️  Encontrados $ERROR_COUNT erros no log"
        echo "Últimos erros:"
        grep -i -E "(error|exception|traceback|failed)" backend/logs/terminal_log.txt | tail -5
    else
        echo "✅ Nenhum erro encontrado nos logs"
    fi
else
    echo "Arquivo de log não encontrado"
fi

echo ""

# Verifica uso geral do sistema
echo "💻 Recursos do sistema:"
echo "-----------------------"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
echo "RAM: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100}')"
echo "Disco: $(df -h . | tail -1 | awk '{print $5}')"

echo ""

# Verifica conectividade com yfinance
echo "🌍 Testando conectividade com APIs:"
echo "------------------------------------"
python3 -c "
import yfinance as yf
import requests
try:
    # Testa yfinance
    data = yf.Ticker('AAPL').history(period='1d')
    if not data.empty:
        print('✅ yfinance: OK')
    else:
        print('⚠️  yfinance: Sem dados')
except Exception as e:
    print(f'❌ yfinance: ERRO - {str(e)[:50]}...')

try:
    # Testa conexão básica
    response = requests.get('https://httpbin.org/status/200', timeout=5)
    if response.status_code == 200:
        print('✅ Internet: OK')
    else:
        print('⚠️  Internet: Problema')
except Exception as e:
    print(f'❌ Internet: ERRO - {str(e)[:50]}...')
" 2>/dev/null

echo ""
echo "======================================"
echo " Verificação concluída"
echo "======================================"
