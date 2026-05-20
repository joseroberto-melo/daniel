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
%GIT% config --global user.email "jose0604roberto@gmail.com"
%GIT% config --global user.name "Positiva BI"
%GIT% config --global credential.helper manager

echo [2/4] Inicializando repositorio...
%GIT% init
%GIT% remote remove origin 2>nul
%GIT% remote add origin https://github.com/joseroberto-melo/daniel.git

echo [3/4] Adicionando arquivos...
%GIT% add .
%GIT% commit -m "feat: sistema positiva bi - scrapers, dashboard e github actions" 2>nul || %GIT% commit -m "update: atualizacao do sistema"

echo [4/4] Enviando para o GitHub...
%GIT% branch -M main
%GIT% push -u origin main

echo.
if %ERRORLEVEL% equ 0 (
    echo  =============================================
    echo   CODIGO ENVIADO PARA O GITHUB COM SUCESSO!
    echo  =============================================
) else (
    echo  AVISO: Erro no envio. Tente novamente.
)
echo.
pause
