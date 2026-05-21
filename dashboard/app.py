import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Positiva BI - Painel de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""<style>
/* Importa a fonte San Francisco / Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", sans-serif !important;
    background-color: #000000 !important;
    color: #f5f5f7 !important;
}

/* Oculta os menus padrões do Streamlit para parecer um app nativo */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

/* Barra lateral premium integrada (estilo iPadOS) */
[data-testid="stSidebar"] { 
    background-color: #08080a !important; 
    border-right: 1px solid #1c1c1e !important; 
}

/* Cards de Métricas Estilo Apple (Space Gray Titanium) */
[data-testid="stMetric"] {
    background-color: #1c1c1e !important;
    border: 1px solid #2c2c2e !important;
    border-radius: 14px !important;
    padding: 24px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
}
[data-testid="stMetricValue"] { 
    color: #ffffff !important; 
    font-size: 2.2rem !important; 
    font-weight: 700 !important; 
    letter-spacing: -0.03em !important;
}
[data-testid="stMetricLabel"] { 
    color: #86868b !important; 
    font-size: 0.85rem !important; 
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    text-transform: none !important;
}

/* Títulos elegantes e limpos */
h1, h2, h3 { 
    color: #ffffff !important; 
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
}

hr { 
    border-color: #1c1c1e !important; 
}

/* Botões Nativos da Apple (Capsule azul clássico) */
.stButton > button {
    background-color: #0071e3 !important;
    color: #ffffff !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 8px 24px !important;
    font-size: 0.9rem !important;
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
.stButton > button:hover { 
    background-color: #147ce5 !important;
    transform: scale(1.02);
}

/* Inputs de texto elegantes e planos */
.stTextInput input { 
    background-color: #1c1c1e !important; 
    color: #ffffff !important; 
    border: 1px solid #2c2c2e !important; 
    border-radius: 10px !important; 
    padding: 12px 16px !important;
}

/* Selectboxes premium */
div[data-baseweb="select"] {
    background-color: #1c1c1e !important;
    border: 1px solid #2c2c2e !important;
    border-radius: 10px !important;
}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#86868b', size=12, family="-apple-system, Inter"), margin=dict(t=30, b=20, l=10, r=10),
    xaxis=dict(gridcolor='#1c1c1e', color='#86868b'),
    yaxis=dict(gridcolor='#1c1c1e', color='#86868b'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#86868b')),
    coloraxis_showscale=False,
)

# ---- CARREGAR DADOS (Supabase ou CSV local) ----
@st.cache_data(ttl=300)
def load_data():
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")

    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            sb = create_client(supabase_url, supabase_key)
            # Busca com paginação para passar do limite de 1.000 registros
            all_data = []
            page_size = 1000
            offset = 0
            while True:
                resp = sb.table("fct_oportunidades_sdr").select("*").range(offset, offset + page_size - 1).execute()
                batch = resp.data
                if not batch:
                    break
                all_data.extend(batch)
                if len(batch) < page_size:
                    break
                offset += page_size
            df = pd.DataFrame(all_data)
            st.session_state['fonte'] = f"☁️ Supabase (Nuvem) — {len(df):,} registros"
            return df
        except Exception as e:
            st.session_state['fonte'] = f"⚠️ Supabase falhou: {e} — usando CSV local"

    # Fallback: CSV local
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "dados_consolidados_teste.csv")
    if os.path.exists(csv_path):
        st.session_state['fonte'] = "💾 CSV Local"
        return pd.read_csv(csv_path, low_memory=False)

    st.session_state['fonte'] = "❌ Sem dados"
    return pd.DataFrame()

def find_col(df, keywords):
    for k in keywords:
        for c in df.columns:
            if k.lower() in c.lower():
                return c
    return None

