@echo off
title Positiva - Enviando codigo para o GitHub...
color 0B
cls
echo.
echo  =============================================
echo     POSITIVA BI - UPLOAD PARA O GITHUB
echo  =============================================
echo.
cd /d "%~dp0"

set GIT="C:\Program Files\Git\cmd\git.exe"

echo [1/4] Configurando Git...
%GIT% config --global user.email "joseroberto@positiva.com"
%GIT% config --global user.name "Positiva BI"

echo [2/4] Inicializando repositorio...
%GIT% init
%GIT% remote remove origin 2>nul
%GIT% remote add origin https://github.com/joseroberto-melo/daniel.git

echo [3/4] Adicionando arquivos...
%GIT% add .
%GIT% commit -m "feat: sistema positiva bi - scrapers, dashboard e github actions"

echo [4/4] Enviando para o GitHub...
%GIT% remote set-url origin https://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@github.com/joseroberto-melo/daniel.git
%GIT% branch -M main
%GIT% push -u origin main

echo.
if %ERRORLEVEL% equ 0 (
    echo  =============================================
    echo   CODIGO ENVIADO PARA O GITHUB COM SUCESSO!
    echo  =============================================
    echo.
    echo  Proximo passo: Configurar os Secrets no GitHub
    echo  (veja as instrucoes no chat)
) else (
    echo  AVISO: Pode ser necessario fazer login no GitHub.
    echo  Tente novamente apos fazer login.
)
echo.
pause
