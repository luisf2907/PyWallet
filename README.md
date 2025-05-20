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