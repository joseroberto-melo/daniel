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
/* Importa a fonte premium Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.stApp { 
    background-color: #090d16; 
    color: #f1f5f9; 
}

/* Sidebar clean, sem bordas coloridas */
[data-testid="stSidebar"] { 
    background-color: #0d121f; 
    border-right: 1px solid #1e293b; 
}

/* Cards de métricas estilo SaaS (Stripe/Linear) */
[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
[data-testid="stMetricValue"] { 
    color: #ffffff !important; 
    font-size: 2rem !important; 
    font-weight: 700 !important; 
    letter-spacing: -0.02em;
}
[data-testid="stMetricLabel"] { 
    color: #9ca3af !important; 
    font-size: 0.8rem !important; 
    font-weight: 500 !important;
    text-transform: none; 
    letter-spacing: normal; 
}

h1, h2, h3 { 
    color: #ffffff !important; 
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

hr { 
    border-color: #1f2937 !important; 
}

/* Botão premium com transição suave */
.stButton > button {
    background: #4f46e5;
    color: #ffffff;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    transition: all 0.2s ease;
}
.stButton > button:hover { 
    background: #4338ca;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    transform: translateY(-1px); 
}

/* Inputs minimalistas */
.stTextInput input { 
    background-color: #111827 !important; 
    color: #f1f5f9 !important; 
    border: 1px solid #374151 !important; 
    border-radius: 8px !important; 
}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#9ca3af', size=12, family="Inter"), margin=dict(t=30, b=20, l=10, r=10),
    xaxis=dict(gridcolor='#1f2937', color='#9ca3af'),
    yaxis=dict(gridcolor='#1f2937', color='#9ca3af'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af')),
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
        <div style='font-size: 0.8rem; font-weight: 700; color: #818cf8; text-transform: uppercase; letter-spacing: 0.05em;'>Positiva Administradora</div>
        <div style='font-size: 1.25rem; font-weight: 800; color: #ffffff; margin-top: 4px; letter-spacing: -0.02em;'>Painel de Performance</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"<p style='font-size:0.75rem;color:#6b7280;margin-bottom:15px;'>{fonte}</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem;font-weight:600;color:#9ca3af;'>Filtros de Visão</p>", unsafe_allow_html=True)

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
    st.markdown(f"<p style='color:#4b5563;font-size:0.7rem;text-align:center;margin-top:10px;'>Sincronizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)

# ---- FILTRAR ----
df_f = df.copy() if not df.empty else pd.DataFrame()
if not df_f.empty:
    if sdr_filtro != "Todos SDRs" and sdr_col: df_f = df_f[df_f[sdr_col] == sdr_filtro]
    if ent_filtro != "Todas Entidades" and ent_col: df_f = df_f[df_f[ent_col] == ent_filtro]

# ---- HEADER ----
st.markdown("""<div style='background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 24px 32px; margin-bottom: 24px;'>
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;'>
        <div>
            <h1 style='margin: 0; font-size: 1.75rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;'>Visão Geral de Leads e Conversão</h1>
            <p style='margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;'>Consolidação comercial atualizada em tempo real</p>
        </div>
        <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; padding: 6px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;'>
            <span style='width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #10b981;'></span>
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

# Cores corporativas elegantes (escala de violetas e cinzas)
COLOR_THEME = ["#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe", "#e0e7ff"]

with col_l:
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 600; margin-bottom: 15px;'>Leads por Entidade</h3>", unsafe_allow_html=True)
    if not df_f.empty and ent_col:
        ec = df_f[ent_col].value_counts().reset_index()
        ec.columns = ['Entidade', 'Qtd']
        fig = px.pie(ec, names='Entidade', values='Qtd', hole=0.6,
                     color_discrete_sequence=COLOR_THEME)
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(textfont_color='white', textposition='inside', textinfo='percent')
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 600; margin-bottom: 15px;'>Top Status dos Leads</h3>", unsafe_allow_html=True)
    if not df_f.empty and sta_col2:
        sc = df_f[sta_col2].value_counts().head(8).reset_index()
        sc.columns = ['Status', 'Qtd']
        fig2 = px.bar(sc, x='Qtd', y='Status', orientation='h',
                      color_discrete_sequence=["#6366f1"], text='Qtd')
        fig2.update_layout(**PLOTLY_LAYOUT)
        fig2.update_traces(textfont_color='white', textposition='inside')
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

if not df_f.empty and sdr_col:
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 600; margin-bottom: 15px;'>Desempenho por Vendedor / SDR</h3>", unsafe_allow_html=True)
    sdr_c = df_f[sdr_col].value_counts().reset_index()
    sdr_c.columns = ['SDR', 'Leads']
    fig3 = px.bar(sdr_c, x='SDR', y='Leads', 
                  color_discrete_sequence=["#4f46e5"], text='Leads')
    fig3.update_layout(**PLOTLY_LAYOUT)
    fig3.update_traces(textfont_color='white', textposition='inside')
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

# ---- QUARTIS ----
st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; margin-bottom: 20px;'>Metas por Quartil</h3>", unsafe_allow_html=True)
quartis = [
    ("1º Quartil", "1 a 3 vidas", "R$ 7.348,50", "#94a3b8"),
    ("2º Quartil", "4 a 8 vidas", "R$ 14.697,00", "#6366f1"),
    ("3º Quartil", "9 a 12 vidas", "R$ 22.045,50", "#4f46e5"),
    ("4º Quartil ★", "13 a 18 vidas", "R$ 29.394,00", "#10b981"),
]
qcols = st.columns(4)
for i, (titulo, vidas, premio, cor) in enumerate(quartis):
    with qcols[i]:
        st.markdown(f"""<div style='background-color: #0f172a;
            border: 1px solid #1e293b; border-left: 4px solid {cor}; border-radius: 8px; padding: 20px; text-align: left;'>
            <div style='font-size:0.75rem; color:#6b7280; font-weight:600; text-transform:uppercase; letter-spacing:0.05em'>{titulo}</div>
            <div style='font-size:1.5rem; font-weight:800; color:#ffffff; margin:6px 0'>{vidas}</div>
            <div style='font-size:0.85rem; color:#94a3b8; font-weight:500'>Comissão: <span style='color:{cor}; font-weight:700'>{premio}/mês</span></div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ---- TABELA ----
st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; margin-bottom: 15px;'>Base de Dados Completa</h3>", unsafe_allow_html=True)
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
    
    # Customização da tabela Streamlit
    st.dataframe(dv[show].reset_index(drop=True), use_container_width=True, height=430)
else:
    st.warning("⚠️ Sem dados. Configure o Supabase ou rode o orquestrador localmente.")

st.divider()
st.markdown(f"<p style='text-align:center; color:#4b5563; font-size:0.75rem; padding: 20px 0;'>Positiva Administradora © {datetime.now().year} • Painel Corporativo</p>",
            unsafe_allow_html=True)
