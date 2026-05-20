@echo off
title POSITIVA - Atualizando Dados...
color 0A
cls
echo.
echo  =============================================
echo     POSITIVA ADMINISTRADORA - ATUALIZACAO
echo  =============================================
echo.
echo  Este processo ira:
echo    1. Ler todas as planilhas dos SDRs
echo    2. Buscar relatorios de ligacoes (CallBox)
echo    3. Buscar vendas fechadas (Portal Positiva)
echo    4. Salvar tudo no banco de dados
echo.
echo  Iniciando... aguarde (pode levar alguns minutos)
echo.
cd /d "%~dp0"

python main_orchestrator.py

echo.
if %ERRORLEVEL% equ 0 (
    echo  =============================================
    echo   ATUALIZACAO CONCLUIDA COM SUCESSO!
    echo   Abra o painel para ver os dados atualizados.
    echo  =============================================
) else (
    echo  AVISO: Ocorreu algum problema. Veja os erros acima.
)
echo.
pause
