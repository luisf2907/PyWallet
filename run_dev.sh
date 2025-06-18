#!/bin/bash
# Prophit/PyWallet - Ambiente de Desenvolvimento Portátil e Completo
# Script tudo-em-um para Linux

# Muda para a pasta do script
cd "$(dirname "$0")"

echo "==============================="
echo " Prophit - Ambiente Dev Completo"
echo "==============================="

# Configura permissões adequadas automaticamente
echo "Configurando permissões..."
chmod +x *.sh 2>/dev/null

# Garante que as pastas necessárias existem
mkdir -p backend/logs
chmod -R 755 backend/logs
mkdir -p uploads
chmod -R 755 uploads
mkdir -p instance
chmod -R 755 instance

# Verificar se o ambiente virtual existe; se não, criar e ativar
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Instalar dependências do backend
echo "Verificando/instalando dependências do backend..."
pip install -r requirements.txt

# Verifica se o Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "AVISO: Node.js não encontrado. Algumas funcionalidades podem não funcionar corretamente."
    echo "Por favor, instale o Node.js usando o gerenciador de pacotes da sua distribuição:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install nodejs npm"
    echo "  Fedora: sudo dnf install nodejs npm"
    echo "  Arch Linux: sudo pacman -S nodejs npm"
    read -p "Pressione ENTER para continuar mesmo assim ou Ctrl+C para cancelar"
fi

# Instalar dependências do frontend React
cd frontend-react
if [ -d "node_modules" ]; then
    echo "Dependências do React já instaladas."
else
    echo "Instalando dependências do React..."
    if command -v npm &> /dev/null; then
        npm install
    else
        echo "AVISO: npm não encontrado. Ignorando instalação de dependências do React."
    fi
fi
cd ..

# Iniciar o backend em background
echo "Iniciando o backend..."
python run.py &
BACKEND_PID=$!

# Espera o backend subir
sleep 5

# Iniciar o frontend React em background
echo "Iniciando o frontend React..."
cd frontend-react
if command -v npm &> /dev/null; then
    npm run dev &
    FRONTEND_PID=$!
else
    echo "AVISO: npm não encontrado. O frontend React não será iniciado."
    FRONTEND_PID=""
fi
cd ..

echo ""
echo "Servidores de desenvolvimento rodando!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços"

# Função para limpar os processos quando o script for encerrado
cleanup() {
    echo "Parando serviços..."
    kill $BACKEND_PID 2>/dev/null
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Configura a função cleanup para ser chamada quando o script receber SIGINT (Ctrl+C)
trap cleanup SIGINT

# Mantém o script rodando
wait
