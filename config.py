import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    # CallBox Credentials
    CALLBOX_URL = "https://positiva.callbox.com.br/login.php"
    CALLBOX_USER = os.getenv("CALLBOX_USER", "Soomar_Supervisor")
    CALLBOX_PASS = os.getenv("CALLBOX_PASS", "Soomar@123")

    # Portal Positiva Credentials
    PORTAL_URL = "https://portal.positiva.com.br/vendas-analise"
    PORTAL_USER = os.getenv("PORTAL_USER", "adriana@stoppelli.com.br")
    PORTAL_PASS = os.getenv("PORTAL_PASS", "151515")

    # Supabase Credentials (Serão configuradas posteriormente)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    # Modos do Playwright
    HEADLESS = os.getenv("HEADLESS", "True").lower() in ('true', '1', 't')
