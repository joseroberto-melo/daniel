"""
Scraper Portal Positiva - Análise de Vendas
URL: https://portal.positiva.com.br/vendas-analise
Extrai resumo de vendas por vendedor, equipe e plataforma.
"""
import pandas as pd
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from config import Config

OUTPUT_CSV = os.path.join(BASE_DIR, "dados_portal_vendas.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "logs", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_portal_scraper():
    """
    Acessa o Portal Positiva e extrai os dados de análise de vendas.
    Retorna DataFrame com: Vendedor, Contratos, Vidas, Prêmio.
    """
    print(f"  URL: {Config.PORTAL_URL}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ERRO: Playwright não instalado.")
        return pd.DataFrame()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=Config.HEADLESS)
        page = browser.new_context().new_page()

        try:
            # 1. ACESSA O PORTAL
            print("  [1/4] Acessando Portal Positiva...")
            page.goto(Config.PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "portal_01_inicio.png"))

            # 2. VERIFICA SE JÁ ESTÁ LOGADO OU PRECISA DE LOGIN
            current_url = page.url
            print(f"  URL atual: {current_url}")

            if "login" in current_url.lower() or "entrar" in current_url.lower():
                print("  [2/4] Página de login detectada. Preenchendo credenciais...")
                for sel in ["input[type='email']", "input[name='email']", "input[name='usuario']"]:
                    try:
                        page.fill(sel, Config.PORTAL_USER, timeout=3000)
                        break
                    except:
                        continue

                for sel in ["input[type='password']", "input[name='senha']", "input[name='password']"]:
                    try:
                        page.fill(sel, Config.PORTAL_PASS, timeout=3000)
                        break
                    except:
                        continue

                # Portal usa botão com texto "Acessar"
                for sel in [
                    "button:has-text('Acessar')",
                    "button[type='submit']",
                    "text='Acessar'",
                    "input[type='submit']"
                ]:
                    try:
                        page.click(sel, timeout=5000)
                        print(f"  Clicou em: {sel}")
                        break
                    except:
                        continue

                page.wait_for_load_state("networkidle", timeout=20000)
            else:
                print("  [2/4] Portal acessado diretamente (sem redirecionamento de login).")

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "portal_02_dashboard.png"))

            # 3. NAVEGA PARA A PÁGINA DE ANÁLISE DE VENDAS
            print("  [3/4] Navegando para Análise de Vendas...")
            page.goto("https://portal.positiva.com.br/vendas-analise",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(8000)  # Aguarda JS + API carregar os dados
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "portal_03_analise.png"))

            # 4. EXTRAI KPIs DOS CARDS DA PÁGINA INICIAL (Início)
            print("  [4/4] Extraindo dados de vendas...")

            # Extrai valores via JavaScript da página renderizada
            dados = page.evaluate("""() => {
                const result = {};
                // Tenta extrair texto de todos os elementos com números
                const allText = document.body.innerText;
                result.page_text = allText.substring(0, 5000);
                
                // Tenta capturar especificamente linhas de tabela
                const rows = [];
                document.querySelectorAll('tr').forEach(tr => {
                    const cells = Array.from(tr.querySelectorAll('td, th')).map(c => c.innerText.trim());
                    if (cells.length > 0) rows.push(cells.join(' | '));
                });
                result.table_rows = rows;
                return result;
            }""")

            rows = dados.get('table_rows', [])
            page_text = dados.get('page_text', '')

            if rows:
                # Salva linhas de tabela como CSV
                import io
                lines = [r for r in rows if r.strip() and r != ' | ']
                df_text = pd.DataFrame({'linha': lines})
                df_text['data_extracao'] = datetime.now().strftime("%Y-%m-%d")
                df_text.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
                print(f"  {len(lines)} linhas de dados extraídas.")
                browser.close()
                return df_text

            elif page_text:
                # Salva o texto bruto da página para análise
                text_path = OUTPUT_CSV.replace('.csv', '_raw.txt')
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(page_text)
                print(f"  Texto da página salvo em: {text_path}")
                df_raw = pd.DataFrame({'conteudo': [page_text]})
                browser.close()
                return df_raw
            else:
                print("  AVISO: Nenhum dado extraído.")
                browser.close()
                return pd.DataFrame()

        except Exception as e:
            print(f"  ERRO no Portal Positiva: {e}")
            try:
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "portal_ERRO.png"))
                print(f"  Screenshot salva em: {SCREENSHOT_DIR}")
            except:
                pass
            browser.close()
            return pd.DataFrame()

if __name__ == "__main__":
    df = run_portal_scraper()
    if not df.empty:
        print("\nDados extraídos:")
        print(df.head(10))
    else:
        print("Nenhum dado. Veja os screenshots em logs/screenshots/")
