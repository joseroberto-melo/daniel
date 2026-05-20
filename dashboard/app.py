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
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1424 100%); color: #e0e6f0; }
[data-testid="stSidebar"] { background: #0f1628; border-right: 1px solid rgba(0,242,254,0.15); }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(0,242,254,0.07), rgba(79,172,254,0.04));
    border: 1px solid rgba(0,242,254,0.2); border-radius: 16px; padding: 16px !important;
}
[data-testid="stMetricValue"] { color: #00f2fe !important; font-size: 1.8rem !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #8892a4 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
h1, h2, h3 { color: #ffffff !important; }
hr { border-color: rgba(0,242,254,0.12) !important; }
.stButton > button {
    background: linear-gradient(135deg, #00f2fe, #4facfe); color: #0a0e1a;
    font-weight: 700; border: none; border-radius: 10px; width: 100%;
}
.stButton > button:hover { box-shadow: 0 6px 20px rgba(0,242,254,0.4); transform: translateY(-1px); }
.stTextInput input { background: rgba(255,255,255,0.05) !important; color: #e0e6f0 !important; border: 1px solid rgba(0,242,254,0.3) !important; border-radius: 8px !important; }
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#c9d6ea', size=12), margin=dict(t=30, b=20, l=10, r=10),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892a4'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892a4'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8892a4')),
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
            resp = sb.table("fct_oportunidades_sdr").select("*").execute()
            df = pd.DataFrame(resp.data)
            st.session_state['fonte'] = "☁️ Supabase (Nuvem)"
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
    st.markdown("""<div style='text-align:center;padding:16px 0'>
        <div style='font-size:2.5rem'>📊</div>
        <div style='font-weight:900;font-size:1.1rem;color:#00f2fe;'>POSITIVA BI</div>
        <div style='color:#4a5568;font-size:0.75rem'>Painel Comercial</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"<p style='font-size:0.72rem;color:#4a5568'>Fonte: {fonte}</p>", unsafe_allow_html=True)
    st.markdown("**⚙️ Filtros**")

    sdr_col = find_col(df, ['sdr_nome'])
    ent_col = find_col(df, ['entidade'])
    sta_col = find_col(df, ['status'])

    sdr_vals = ["Todos"] + (sorted(df[sdr_col].dropna().unique().tolist()) if sdr_col and not df.empty else [])
    ent_vals = ["Todas"] + (sorted(df[ent_col].dropna().unique().tolist()) if ent_col and not df.empty else [])

    sdr_filtro = st.selectbox("👤 Vendedor / SDR", sdr_vals)
    ent_filtro = st.selectbox("🏥 Entidade / Conselho", ent_vals)
    st.divider()
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"<p style='color:#2d3748;font-size:0.7rem;text-align:center'>Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)

# ---- FILTRAR ----
df_f = df.copy() if not df.empty else pd.DataFrame()
if not df_f.empty:
    if sdr_filtro != "Todos" and sdr_col: df_f = df_f[df_f[sdr_col] == sdr_filtro]
    if ent_filtro != "Todas" and ent_col: df_f = df_f[df_f[ent_col] == ent_filtro]

# ---- HEADER ----
st.markdown("""<div style='background:linear-gradient(135deg,rgba(0,242,254,0.08),rgba(79,172,254,0.04));
    border:1px solid rgba(0,242,254,0.2);border-radius:20px;padding:24px 32px;margin-bottom:20px'>
    <span style='font-size:2rem;font-weight:900;background:linear-gradient(135deg,#00f2fe,#4facfe);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent'>📊 Positiva Administradora</span>
    <span style='background:rgba(0,242,254,0.15);border:1px solid rgba(0,242,254,0.3);
    color:#00f2fe;padding:3px 12px;border-radius:20px;font-size:0.75rem;margin-left:12px'>🟢 AO VIVO</span>
    <br><span style='color:#8892a4;font-size:0.9rem'>Painel unificado de Vendas, Cotações e Produtividade</span>
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

with col_l:
    st.markdown("### 🏥 Leads por Entidade")
    if not df_f.empty and ent_col:
        ec = df_f[ent_col].value_counts().reset_index()
        ec.columns = ['Entidade', 'Qtd']
        fig = px.pie(ec, names='Entidade', values='Qtd', hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(textfont_color='white')
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown("### 📊 Status dos Leads")
    if not df_f.empty and sta_col2:
        sc = df_f[sta_col2].value_counts().head(8).reset_index()
        sc.columns = ['Status', 'Qtd']
        fig2 = px.bar(sc, x='Qtd', y='Status', orientation='h',
                      color='Qtd', color_continuous_scale='Teal', text='Qtd')
        fig2.update_layout(**PLOTLY_LAYOUT)
        fig2.update_traces(textfont_color='white')
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

if not df_f.empty and sdr_col:
    st.markdown("### 👤 Leads por Vendedor / SDR")
    sdr_c = df_f[sdr_col].value_counts().reset_index()
    sdr_c.columns = ['SDR', 'Leads']
    fig3 = px.bar(sdr_c, x='SDR', y='Leads', color='Leads',
                  color_continuous_scale='Blues', text='Leads')
    fig3.update_layout(**PLOTLY_LAYOUT)
    fig3.update_traces(textfont_color='white')
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

# ---- QUARTIS ----
st.markdown("### 🏆 Metas por Quartil")
quartis = [
    ("1º Quartil", "1 a 3 vidas", "R$ 7.348,50", "#ef4444"),
    ("2º Quartil", "4 a 8 vidas", "R$ 14.697,00", "#f59e0b"),
    ("3º Quartil", "9 a 12 vidas", "R$ 22.045,50", "#f97316"),
    ("4º Quartil ★", "13 a 18 vidas", "R$ 29.394,00", "#10b981"),
]
qcols = st.columns(4)
for i, (titulo, vidas, premio, cor) in enumerate(quartis):
    with qcols[i]:
        st.markdown(f"""<div style='background:linear-gradient(135deg,{cor}15,{cor}05);
            border:1px solid {cor}50;border-radius:16px;padding:20px;text-align:center'>
            <div style='font-size:0.75rem;color:#8892a4;text-transform:uppercase;letter-spacing:0.1em'>{titulo}</div>
            <div style='font-size:1.5rem;font-weight:900;color:{cor};margin:8px 0'>{vidas}</div>
            <div style='font-size:0.9rem;color:#c9d6ea;font-weight:600'>{premio}/mês</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ---- TABELA ----
st.markdown("### 🔍 Base de Dados — Todos os Leads")
sr, ex = st.columns([4, 1])
with sr:
    busca = st.text_input("", placeholder="🔍  Buscar por nome, telefone, entidade, status...")
with ex:
    if not df_f.empty:
        st.download_button("📥 Exportar CSV", df_f.to_csv(index=False).encode('utf-8-sig'),
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
st.markdown(f"<p style='text-align:center;color:#1a2035;font-size:0.75rem'>Positiva Administradora © {datetime.now().year}</p>",
            unsafe_allow_html=True)
