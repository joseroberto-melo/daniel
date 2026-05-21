"""
Lógica de Banco de Dados - Supabase
Salva e atualiza dados de todas as fontes (SDR, CallBox, Portal) no Supabase.
"""
import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Carrega .env se existir (ambiente local)
load_dotenv()

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

def clean_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """Converte tipos incompatíveis com JSON para string/None."""
    import math
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].apply(lambda v: (
            None if (v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))))
            else str(v) if hasattr(v, 'isoformat') or not isinstance(v, (str, int, float, bool, type(None)))
            else v
        ))
    return df

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

    # Converte via JSON para garantir tipos nativos Python (trata NaN, Inf, datetime)
    import json
    records = json.loads(df.to_json(orient="records", date_format="iso", default_handler=str))

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
    """Salva os leads das planilhas SDR mapeando para o schema da tabela."""
    if df.empty:
        return
    import json as _json

    # Colunas conhecidas no Supabase (exatas)
    KNOWN = {'id', 'sdr_nome', 'entidade', 'nome', 'ddd', 'telefone',
             'email', 'status', 'canal', 'tipo_cotacao', 'n_vidas',
             'motivo', 'data_solicitacao', 'data_envio', 'extra', 'updated_at'}

    # Mapeamento de nomes das colunas do Excel → campos da tabela
    COL_MAP = {
        'e-mail': 'email', 'email': 'email',
        'tipo de cotação': 'tipo_cotacao', 'tipo de cotacao': 'tipo_cotacao',
        'n° vidas': 'n_vidas', 'nº vidas': 'n_vidas', 'n vidas': 'n_vidas',
        'motivo da perda': 'motivo', 'motivo': 'motivo',
        'data da solicitação': 'data_solicitacao', 'data da solicitacao': 'data_solicitacao',
        'data do envio': 'data_envio',
        'status finalizadores': 'status',
    }

    import json as _json
    rows = []
    for i, (_, row) in enumerate(df.iterrows()):
        record = {'updated_at': datetime.now().isoformat()}
        extra = {}
        for col, val in row.items():
            col_lower = str(col).strip().lower()
            mapped = COL_MAP.get(col_lower, col_lower)
            # Converte valor para tipo serializável
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            elif isinstance(val, float):
                import math
                val = None if (math.isnan(val) or math.isinf(val)) else val
            elif not isinstance(val, (str, int, float, bool, type(None))):
                val = str(val)

            if mapped in KNOWN:
                record[mapped] = val
            else:
                extra[col_lower] = val

        record['extra'] = _json.dumps(extra, ensure_ascii=False, default=str)
        # Gera ID único
        record['id'] = f"{str(record.get('sdr_nome',''))[:12]}_{str(record.get('entidade',''))[:8]}_{i}".replace(" ", "_").lower()
        rows.append(record)

    df_clean = pd.DataFrame(rows)
    upsert_dataframe(df_clean, "fct_oportunidades_sdr", conflict_cols=["id"])

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
