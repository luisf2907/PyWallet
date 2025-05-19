# Prophit React Frontend

Este é o frontend React do Prophit (antigo PyWallet).

## Pré-requisitos
- Node.js (https://nodejs.org/) instalado no sistema (disponível em qualquer pasta)

## Instalação

No diretório `frontend-react`:
```powershell
npm install
```

## Desenvolvimento

```powershell
npm run dev
```

## Build

```powershell
npm run build
```

## Observações de Portabilidade
- O frontend pode ser rodado em qualquer pasta ou unidade.
- Os scripts do projeto principal já usam caminhos relativos.
- O diretório `node_modules/` está no `.gitignore` e não é enviado para o repositório.

## Integração com Backend
O backend deve estar rodando em http://localhost:5000 (ou ajuste o proxy em `vite.config.js` se necessário).
