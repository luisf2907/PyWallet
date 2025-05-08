@echo off
git add .
set /p VERSAO=Digite o comentario:
git commit -m "%VERSAO%"
git push origin %1
