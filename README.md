# PyWallet - Sistema de Análise de Investimentos

PyWallet é uma aplicação web para análise e acompanhamento de investimentos em ações brasileiras e americanas.

## Características

- Dashboard com visão geral do portfólio
- Acompanhamento da performance individual de ativos
- Gráfico de evolução do portfólio ao longo do tempo
- Gráfico de distribuição de ativos 
- Registro e acompanhamento de proventos (dividendos)
- Suporte para ações da B3 e das bolsas americanas
- Cache inteligente para reduzir dependência do Yahoo Finance

## Requisitos

- Python 3.8+
- Navegador web moderno
- Conexão com internet (para atualização de preços e dividendos)

## Instalação no Fedora Linux

Para instalar o PyWallet em um servidor Fedora Linux, siga os passos abaixo:

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/pywallet3.git
   cd pywallet3
   ```

2. Torne o script de instalação executável:
   ```bash
   chmod +x install_fedora.sh
   ```

3. Execute o script de instalação como root:
   ```bash
   sudo ./install_fedora.sh
   ```

Este script irá:
- Instalar todas as dependências necessárias
- Configurar um usuário dedicado para o serviço (pywallet)
- Instalar o PyWallet em `/opt/pywallet`
- Configurar o serviço systemd para inicialização automática
- Configurar o Nginx como proxy reverso

## Uso em modo servidor

Após a instalação, o PyWallet estará rodando como serviço e pode ser acessado em:
```
http://seu-ip-servidor
```

### Gerenciamento do serviço

Para gerenciar o serviço PyWallet:
```bash
# Iniciar o serviço
sudo systemctl start pywallet

# Parar o serviço 
sudo systemctl stop pywallet

# Verificar status
sudo systemctl status pywallet

# Visualizar logs
sudo journalctl -u pywallet
```

### Usuário padrão

Um usuário padrão é criado durante a instalação:
- Email: root@example.com
- Senha: password123

Recomenda-se trocar a senha após o primeiro login.

## Configuração para ambiente de produção

Para aumentar a segurança em ambiente de produção, configure a variável de ambiente:
```bash
export PYWALLET_PRODUCTION=true
```

Você também pode definir uma chave secreta personalizada:
```bash
export PYWALLET_SECRET_KEY='sua_chave_secreta_aqui'
```

Adicione estas linhas ao arquivo `/etc/environment` para torná-las permanentes.

## Solução de problemas

### Problemas de permissão
Se encontrar problemas de permissão, verifique se as permissões estão corretas:
```bash
sudo chown -R pywallet:pywallet /opt/pywallet
sudo chmod -R 755 /opt/pywallet
```

### Rate Limiting do Yahoo Finance
O sistema possui um mecanismo inteligente de cache e pausas quando o Yahoo Finance limita requisições. Se os preços não estão atualizando, é normal - a aplicação usará os últimos valores armazenados no cache.

## Licença

Este software é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.