#!/usr/bin/env python3
"""
Orquestrador Principal - Positiva Administradora
Salva no Supabase (nuvem) quando disponível, ou em CSV local como fallback.
"""
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

LOG_FILE = os.path.join(BASE_DIR, "logs", "ultima_atualizacao.log")

def log(msg):
    ts = datetime.now().strftime("[%H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run():
    log("=" * 52)
    log("  POSITIVA ADMINISTRADORA - ATUALIZACAO INICIADA")
    log(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    log("=" * 52)

    from database.upsert_logic import save_sdr_leads, save_callbox_data, save_portal_data

    # ---------- PASSO 1: PLANILHAS SDR ----------
    log("[1/3] Consolidando planilhas dos SDRs...")
    try:
        from scrapers.excel_consolidator import consolidate_all_sheets
        df_sdr = consolidate_all_sheets()
        if not df_sdr.empty:
            save_sdr_leads(df_sdr)
            log(f"  OK: {len(df_sdr)} leads das planilhas salvos.")
        else:
            log("  AVISO: Nenhum dado nas planilhas.")
    except Exception as e:
        log(f"  ERRO planilhas: {e}")

    # ---------- PASSO 2: CALLBOX ----------
    log("[2/3] Extraindo ligacoes do CallBox...")
    try:
        from scrapers.callbox_scraper import run_callbox_scraper
        df_cb = run_callbox_scraper()
        if not df_cb.empty:
            save_callbox_data(df_cb)
            log(f"  OK: {len(df_cb)} registros de ligacoes salvos.")
        else:
            log("  AVISO: Sem dados do CallBox.")
    except Exception as e:
        log(f"  ERRO CallBox: {e}")

    # ---------- PASSO 3: PORTAL POSITIVA ----------
    log("[3/3] Extraindo vendas do Portal Positiva...")
    try:
        from scrapers.portal_scraper import run_portal_scraper
        df_portal = run_portal_scraper()
        if not df_portal.empty:
            save_portal_data(df_portal)
            log(f"  OK: {len(df_portal)} linhas de vendas salvas.")
        else:
            log("  AVISO: Sem dados do Portal.")
    except Exception as e:
        log(f"  ERRO Portal: {e}")

    log("=" * 52)
    log("  ATUALIZACAO CONCLUIDA!")
    log("=" * 52)

if __name__ == "__main__":
    run()
