@echo off
title POSITIVA ADMINISTRADORA - Iniciando Painel...
color 0B
cls
echo.
echo  =============================================
echo     POSITIVA ADMINISTRADORA - PAINEL DE BI
echo  =============================================
echo.
echo  Iniciando o sistema, por favor aguarde...
echo.
cd /d "%~dp0"

echo  [1/2] Verificando dependencias...
pip install streamlit plotly pandas openpyxl python-dotenv -q --no-warn-script-location >nul 2>&1

echo  [2/2] Abrindo Painel no navegador...
echo.
echo  ============================================
echo   O PAINEL ABRIRA AUTOMATICAMENTE NO NAVEGADOR
echo   Para fechar, pressione CTRL+C nesta janela
echo  ============================================
echo.
python -m streamlit run dashboard\app.py --browser.gatherUsageStats false

if %ERRORLEVEL% neq 0 (
    echo.
    echo  ERRO: Nao foi possivel iniciar o sistema.
    echo  Verifique se o Python esta instalado corretamente.
    pause
)
