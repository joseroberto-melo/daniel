"""
Lógica de Banco de Dados - Supabase
Salva e atualiza dados de todas as fontes (SDR, CallBox, Portal) no Supabase.
"""
import os
import sys
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

def get_client():
    """Retorna o cliente Supabase configurado."""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        print("  AVISO: Supabase não configurado. Salvando só em CSV local.")
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception as e:
        print(f"  AVISO: Erro ao conectar Supabase: {e}")
        return None

def upsert_dataframe(df: pd.DataFrame, table_name: str, conflict_cols: list = None):
    """Salva um DataFrame no Supabase em lotes de 500 registros."""
    if df.empty:
        print(f"  DataFrame vazio — nada salvo em '{table_name}'.")
        return

    supabase = get_client()
    if not supabase:
        # Fallback: salva CSV localmente
        out = os.path.join(BASE_DIR, f"{table_name}.csv")
        df.to_csv(out, index=False, encoding='utf-8-sig')
        print(f"  Salvo localmente em: {out}")
        return

    # Limpa valores NaN (JSON não aceita NaN)
    df = df.where(pd.notnull(df), None)
    records = df.to_dict(orient="records")

    BATCH = 500
    total = len(records)
    saved = 0
    for i in range(0, total, BATCH):
        batch = records[i:i+BATCH]
        try:
            supabase.table(table_name).upsert(batch, on_conflict=",".join(conflict_cols) if conflict_cols else None).execute()
            saved += len(batch)
            print(f"  [{table_name}] Lote {i//BATCH + 1}: {saved}/{total} registros salvos.")
        except Exception as e:
            print(f"  ERRO no lote {i//BATCH + 1}: {e}")

def save_sdr_leads(df: pd.DataFrame):
    """Salva os leads das planilhas SDR."""
    if df.empty:
        return
    df['id'] = df.apply(
        lambda r: f"{str(r.get('sdr_nome',''))[:20]}_{str(r.get('entidade',''))[:10]}_{str(r.get('nome',''))[:30]}".replace(" ","_").lower(),
        axis=1
    )
    df['updated_at'] = datetime.now().isoformat()
    upsert_dataframe(df, "fct_oportunidades_sdr", conflict_cols=["id"])

def save_callbox_data(df: pd.DataFrame):
    """Salva os dados de ligações do CallBox."""
    if df.empty:
        return
    df['updated_at'] = datetime.now().isoformat()
    upsert_dataframe(df, "fct_ligacoes_callbox")

def save_portal_data(df: pd.DataFrame):
    """Salva os dados de vendas do Portal Positiva."""
    if df.empty:
        return
    df['updated_at'] = datetime.now().isoformat()
    upsert_dataframe(df, "fct_vendas_portal")
