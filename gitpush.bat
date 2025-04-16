@echo off
git add .
set /p VERSAO=Digite o comentário:
git commit -m "%VERSAO%"
git push origin %1
