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

# Instalar dependências
echo "Instalando dependências..."
dnf update -y
dnf install -y python3 python3-pip python3-devel gcc sqlite-devel nginx

# Criar diretório de instalação
mkdir -p $INSTALL_DIR
echo "Diretório de instalação criado: $INSTALL_DIR"

# Copiar arquivos para o diretório de instalação
echo "Copiando arquivos..."
cp -R . $INSTALL_DIR/

# Instalar dependências Python
echo "Instalando dependências Python..."
pip3 install -r $INSTALL_DIR/requirements.txt
pip3 install -r $INSTALL_DIR/backend/requirements.txt

# Definir permissões
echo "Configurando permissões..."
chown -R pywallet:pywallet $INSTALL_DIR
chmod -R 755 $INSTALL_DIR

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