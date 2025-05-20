# Prophit

## Pré-requisitos
- Python 3.10+
- Node.js (https://nodejs.org/) (para rodar o frontend React)
- (Opcional, mas recomendado) Git

## Instalação e Execução (Windows)

1. **Clone o repositório** (em qualquer pasta):
   ```powershell
   git clone <url-do-repositorio>
   cd pywallet3
   ```

2. **Crie e ative o ambiente virtual Python:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instale as dependências do backend:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Instale o Node.js** (se ainda não tiver):
   - Baixe em https://nodejs.org/ e instale (marque a opção "Add to PATH").
   - Feche e reabra o terminal após instalar.

5. **Instale as dependências do frontend React:**
   ```powershell
   cd frontend-react
   npm install
   cd ..
   ```

6. **Inicie o sistema (backend + frontend):**
   ```powershell
   .\run_dev.bat
   ```
   ou
   ```powershell
   .\run_total.bat
   ```

- O backend estará em http://localhost:5000
- O frontend React estará em http://localhost:3000

## Observações
- Os scripts `.bat` são portáteis e funcionam em qualquer pasta ou unidade.
- Não use caminhos absolutos nos seus scripts personalizados.
- O diretório `uploads/`, `venv/`, `node_modules/` e arquivos temporários estão no `.gitignore` e não são enviados para o repositório.
- Para rodar em outro computador, basta repetir os passos acima.

## Acesso Externo com Tailscale Funnel

Para acessar a aplicação de fora da sua rede local, você pode usar o Tailscale Funnel.

1.  **Instale o Tailscale:** Siga as instruções em [https://tailscale.com/download](https://tailscale.com/download) para o seu sistema operacional.
2.  **Autentique-se:** Faça login no Tailscale na máquina onde o Prophit está rodando.
3.  **Habilite HTTPS (Opcional, mas recomendado):**
    ```bash
    tailscale cert seu-nome-de-maquina.tailnet.ts.net
    ```
    Isso irá provisionar certificados TLS para sua máquina.
4.  **Exponha o serviço desejado (frontend ou backend):**
    *   Para expor o frontend (React em `http://localhost:3000`):
        ```bash
        tailscale funnel 3000
        ```
    *   Para expor o backend (Flask em `http://localhost:5000`):
        ```bash
        tailscale funnel 5000
        ```
    Você também pode especificar um nome de host:
        ```bash

        tailscale serve --https=443 off
        tailscale funnel --set-path / localhost:3000
        ```
    Após isso, deverá abrir o arquivo vite.config.js em ../frontend-react e alterar o alllowedHosts: [lista de URLs] e colocar o URL tailnet da máquina em questão

5.  **Verifique o status:**
    ```bash
    tailscale funnel status
    ```

Com isso, a aplicação estará acessível externamente através do nome DNS fornecido pelo Tailscale.

**Observação sobre MagicDNS e `run.py`:**
O Tailscale utiliza MagicDNS para resolver nomes de máquinas na sua tailnet para IPs internos do Tailscale. Se você deseja que o `run.py` (ou scripts relacionados) utilizem automaticamente o IP do MagicDNS da máquina para o backend, isso exigiria que o script pudesse consultar o MagicDNS ou o IP da interface Tailscale no momento da execução. 

Uma forma de obter o IP do Tailscale da máquina atual via linha de comando (que poderia ser incorporada em scripts) é:
- Linux/macOS: `tailscale ip -4`
- Windows (PowerShell): `(tailscale ip -4)[0]`

No entanto, a integração direta disso no `run.py` para que o frontend React (que roda no navegador do cliente) use esse IP dinamicamente para se conectar ao backend pode ser complexa, pois o frontend precisa saber o endereço do backend no momento da compilação ou via configuração de ambiente. A abordagem mais simples é o frontend continuar apontando para `localhost:5000` e o Tailscale Funnel/proxy reverso cuidar do roteamento externo.
Se o objetivo é que outros dispositivos *dentro da sua tailnet* acessem o backend, eles podem usar `http://<nome-da-maquina-servidora>:5000` diretamente, graças ao MagicDNS, sem precisar do Funnel para isso. O Funnel é para acesso *de fora* da tailnet.