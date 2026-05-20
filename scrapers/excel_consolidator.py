"""
Consolidador de Planilhas SDR - Positiva Administradora
Lê todas as planilhas .xlsx na pasta DocumentosBase (ou Google Drive local)
e consolida em um único CSV.
"""
import pandas as pd
import os
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "DocumentosBase")
OUTPUT_CSV = os.path.join(BASE_DIR, "dados_consolidados_teste.csv")

RELEVANT_SHEETS = [
    'CREMERJ', 'CREMESP', 'CFM', 'ASSEMPERJ', 'CRORJ',
    'CREASP', 'CREFITO', 'ODONTO', 'ABRIGO DO MARINHEIRO',
    'EMPRESARIAL-ADESÃO', 'EMPRESARIAL-ADES\u00c3O', 'PROJETO PME'
]

def extract_sdr_name(filename):
    base = os.path.basename(filename)
    if "(" in base and ")" in base:
        return base.split("(")[1].split(")")[0].strip()
    return base.replace(".xlsx", "").strip()

def read_one_spreadsheet(file_path):
    sdr_name = extract_sdr_name(file_path)
    try:
        xls = pd.ExcelFile(file_path)
    except Exception as e:
        print(f"  Erro ao abrir arquivo: {e}")
        return pd.DataFrame()

    frames = []
    for sheet in xls.sheet_names:
        sheet_upper = sheet.strip().upper()
        if sheet_upper in [s.upper() for s in RELEVANT_SHEETS]:
            try:
                df = pd.read_excel(xls, sheet_name=sheet)
                # Remove linhas completamente vazias
                df = df.dropna(how='all')
                # Padroniza colunas para minúsculo
                df.columns = [str(c).strip().lower() for c in df.columns]
                df['sdr_nome'] = sdr_name
                df['entidade'] = sheet.strip().upper()
                frames.append(df)
                print(f"    [{sheet}] {len(df)} linhas")
            except Exception as e:
                print(f"    Erro na aba {sheet}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def consolidate_all_sheets():
    print("Procurando planilhas em:", DOCS_DIR)
    xlsx_files = []

    # Busca na pasta DocumentosBase
    if os.path.exists(DOCS_DIR):
        for f in os.listdir(DOCS_DIR):
            if f.endswith(".xlsx") and not f.startswith("~"):
                xlsx_files.append(os.path.join(DOCS_DIR, f))

    # Busca na pasta raiz do projeto também
    for f in os.listdir(BASE_DIR):
        if f.endswith(".xlsx") and not f.startswith("~"):
            full = os.path.join(BASE_DIR, f)
            if full not in xlsx_files:
                xlsx_files.append(full)

    if not xlsx_files:
        print("  AVISO: Nenhuma planilha .xlsx encontrada.")
        return pd.DataFrame()

    print(f"  {len(xlsx_files)} planilha(s) encontrada(s).")
    all_data = []
    for fp in xlsx_files:
        sdr_name = extract_sdr_name(fp)
        print(f"  Processando SDR: {sdr_name}")
        df = read_one_spreadsheet(fp)
        if not df.empty:
            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\n  Total consolidado: {len(final_df)} linhas")
    print(f"  Salvo em: {OUTPUT_CSV}")
    return final_df

if __name__ == "__main__":
    consolidate_all_sheets()
