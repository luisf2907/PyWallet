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

# Verifica se o Node.js está instalado e se a versão é compatível
if ! command -v node &> /dev/null; then
    echo "AVISO: Node.js não encontrado. Algumas funcionalidades podem não funcionar corretamente."
    echo "Por favor, instale o Node.js v16+ usando o NodeSource:"
    echo "  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -"
    echo "  sudo apt install -y nodejs"
    read -p "Pressione ENTER para continuar mesmo assim ou Ctrl+C para cancelar"
else
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo "AVISO: A versão do Node.js ($NODE_VERSION) é muito antiga para o Vite."
        echo "O Vite requer Node.js v16+ para funcionar corretamente."
        echo "Por favor, atualize o Node.js usando o NodeSource:"
        echo "  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -"
        echo "  sudo apt install -y nodejs"
        read -p "Pressione ENTER para continuar mesmo assim (o frontend pode falhar) ou Ctrl+C para cancelar"
    fi
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

# Iniciar o backend em uma nova aba do terminal
echo "Iniciando o backend..."
SCRIPT_DIR="$(pwd)"

# Determinar qual gerenciador de terminal usar
if command -v gnome-terminal &> /dev/null; then
    # Gnome Terminal (Ubuntu, outros com GNOME)
    gnome-terminal --tab --title="PyWallet Backend" --working-directory="$SCRIPT_DIR" -- bash -c "source venv/bin/activate && python run.py; exec bash"
    
    # Espera o backend subir
    sleep 5
    
    # Iniciar o frontend React em uma nova aba
    echo "Iniciando o frontend React..."
    if command -v npm &> /dev/null; then
        gnome-terminal --tab --title="PyWallet Frontend" --working-directory="$SCRIPT_DIR/frontend-react" -- bash -c "npm run dev; exec bash"
    else
        echo "AVISO: npm não encontrado. O frontend React não será iniciado."
    fi
elif command -v konsole &> /dev/null; then
    # KDE Konsole
    konsole --new-tab -p tabtitle="PyWallet Backend" --workdir="$SCRIPT_DIR" -e bash -c "source venv/bin/activate && python run.py; exec bash" &
    
    # Espera o backend subir
    sleep 5
    
    # Iniciar o frontend React em uma nova aba
    echo "Iniciando o frontend React..."
    if command -v npm &> /dev/null; then
        konsole --new-tab -p tabtitle="PyWallet Frontend" --workdir="$SCRIPT_DIR/frontend-react" -e bash -c "npm run dev; exec bash" &
    else
        echo "AVISO: npm não encontrado. O frontend React não será iniciado."
    fi
elif command -v xterm &> /dev/null; then
    # xterm (fallback genérico)
    xterm -T "PyWallet Backend" -e "cd '$SCRIPT_DIR' && source venv/bin/activate && python run.py; bash" &
    
    # Espera o backend subir
    sleep 5
    
    # Iniciar o frontend React em uma nova aba
    echo "Iniciando o frontend React..."
    if command -v npm &> /dev/null; then
        xterm -T "PyWallet Frontend" -e "cd '$SCRIPT_DIR/frontend-react' && npm run dev; bash" &
    else
        echo "AVISO: npm não encontrado. O frontend React não será iniciado."
    fi
else
    echo "Nenhum terminal compatível encontrado para abrir abas separadas."
    echo "Executando serviços no terminal atual (sem abas separadas)..."
    
    # Fallback para o método original
    python run.py &
    BACKEND_PID=$!
    
    # Espera o backend subir
    sleep 5
    
    # Iniciar o frontend React em background
    cd frontend-react
    if command -v npm &> /dev/null; then
        npm run dev &
        FRONTEND_PID=$!
    else
        echo "AVISO: npm não encontrado. O frontend React não será iniciado."
        FRONTEND_PID=""
    fi
    cd ..
    
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
fi

# Mensagem final informativa
echo ""
echo "Servidores de desenvolvimento iniciados!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Os servidores estão rodando em abas separadas do terminal."
echo "Você pode fechar este terminal se desejar."