#!/bin/bash

# Script de instalação do PyWallet para Fedora
# Execute este script como root (sudo)

if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root (sudo)."
  exit 1
fi

echo "======================================================="
echo "      Instalação do PyWallet para Fedora Linux         "
echo "======================================================="
echo ""

# Diretório de instalação
INSTALL_DIR="/opt/pywallet"
echo "Diretório de instalação: $INSTALL_DIR"

# Criar usuário dedicado para o serviço
if ! id -u pywallet &>/dev/null; then
    useradd -r -s /bin/false pywallet
    echo "Usuário pywallet criado"
else
    echo "Usuário pywallet já existe"
fi

# Instalar dependências do sistema
echo "Instalando dependências do sistema..."
dnf update -y
dnf install -y python3 python3-pip python3-devel gcc gcc-c++ make \
    sqlite-devel nginx python3-wheel python3-setuptools \
    dos2unix libffi-devel openssl-devel

# Atualizar pip para a versão mais recente
echo "Atualizando pip..."
pip3 install --upgrade pip setuptools wheel

# Criar diretório de instalação
mkdir -p $INSTALL_DIR
echo "Diretório de instalação criado: $INSTALL_DIR"

# Copiar arquivos para o diretório de instalação
echo "Copiando arquivos..."
cp -R . $INSTALL_DIR/

# Corrigir terminadores de linha (CRLF para LF)
echo "Corrigindo terminadores de linha..."
dos2unix $INSTALL_DIR/*.sh
dos2unix $INSTALL_DIR/pywallet.service

# Instalar dependências Python em etapas separadas
echo "Instalando dependências Python essenciais primeiro..."
pip3 install numpy==1.24.4 pandas==2.0.3 Werkzeug==2.2.3

echo "Instalando dependências Python restantes..."
pip3 install -r $INSTALL_DIR/requirements.txt
pip3 install yfinance==0.2.36

echo "Instalando dependências específicas do backend..."
pip3 install flask==2.2.5 flask-cors==3.0.10 flask-sqlalchemy==3.0.5

# Definir permissões
echo "Configurando permissões..."
chown -R pywallet:pywallet $INSTALL_DIR
chmod -R 755 $INSTALL_DIR

# Criar os diretórios necessários
mkdir -p $INSTALL_DIR/instance
mkdir -p $INSTALL_DIR/uploads
mkdir -p $INSTALL_DIR/templates
chown -R pywallet:pywallet $INSTALL_DIR/instance $INSTALL_DIR/uploads $INSTALL_DIR/templates
chmod -R 755 $INSTALL_DIR/instance $INSTALL_DIR/uploads $INSTALL_DIR/templates

# Configurar o serviço systemd
echo "Configurando serviço systemd..."
cp $INSTALL_DIR/pywallet.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pywallet.service

# Configurar Nginx como proxy reverso
echo "Configurando Nginx..."
cat > /etc/nginx/conf.d/pywallet.conf << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Permitir que o Nginx se conecte à rede
if command -v setsebool &> /dev/null; then
    setsebool -P httpd_can_network_connect 1
fi

# Reiniciar Nginx e iniciar o serviço
echo "Iniciando serviços..."
systemctl restart nginx
systemctl start pywallet

echo ""
echo "======================================================="
echo "Instalação concluída!"
echo ""
echo "PyWallet está instalado e configurado como serviço."
echo "Você pode acessar através do navegador: http://seu-ip-servidor"
echo ""
echo "Para gerenciar o serviço:"
echo "  - Iniciar:   systemctl start pywallet"
echo "  - Parar:     systemctl stop pywallet"
echo "  - Reiniciar: systemctl restart pywallet"
echo "  - Status:    systemctl status pywallet"
echo ""
echo "Para visualizar os logs:"
echo "  journalctl -u pywallet"
echo "======================================================="