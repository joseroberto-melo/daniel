"""
Scraper CallBox - Positiva Administradora
URL: https://positiva.callbox.com.br/login.php
Extrai relatório de ligações por agente/período.
"""
import pandas as pd
import os
import sys
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from config import Config

OUTPUT_CSV = os.path.join(BASE_DIR, "dados_callbox.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "logs", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_callbox_scraper(data_inicio=None, data_fim=None):
    """
    Acessa o CallBox, seleciona o período e extrai o relatório de ligações.
    Retorna um DataFrame com os dados extraídos.
    """
    if data_inicio is None:
        data_inicio = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
    if data_fim is None:
        data_fim = datetime.now().strftime("%d/%m/%Y")

    print(f"  Período: {data_inicio} a {data_fim}")
    print(f"  URL: {Config.CALLBOX_URL}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ERRO: Playwright não instalado. Execute: pip install playwright && playwright install chromium")
        return pd.DataFrame()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=Config.HEADLESS)
        page = browser.new_context().new_page()

        try:
            # 1. ACESSA A PÁGINA DE LOGIN
            print("  [1/5] Acessando página de login...")
            page.goto(Config.CALLBOX_URL, wait_until="domcontentloaded", timeout=30000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "callbox_01_login.png"))

            # 2. PREENCHE CREDENCIAIS
            print("  [2/5] Preenchendo credenciais...")
            # Tenta seletores comuns de login — ajustar se necessário
            for sel in ["input[name='login']", "input[name='usuario']", "input[name='username']", "input[type='text']:first-of-type"]:
                try:
                    page.fill(sel, Config.CALLBOX_USER, timeout=3000)
                    break
                except:
                    continue

            for sel in ["input[name='senha']", "input[name='password']", "input[type='password']"]:
                try:
                    page.fill(sel, Config.CALLBOX_PASS, timeout=3000)
                    break
                except:
                    continue

            # 3. CLICA EM ENTRAR
            print("  [3/5] Realizando login...")
            for sel in ["button[type='submit']", "input[type='submit']", "button:has-text('Entrar')", "button:has-text('Login')"]:
                try:
                    page.click(sel, timeout=3000)
                    break
                except:
                    continue

            page.wait_for_load_state("networkidle", timeout=20000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "callbox_02_pos_login.png"))
            print("  Login realizado. Verificando acesso...")

            # 4. NAVEGA PARA RELATÓRIOS
            print("  [4/5] Navegando para Relatórios de Callcenter...")
            for text in ["Relatórios", "Relatorios", "Reports"]:
                try:
                    page.click(f"text='{text}'", timeout=5000)
                    page.wait_for_timeout(1000)
                    break
                except:
                    continue

            for text in ["Relatórios de Callcenter", "Callcenter", "Ligações"]:
                try:
                    page.click(f"text='{text}'", timeout=5000)
                    page.wait_for_load_state("networkidle", timeout=10000)
                    break
                except:
                    continue

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "callbox_03_relatorios.png"))

            # 5. SELECIONA PERÍODO E APLICA
            print("  [5/5] Aplicando filtros de data...")
            for sel in ["input[name='data_inicio']", "input[name='dtInicio']", "input[name='data_de']", "#data_inicio"]:
                try:
                    page.fill(sel, data_inicio, timeout=3000)
                    break
                except:
                    continue

            for sel in ["input[name='data_fim']", "input[name='dtFim']", "input[name='data_ate']", "#data_fim"]:
                try:
                    page.fill(sel, data_fim, timeout=3000)
                    break
                except:
                    continue

            for sel in ["button:has-text('Aplicar')", "button:has-text('Filtrar')", "button:has-text('Buscar')", "input[value='Aplicar']"]:
                try:
                    page.click(sel, timeout=3000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    break
                except:
                    continue

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "callbox_04_resultado.png"))

            # 6. EXTRAI TABELA
            print("  Extraindo dados da tabela...")
            html = page.content()
            tables = pd.read_html(html)

            if tables:
                df = tables[0]  # Pega a primeira tabela
                df['data_extracao'] = datetime.now().strftime("%Y-%m-%d")
                df['data_inicio_periodo'] = data_inicio
                df['data_fim_periodo'] = data_fim
                df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
                print(f"  Dados salvos em: {OUTPUT_CSV}")
                browser.close()
                return df
            else:
                print("  AVISO: Nenhuma tabela encontrada na página.")
                browser.close()
                return pd.DataFrame()

        except Exception as e:
            print(f"  ERRO durante scraping do CallBox: {e}")
            try:
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "callbox_ERRO.png"))
                print(f"  Screenshot de erro salva em: {SCREENSHOT_DIR}")
            except:
                pass
            browser.close()
            return pd.DataFrame()

if __name__ == "__main__":
    df = run_callbox_scraper()
    if not df.empty:
        print(df.head())
    else:
        print("Nenhum dado extraído. Verifique os screenshots na pasta logs/screenshots/")