df = load_data()
fonte = st.session_state.get('fonte', '...')

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("""<div style='padding: 20px 0 10px 0;'>
        <div style='font-size: 0.8rem; font-weight: 600; color: #86868b; text-transform: uppercase; letter-spacing: 0.05em;'>Positiva Administradora</div>
        <div style='font-size: 1.4rem; font-weight: 700; color: #ffffff; margin-top: 4px; letter-spacing: -0.03em;'>Performance</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"<p style='font-size:0.75rem;color:#86868b;margin-bottom:15px;'>{fonte}</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem;font-weight:600;color:#f5f5f7;'>Filtros de Visão</p>", unsafe_allow_html=True)

    sdr_col = find_col(df, ['sdr_nome'])
    ent_col = find_col(df, ['entidade'])
    sta_col = find_col(df, ['status'])

    sdr_vals = ["Todos SDRs"] + (sorted(df[sdr_col].dropna().unique().tolist()) if sdr_col and not df.empty else [])
    ent_vals = ["Todas Entidades"] + (sorted(df[ent_col].dropna().unique().tolist()) if ent_col and not df.empty else [])

    sdr_filtro = st.selectbox("👤 Filtrar SDR", sdr_vals)
    ent_filtro = st.selectbox("🏥 Filtrar Entidade", ent_vals)
    st.divider()
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"<p style='color:#86868b;font-size:0.7rem;text-align:center;margin-top:10px;'>Sincronizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)

# ---- FILTRAR ----
df_f = df.copy() if not df.empty else pd.DataFrame()
if not df_f.empty:
    if sdr_filtro != "Todos SDRs" and sdr_col: df_f = df_f[df_f[sdr_col] == sdr_filtro]
    if ent_filtro != "Todas Entidades" and ent_col: df_f = df_f[df_f[ent_col] == ent_filtro]

# ---- HEADER ----
st.markdown("""<div style='padding: 10px 0 20px 0; margin-bottom: 24px; border-bottom: 1px solid #1c1c1e;'>
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;'>
        <div>
            <h1 style='margin: 0; font-size: 2.2rem; font-weight: 700; color: #ffffff; letter-spacing: -0.04em;'>Visão Geral de Leads e Conversão</h1>
            <p style='margin: 4px 0 0 0; color: #86868b; font-size: 0.95rem; font-weight: 400;'>Consolidação comercial em tempo real</p>
        </div>
        <div style='background: rgba(48, 209, 88, 0.1); border: 1px solid rgba(48, 209, 88, 0.2); color: #30d158; padding: 6px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 500; display: inline-flex; align-items: center; gap: 6px;'>
            <span style='width: 6px; height: 6px; background-color: #30d158; border-radius: 50%; display: inline-block;'></span>
            Ao Vivo
        </div>
    </div>
</div>""", unsafe_allow_html=True)

# ---- KPIs ----
total = len(df_f)
sta_col2 = find_col(df_f, ['status'])
vidas_col = find_col(df_f, ['vidas', 'nº'])
vendas = perdas = analise = total_vidas = 0

if sta_col2 and not df_f.empty:
    sv = df_f[sta_col2].astype(str).str.upper()
    vendas   = int(sv.str.contains("GANHO|CONTRATOU|VENDA").sum())
    perdas   = int(sv.str.contains("PERDA").sum())
    analise  = int(sv.str.contains("ANALISE|ANÁLISE").sum())
if vidas_col and not df_f.empty:
    total_vidas = int(pd.to_numeric(df_f[vidas_col], errors='coerce').sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📋 Total de Leads", f"{total:,}")
c2.metric("✅ Vendas Ganhas", vendas, delta=f"+{vendas}")
c3.metric("❌ Perdas", perdas)
c4.metric("🔄 Em Análise", analise)
c5.metric("❤️ Total Vidas", f"{total_vidas:,}")
st.divider()

# ---- GRÁFICOS ----
col_l, col_r = st.columns([1.3, 1])

# Apple Palette: Blue, Purple, Orange, Green, Teal
APPLE_PALETTE = ["#007aff", "#af52de", "#ff9500", "#34c759", "#5ac8fa", "#ff3b30"]

with col_l:
    st.markdown("<h3 style='font-size: 1.15rem; font-weight: 600; margin-bottom: 15px; color:#ffffff;'>Leads por Entidade</h3>", unsafe_allow_html=True)
    if not df_f.empty and ent_col:
        ec = df_f[ent_col].value_counts().reset_index()
        ec.columns = ['Entidade', 'Qtd']
        fig = px.pie(ec, names='Entidade', values='Qtd', hole=0.7,
                     color_discrete_sequence=APPLE_PALETTE)
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(textfont_color='white', textposition='outside', textinfo='percent')
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown("<h3 style='font-size: 1.15rem; font-weight: 600; margin-bottom: 15px; color:#ffffff;'>Top Status dos Leads</h3>", unsafe_allow_html=True)
    if not df_f.empty and sta_col2:
        sc = df_f[sta_col2].value_counts().head(8).reset_index()
        sc.columns = ['Status', 'Qtd']
        fig2 = px.bar(sc, x='Qtd', y='Status', orientation='h',
                      color_discrete_sequence=["#007aff"], text='Qtd')
        fig2.update_layout(**PLOTLY_LAYOUT)
        fig2.update_traces(textfont_color='white', textposition='inside')
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

if not df_f.empty and sdr_col:
    st.markdown("<h3 style='font-size: 1.15rem; font-weight: 600; margin-bottom: 15px; color:#ffffff;'>Desempenho por Vendedor / SDR</h3>", unsafe_allow_html=True)
    sdr_c = df_f[sdr_col].value_counts().reset_index()
    sdr_c.columns = ['SDR', 'Leads']
    fig3 = px.bar(sdr_c, x='SDR', y='Leads', 
                  color_discrete_sequence=["#007aff"], text='Leads')
    fig3.update_layout(**PLOTLY_LAYOUT)
    fig3.update_traces(textfont_color='white', textposition='inside')
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

# ---- QUARTIS ----
st.markdown("<h3 style='font-size: 1.3rem; font-weight: 700; margin-bottom: 20px; color:#ffffff;'>Metas por Quartil</h3>", unsafe_allow_html=True)
quartis = [
    ("1º Quartil", "1 a 3 vidas", "R$ 7.348,50", "#8e8e93"),
    ("2º Quartil", "4 a 8 vidas", "R$ 14.697,00", "#007aff"),
    ("3º Quartil", "9 a 12 vidas", "R$ 22.045,50", "#af52de"),
    ("4º Quartil ★", "13 a 18 vidas", "R$ 29.394,00", "#34c759"),
]
qcols = st.columns(4)
for i, (titulo, vidas, premio, cor) in enumerate(quartis):
    with qcols[i]:
        st.markdown(f"""<div style='background-color: #1c1c1e;
            border: 1px solid #2c2c2e; border-radius: 12px; padding: 24px; text-align: left; box-shadow: 0 4px 20px rgba(0,0,0,0.3);'>
            <div style='font-size:0.75rem; color:#86868b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em'>{titulo}</div>
            <div style='font-size:1.75rem; font-weight:700; color:#ffffff; margin:8px 0; letter-spacing:-0.02em;'>{vidas}</div>
            <div style='font-size:0.85rem; color:#86868b; font-weight:400;'>Comissão: <span style='color:{cor}; font-weight:600;'>{premio}/mês</span></div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ---- TABELA ----
st.markdown("<h3 style='font-size: 1.3rem; font-weight: 700; margin-bottom: 15px; color:#ffffff;'>Base de Dados Completa</h3>", unsafe_allow_html=True)
sr, ex = st.columns([4, 1])
with sr:
    busca = st.text_input("", placeholder="🔍  Digite nome, telefone, entidade ou status para filtrar a tabela...")
with ex:
    if not df_f.empty:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.download_button("📥 Exportar Planilha (CSV)", df_f.to_csv(index=False).encode('utf-8-sig'),
                           f"positiva_leads_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

if not df_f.empty:
    dv = df_f.copy()
    if busca:
        mask = dv.apply(lambda r: r.astype(str).str.contains(busca, case=False, na=False).any(), axis=1)
        dv = dv[mask]
    prio = ['sdr_nome', 'entidade', 'nome', 'ddd', 'telefone']
    extras = [c for c in dv.columns if any(k in c.lower() for k in ['status', 'vida', 'canal', 'tipo', 'motivo'])]
    show = list(dict.fromkeys([c for c in prio + extras if c in dv.columns]))[:10]
    if not show: show = dv.columns.tolist()[:8]
    st.caption(f"Exibindo {len(dv):,} de {len(df_f):,} registros")
    
    st.dataframe(dv[show].reset_index(drop=True), use_container_width=True, height=430)
else:
    st.warning("⚠️ Sem dados. Configure o Supabase ou rode o orquestrador localmente.")

st.divider()
st.markdown(f"<p style='text-align:center; color:#86868b; font-size:0.75rem; padding: 25px 0;'>Positiva Administradora • Painel de Performance Corporativa © {datetime.now().year}</p>",
            unsafe_allow_html=True)
