# Script para salvar todos os arquivos abertos no VS Code
Write-Host "Preparando para salvar todos os arquivos do projeto..." -ForegroundColor Green

# Tenta salvar todos os arquivos no VS Code
Write-Host "Tentando salvar arquivos no VS Code..." -ForegroundColor Yellow

# Pressione Ctrl+K, S no VS Code para salvar todos os arquivos
Write-Host "Por favor, pressione manualmente" -ForegroundColor Cyan
Write-Host "CTRL+K, S" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "em seu VS Code para salvar todos os arquivos." -ForegroundColor Cyan
Write-Host "Alternativamente, use File > Save All no menu superior." -ForegroundColor Cyan

Write-Host "`nPressione Enter quando tiver concluído o salvamento..." -ForegroundColor Yellow
$null = Read-Host

# Verifica se a pasta frontend-react existe
if (Test-Path -Path "i:\Github\pywallet3\frontend-react") {
    # Tenta reiniciar o servidor de desenvolvimento
    Write-Host "`nReiniciando o servidor de desenvolvimento..." -ForegroundColor Green
    
    # Navega para a pasta e inicia o servidor
    Set-Location -Path "i:\Github\pywallet3\frontend-react"
    npm run dev
}
else {
    Write-Host "A pasta frontend-react não foi encontrada!" -ForegroundColor Red
}

Write-Host "Processo concluído!" -ForegroundColor Green
