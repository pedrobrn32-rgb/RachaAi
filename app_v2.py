"""
Racha Ai! - App Principal Refatorado
Versão 2.0: Seguro, Rápido, User-Friendly, Free
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime
import base64
import requests
import json

from google.cloud import storage

from models.participante import Participante
from models.despesa import Despesa, CATEGORIAS
from models.grupo import Grupo, TIPOS_EVENTO
from utils.calculos import Calculadora
from utils.algoritmo_divisao import AlgoritmoDivisao
from utils.formatacao import Formatador
from utils.renderizador import Renderizador
from utils.validators import (
    sanitize_input, validate_username, parse_valor, validate_data
)
from utils.components import (
    card_despesa, card_participante, card_pagamento,
    alert_info, alert_sucesso, alert_erro, alert_aviso, divider, link_compartilhamento
)

from config import (
    GCS_BUCKET_NAME, ADMIN_USER, BASE_URL, MOEDAS,
    SESSION_TIMEOUT_MINS, PAGE_SIZE_DESPESAS, PAGE_SIZE_GRUPOS, logger
)
from services.gcs import GCSManager
from services.cache import StreamlitCache
from services.auth import AuthService, LoginManager

# ═══════════════════════════════════════════════════════════════════
# ─── INICIALIZAÇÃO ───
# ═══════════════════════════════════════════════════════════════════

# Sidebar starts open; closes (persists collapsed) after a group is clicked.
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

st.set_page_config(
    page_title="Racha Aí!",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state,
)

# ─── Tema global (Plus Jakarta Sans + Verde Esmeralda, alinhado ao DESIGN.md) ───
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{
    color-scheme:light only !important;
    --primary:#006c49;--primary-dark:#004d2e;--primary-light:#10b981;
    --bg:#f8f9ff;--surface:#ffffff;--text:#0b1c30;--text-soft:#3c4a42;
    --border:#e6ebf5;--shadow:0 4px 20px rgba(30,41,59,.06);--radius:16px}
/* Tipografia global */
html,body,[class*="css"],[data-testid="stAppViewContainer"],
[data-testid="stSidebar"]{font-family:'Plus Jakarta Sans',sans-serif !important}
/* Light mode forçado (evita dark-mode vazando nas cores) */
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],.main,.block-container,
[data-testid="stHeader"],[data-testid="stToolbar"]{
    background-color:var(--bg) !important;color:var(--text) !important;color-scheme:light !important}
[data-testid="stHeader"]{background:transparent !important}
.main .block-container{padding-top:1.2rem;max-width:1200px}
p,span,h1,h2,h3,h4,h5,h6,li,td,th,label,caption,
.stMarkdown,.stCaption,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,
[data-baseweb="tab"]{color:var(--text) !important}
h1,h2,h3{font-weight:700 !important;letter-spacing:-.01em}
/* Inputs */
input,textarea,[data-baseweb="input"] input,
[data-baseweb="select"] span,[data-baseweb="select"] div,
[data-baseweb="select"] p,.stSelectbox [class*="singleValue"],
[class*="placeholder"]{color:var(--text) !important}
[data-baseweb="input"],[data-baseweb="select"],
.stTextInput>div>div,.stSelectbox>div>div,.stMultiSelect>div>div,
.stNumberInput>div>div,.stDateInput>div>div{
    background:var(--surface) !important;border-color:var(--border) !important;border-radius:12px !important}
[data-baseweb="input"]:focus-within,.stTextInput>div>div:focus-within,
.stNumberInput>div>div:focus-within{
    border-color:var(--primary) !important;box-shadow:0 0 0 3px rgba(0,108,73,.12) !important}
[data-baseweb="popover"],[data-baseweb="menu"],
[data-baseweb="select"] ul,[role="listbox"]{background:var(--surface) !important}
[data-baseweb="menu"] li,[role="option"]{color:var(--text) !important;background:var(--surface) !important}
[data-baseweb="menu"] li:hover,[role="option"]:hover{background:#f0fdf4 !important}
[data-baseweb="tag"]{background:#e8f5e9 !important;color:var(--primary-dark) !important;border-radius:8px !important}
.stTabs [data-baseweb="tab"]{opacity:.7;font-weight:600}
.stTabs [aria-selected="true"]{opacity:1 !important;color:var(--primary) !important}
/* Cards: containers com borda viram cards suaves */
[data-testid="stVerticalBlockBorderWrapper"]{
    background:var(--surface) !important;border:1px solid var(--border) !important;
    border-radius:var(--radius) !important;box-shadow:var(--shadow) !important}
/* Métricas (texto, sem caixa dupla dentro dos cards) */
[data-testid="stMetricValue"]{color:var(--primary) !important;font-weight:800 !important}
[data-testid="stMetricLabel"]{color:var(--text-soft) !important}
/* Componente Tailwind (iframe) sem moldura */
[data-testid="stIFrame"],iframe{border:none !important}
/* BOTOES */
html body [data-testid="stApp"] .main button,
html body [data-testid="stApp"] [data-testid="stMainBlockContainer"] button{
    background-color:var(--surface) !important;color:var(--text) !important;
    border:1px solid var(--border) !important;border-radius:999px;font-weight:600;transition:all .15s ease}
html body [data-testid="stApp"] .main button *{color:inherit !important;background-color:transparent !important}
html body [data-testid="stApp"] .main button:hover{
    background-color:#f0fdf4 !important;border-color:var(--primary) !important;
    color:var(--primary) !important;transform:translateY(-1px)}
html body [data-testid="stApp"] .main button:active{transform:translateY(0) scale(.98)}
html body [data-testid="stApp"] .main .stFormSubmitButton button,
html body [data-testid="stApp"] .main [data-testid="baseButton-primary"]{
    background:linear-gradient(135deg,var(--primary) 0%,var(--primary-light) 100%) !important;
    color:#fff !important;border:none !important;box-shadow:0 4px 14px rgba(0,108,73,.25) !important}
html body [data-testid="stApp"] .main .stFormSubmitButton button:hover,
html body [data-testid="stApp"] .main [data-testid="baseButton-primary"]:hover{
    filter:brightness(1.06);color:#fff !important;transform:translateY(-1px)}
/* SIDEBAR */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#006c49 0%,#004d2e 100%) !important}
[data-testid="stSidebar"] *{color:#fff !important}
[data-testid="stSidebar"] button{
    background:rgba(255,255,255,0.15) !important;color:#ffffff !important;
    border:1px solid rgba(255,255,255,0.3) !important;border-radius:12px;width:100%;
    margin-bottom:5px;padding:8px 14px;font-weight:600}
[data-testid="stSidebar"] button:hover{background:rgba(255,255,255,0.28) !important}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]{align-items:center !important;gap:6px !important}
[data-testid="stSidebar"] [data-testid="column"] + [data-testid="column"] button{
    background:rgba(255,255,255,0.06) !important;border:1px solid rgba(255,255,255,0.18) !important;
    border-radius:10px !important;padding:0 !important;margin:0 0 5px 0 !important;
    width:38px !important;height:38px !important;min-height:38px !important;
    display:flex !important;align-items:center !important;justify-content:center !important;
    font-size:1rem;opacity:.85}
[data-testid="stSidebar"] [data-testid="column"] + [data-testid="column"] button:hover{
    background:rgba(239,68,68,0.85) !important;border-color:rgba(239,68,68,0.9) !important;
    opacity:1;transform:none !important}
/* Mobile */
@media (max-width:640px){.main .block-container{padding-left:1rem;padding-right:1rem}}
</style>""", unsafe_allow_html=True)

# ─── Sidebar + polimento profissional ───
st.markdown("""<style>
/* Sidebar mais larga e com profundidade */
[data-testid="stSidebar"]{box-shadow:4px 0 24px rgba(0,0,0,.14)}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.18) !important;margin:.6rem 0}
[data-testid="stSidebar"] .stButton button{
    text-align:left !important;justify-content:flex-start !important;border-radius:10px !important}
[data-testid="stSidebar"] .stButton button:hover{transform:translateX(3px)}
/* DESKTOP: barra sempre aberta e fixa (esconde o botao de recolher) */
@media (min-width:768px){
    [data-testid="stSidebar"]{width:300px !important;min-width:300px !important}
    [data-testid="stSidebarCollapseButton"],
    [data-testid="baseButton-headerNoPadding"]{display:none !important}
}
/* Botao de ABRIR a barra (>>>) destacado como "Menu" (visivel no mobile) */
[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{
    background:linear-gradient(135deg,#006c49,#10b981) !important;
    border-radius:999px !important;padding:8px 14px !important;left:12px !important;top:12px !important;
    box-shadow:0 6px 18px rgba(0,108,73,.4) !important;
    display:flex !important;align-items:center !important;gap:6px !important;
    animation:pulseMenu 2.2s ease-in-out infinite}
[data-testid="stSidebarCollapsedControl"] svg,[data-testid="collapsedControl"] svg{
    color:#fff !important;fill:#fff !important;width:22px !important;height:22px !important}
[data-testid="stSidebarCollapsedControl"]::after,[data-testid="collapsedControl"]::after{
    content:"Menu";color:#fff;font-weight:700;font-size:.9rem;letter-spacing:.01em}
@keyframes pulseMenu{0%,100%{box-shadow:0 6px 18px rgba(0,108,73,.4)}
    50%{box-shadow:0 6px 28px rgba(16,185,129,.75)}}
/* Polimento de superficies */
[data-testid="stForm"]{border:1px solid var(--border) !important;border-radius:18px !important;
    box-shadow:var(--shadow) !important;padding:8px 6px}
[data-testid="stExpander"]{border:1px solid var(--border) !important;border-radius:14px !important;
    box-shadow:var(--shadow) !important;overflow:hidden}
.stAlert{border-radius:14px !important;border:1px solid var(--border) !important}
[data-testid="stIFrame"]{border-radius:16px;overflow:hidden}
h2,h3{margin-top:.2rem}
</style>""", unsafe_allow_html=True)

fmt = Formatador()


def render_tailwind(html: str, height: int):
    """Renderiza HTML Tailwind (read-only) num iframe sandbox do Streamlit.

    Botões dentro do HTML não disparam rerun do Streamlit — por isso usamos
    Tailwind só para exibição e mantemos widgets nativos para as ações.
    """
    components.html(html, height=height, scrolling=True)


def page_banner(icon, title, eyebrow="", gradient="linear-gradient(135deg,#006c49,#10b981)"):
    """Vibrant gradient page header for native screens."""
    eyebrow_html = (
        f'<div style="color:rgba(255,255,255,.8);font-size:.72rem;font-weight:700;'
        f'letter-spacing:.12em;text-transform:uppercase;margin-bottom:2px">{eyebrow}</div>'
        if eyebrow else ""
    )
    st.markdown(
        f'<div style="background:{gradient};padding:18px 22px;border-radius:18px;'
        f'margin-bottom:18px;box-shadow:0 10px 26px rgba(0,108,73,.22);position:relative;overflow:hidden">'
        f'<div style="position:absolute;right:-26px;top:-30px;width:120px;height:120px;'
        f'border-radius:50%;background:rgba(255,255,255,.12)"></div>'
        f'{eyebrow_html}'
        f'<div style="color:#fff;font-size:1.5rem;font-weight:800;position:relative">{icon} {title}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─── Session State (Inicialização) ───
def init_session_state():
    """Inicializa session state com dados do GCS"""
    if "gcs_manager" not in st.session_state:
        st.session_state.gcs_manager = GCSManager()
    
    if "dados" not in st.session_state:
        # Carrega do GCS uma única vez
        st.session_state.dados = st.session_state.gcs_manager.get_data(use_cache=True)
        st.session_state.usuarios = st.session_state.dados.get("usuarios", {})
        # Desserializa grupos: o GCS guarda como dict, mas o app todo usa como
        # objeto Grupo (.nome, .participantes, .to_dict()...). Converte na entrada.
        raw_grupos = st.session_state.dados.get("grupos", {})
        st.session_state.grupos = {
            gid: (g if isinstance(g, Grupo) else Grupo.from_dict(g))
            for gid, g in raw_grupos.items()
        }
        st.session_state.pagamentos = st.session_state.dados.get("pagamentos", {})
    
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = None
    
    if "grupo_ativo_id" not in st.session_state:
        st.session_state.grupo_ativo_id = None
    
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    if "editando_despesa" not in st.session_state:
        st.session_state.editando_despesa = None
    
    StreamlitCache.init()

init_session_state()

# ─── Funções Auxiliares ───
@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def obter_cotacao(moeda: str, data_str: str) -> float:
    """Obtém cotação da moeda (com cache de 1h)"""
    if moeda == "BRL":
        return 1.0
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d")
        d = dt.strftime("%Y%m%d")
        url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={d}&end_date={d}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json():
            return float(r.json()[0]["bid"])
        url2 = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
        r2 = requests.get(url2, timeout=5)
        if r2.status_code == 200:
            return float(r2.json()[f"{moeda}BRL"]["bid"])
    except Exception as e:
        logger.warning(f"Erro ao obter cotação: {e}")
    return 1.0

def formatar_valor(valor, moeda="BRL"):
    """Formata valor monetário"""
    s = MOEDAS.get(moeda, {}).get("simbolo", "R$")
    if valor < 0:
        return f"- {s} {abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def salvar_dados():
    """Salva dados atomicamente no GCS"""
    dados = {
        "usuarios": st.session_state.usuarios,
        "grupos": {
            gid: (g.to_dict() if hasattr(g, "to_dict") else g)
            for gid, g in st.session_state.grupos.items()
        },
        "pagamentos": st.session_state.pagamentos,
    }
    if st.session_state.gcs_manager.save_data(dados):
        logger.info("✅ Dados salvos com sucesso")
        return True
    else:
        logger.error("❌ Erro ao salvar dados")
        alert_erro("Erro ao salvar. Tente novamente.")
        return False

def user_info(username=None):
    """Retorna informações do usuário"""
    u = username or st.session_state.usuario_logado
    return st.session_state.usuarios.get(u, {})

def is_admin():
    """Verifica se usuário é admin"""
    return st.session_state.usuario_logado == ADMIN_USER

def get_grupo_ativo():
    """Retorna grupo ativo"""
    gid = st.session_state.grupo_ativo_id
    if gid and gid in st.session_state.grupos:
        return st.session_state.grupos[gid]
    return None

def calcular_transferencias(grupo):
    """Calcula transferências mínimas"""
    calc = Calculadora(grupo)
    saldos = calc.saldos()
    devedores = [[pid, -s] for pid, s in saldos.items() if s < -0.01]
    credores = [[pid, s] for pid, s in saldos.items() if s > 0.01]
    devedores.sort(key=lambda x: x[1], reverse=True)
    credores.sort(key=lambda x: x[1], reverse=True)
    transferencias = []
    i, j = 0, 0
    while i < len(devedores) and j < len(credores):
        deve, recebe = devedores[i][1], credores[j][1]
        valor = min(deve, recebe)
        if valor > 0.01:
            transferencias.append({
                "de": devedores[i][0],
                "para": credores[j][0],
                "valor": round(valor, 2),
            })
        devedores[i][1] -= valor
        credores[j][1] -= valor
        if devedores[i][1] < 0.01:
            i += 1
        if credores[j][1] < 0.01:
            j += 1
    return transferencias

# ═══════════════════════════════════════════════════════════════════
# ─── TELAS DE AUTENTICAÇÃO ───
# ═══════════════════════════════════════════════════════════════════

def tela_login():
    """Tela de login e registro"""
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        logo = load_image_b64("logo.png")
        logo_html = (
            f'<img src="data:image/png;base64,{logo}" '
            f'style="width:84px;height:84px;border-radius:20px;object-fit:contain;'
            f'background:rgba(255,255,255,.18);padding:8px">'
        ) if logo else '<div style="font-size:3.4rem;line-height:1">💸</div>'
        st.markdown(
            f'<div style="text-align:center;padding:34px 20px;border-radius:24px;margin:8px 0 20px;'
            f'background:linear-gradient(135deg,#006c49 0%,#10b981 100%);'
            f'box-shadow:0 12px 30px rgba(0,108,73,.30)">'
            f'{logo_html}'
            f'<div style="font-size:2rem;font-weight:800;color:#fff;letter-spacing:-.02em;margin-top:12px">Racha Aí!</div>'
            f'<div style="color:rgba(255,255,255,.92);font-size:1rem;margin-top:4px">Divida contas com segurança e praticidade</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        tab1, tab2 = st.tabs(["🔓 Entrar", "🆕 Cadastro"])
        
        with tab1:
            with st.form("login_form"):
                user = st.text_input("👤 Usuário", placeholder="seu_usuario").strip().lower()
                senha = st.text_input("🔑 Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    if user and senha:
                        sucesso, msg = LoginManager.login(user, senha, st.session_state.usuarios)
                        if sucesso:
                            st.session_state.usuario_logado = user
                            salvar_dados()
                            st.success(msg)
                            st.rerun()
                        else:
                            alert_erro(msg)
                    else:
                        alert_erro("Preencha todos os campos")
        
        with tab2:
            with st.form("registro_form"):
                novo_user = st.text_input(
                    "👤 Usuário", 
                    placeholder="seu_usuario"
                ).strip().lower()
                nome = st.text_input("📝 Nome completo", placeholder="Seu Nome")
                nova_senha = st.text_input("🔑 Senha", type="password", placeholder="Mín 6 caracteres")
                tipo_pix = st.selectbox("💳 Tipo PIX", ["CPF", "E-mail", "Telefone", "Aleatória"])
                pix = st.text_input("📱 Chave PIX", placeholder="123.456.789-00")
                foto = st.file_uploader("🖼️ Foto (opcional)", type=["png", "jpg", "jpeg"])
                submit = st.form_submit_button("Criar Conta", use_container_width=True)
                
                if submit:
                    foto_b64 = None
                    if foto:
                        foto_b64 = base64.b64encode(foto.read()).decode()
                    
                    sucesso, msg = LoginManager.registrar(
                        username=novo_user,
                        senha=nova_senha,
                        nome=nome,
                        usuarios=st.session_state.usuarios,
                        pix=pix,
                        tipo_pix=tipo_pix,
                        foto=foto_b64,
                    )
                    
                    if sucesso:
                        st.session_state.usuario_logado = novo_user
                        salvar_dados()
                        alert_sucesso(f"Bem-vindo, {nome}! 🎉")
                        st.rerun()
                    else:
                        alert_erro(msg)

# ═══════════════════════════════════════════════════════════════════
# ─── SIDEBAR ───
# ═══════════════════════════════════════════════════════════════════

def render_sidebar():
    """Renderiza sidebar com navegação"""
    user = st.session_state.usuario_logado
    uinfo = user_info()
    grupo = get_grupo_ativo()
    
    with st.sidebar:
        logo = load_image_b64("logo.png")
        logo_html = (
            f'<img src="data:image/png;base64,{logo}" '
            f'style="width:40px;height:40px;border-radius:10px;object-fit:contain;'
            f'background:rgba(255,255,255,.12);padding:3px;flex:0 0 auto">'
        ) if logo else '<span style="font-size:1.7rem;line-height:1">💸</span>'
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin:2px 0 12px">'
            f'{logo_html}'
            f'<span style="font-size:1.45rem;font-weight:800;color:#fff;'
            f'letter-spacing:-.02em;line-height:1.1">Racha Aí!</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        foto = uinfo.get("foto")
        nome = uinfo.get("nome", user)
        if foto:
            st.markdown(
                f'<img src="data:image/png;base64,{foto}" '
                f'style="width:28px;height:28px;border-radius:50%;object-fit:cover;'
                f'border:2px solid rgba(255,255,255,0.5);vertical-align:middle"> <b>{nome}</b>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"👤 **{nome}**")
        
        if is_admin():
            st.caption("🔑 Admin")
        
        divider()
        
        if grupo:
            st.markdown(f"#### 📌 {grupo.nome}")
            st.caption(f"{grupo.tipo_evento} • {len(grupo.participantes)} pessoas")
            divider()
            
            for key, label, icon in [
                ("dashboard", "Despesas", "📊"),
                ("adicionar", "Nova Despesa", "➕"),
                ("participantes", "Participantes", "👥"),
                ("fechamento", "Fechamento", "💰"),
            ]:
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
        
        divider()
        
        if st.button("👤 Meu Perfil", key="nav_perfil", use_container_width=True):
            st.session_state.page = "perfil"
            st.rerun()
        
        if is_admin():
            if st.button("🔑 Admin", key="nav_admin", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()
        
        divider()
        st.markdown("**📁 Meus Grupos:**")
        
        meus_grupos = {
            gid: g for gid, g in st.session_state.grupos.items()
            if any(p.id == user for p in g.participantes)
        }
        
        if meus_grupos:
            for gid, g in list(meus_grupos.items())[:PAGE_SIZE_GRUPOS]:
                transferencias_grp = calcular_transferencias(g)
                pagamentos_grp = st.session_state.pagamentos.get(gid, {})
                all_paid = all(
                    f"{t['de']}->{t['para']}" in pagamentos_grp 
                    for t in transferencias_grp
                )
                icon = "✅" if all_paid else ("📌" if gid == st.session_state.grupo_ativo_id else "📂")
                pode_deletar = (g.criado_por == user) or is_admin()
                
                if pode_deletar:
                    c1, c2 = st.columns([6, 1], gap="small")
                    with c1:
                        if st.button(f"{icon} {g.nome}", key=f"grp_{gid}", use_container_width=True):
                            st.session_state.grupo_ativo_id = gid
                            st.session_state.page = "dashboard"
                            st.session_state.sidebar_state = "collapsed"
                            st.query_params["grupo"] = gid
                            st.rerun()
                    with c2:
                        if st.button("🗑️", key=f"delgrp_{gid}", help="Deletar"):
                            del st.session_state.grupos[gid]
                            if st.session_state.grupo_ativo_id == gid:
                                st.session_state.grupo_ativo_id = None
                            salvar_dados()
                            alert_sucesso("Grupo deletado")
                            st.rerun()
                else:
                    if st.button(f"{icon} {g.nome}", key=f"grp_{gid}", use_container_width=True):
                        st.session_state.grupo_ativo_id = gid
                        st.session_state.page = "dashboard"
                        st.session_state.sidebar_state = "collapsed"
                        st.query_params["grupo"] = gid
                        st.rerun()
        else:
            st.caption("😴 Nenhum grupo ainda")
        
        if st.button("➕ Novo Grupo", key="criar_grupo_btn", use_container_width=True):
            st.session_state.page = "criar_grupo"
            st.rerun()
        
        divider()
        if st.button("🚪 Sair", key="logout_btn", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# ─── TELAS PRINCIPAIS ───
# ═══════════════════════════════════════════════════════════════════

def tela_criar_grupo():
    """Tela para criar novo grupo"""
    page_banner("➕", "Criar Novo Grupo", "Grupo")
    with st.form("form_novo_grupo"):
        nome = st.text_input("📝 Nome do grupo", placeholder="Ex: Viagem Rio 2026")
        desc = st.text_input("📋 Descrição", placeholder="Ex: Gastos da viagem")
        tipo = st.selectbox("🎫 Tipo de evento", TIPOS_EVENTO)
        submit = st.form_submit_button("Criar", use_container_width=True)
        
        if submit:
            if nome:
                slug = "".join(
                    c for c in nome.lower().replace(" ", "-") 
                    if c.isalnum() or c == "-"
                )[:30]
                
                if slug in st.session_state.grupos:
                    slug += f"-{len(st.session_state.grupos)}"
                
                user = st.session_state.usuario_logado
                uinfo = user_info()
                
                novo = Grupo(
                    nome=nome, descricao=desc, tipo_evento=tipo,
                    id=slug, criado_por=user
                )
                novo.adicionar_participante(Participante(
                    nome=uinfo.get("nome", user),
                    chave_pix=uinfo.get("pix", ""),
                    tipo_chave_pix=uinfo.get("tipo_pix", "CPF"),
                    id=user,
                ))
                
                st.session_state.grupos[slug] = novo
                st.session_state.grupo_ativo_id = slug
                st.session_state.page = "dashboard"
                st.query_params["grupo"] = slug
                salvar_dados()
                
                alert_sucesso(f'Grupo "{nome}" criado! 🎉')
                st.rerun()
            else:
                alert_erro("Informe o nome do grupo")
    
    st.markdown("---")
    st.info("💡 Compartilhe o link do grupo com seus amigos para que entrem automaticamente!")

def tela_dashboard():
    """Dashboard de despesas"""
    grupo = get_grupo_ativo()
    if not grupo:
        return
    
    if not grupo.despesas:
        st.markdown(f"## 📊 Despesas — {grupo.nome}")
        alert_info("Sem despesas", "Clique em 'Nova Despesa' para adicionar sua primeira")
        link_compartilhamento(st.session_state.grupo_ativo_id)
    else:
        # ─── Visão geral (design Tailwind, read-only) ───
        n_recentes = min(5, len(grupo.despesas))
        altura = 620 + n_recentes * 84 + len(grupo.participantes) * 84
        render_tailwind(Renderizador(grupo).render_dashboard(), height=altura)

        # ─── Gestão de despesas (widgets nativos para editar/excluir) ───
        st.markdown("### 🧾 Gerenciar despesas")

        # Paginação
        despesas_sorted = sorted(grupo.despesas, key=lambda x: x.data, reverse=True)
        page = st.number_input(
            "Página",
            1,
            (len(despesas_sorted) // PAGE_SIZE_DESPESAS) + 1,
            key="pag_despesa"
        )
        start = (page - 1) * PAGE_SIZE_DESPESAS
        end = start + PAGE_SIZE_DESPESAS
        
        for d in despesas_sorted[start:end]:
            pag = grupo.get_participante(d.pagador_id)
            acao = card_despesa(d, grupo)
            if acao == "edit":
                st.session_state.editando_despesa = d.id
                st.rerun()
            elif acao == "delete":
                grupo.remover_despesa(d.id)
                salvar_dados()
                alert_sucesso("Despesa removida")
                st.rerun()

            if st.session_state.editando_despesa == d.id:
                st.markdown("---")
                with st.form(f"form_edit_{d.id}"):
                    st.markdown("### ✏️ Editando despesa")
                    desc = st.text_input("Descrição", value=d.descricao, key=f"ed_desc_{d.id}")
                    cat = st.selectbox(
                        "Categoria",
                        CATEGORIAS,
                        index=CATEGORIAS.index(d.categoria),
                        key=f"ed_cat_{d.id}"
                    )
                    valor_txt = st.text_input(
                        "Valor",
                        value=str(d.valor).replace(".", ","),
                        key=f"ed_val_{d.id}"
                    )
                    
                    pagador = st.selectbox(
                        "Pagador",
                        grupo.participantes,
                        index=next(
                            (i for i, p in enumerate(grupo.participantes) if p.id == d.pagador_id),
                            0
                        ),
                        format_func=lambda p: p.nome,
                        key=f"ed_pag_{d.id}"
                    )
                    
                    data = st.date_input(
                        "Data",
                        value=datetime.strptime(d.data, "%Y-%m-%d").date(),
                        format="DD/MM/YYYY",
                        key=f"ed_data_{d.id}"
                    )
                    
                    nomes_todos = [p.nome for p in grupo.participantes]
                    nomes_atuais = [
                        grupo.get_participante(pid).nome
                        for pid in d.participantes_ids
                        if grupo.get_participante(pid)
                    ]
                    divisao = st.multiselect(
                        "Dividir entre",
                        nomes_todos,
                        default=nomes_atuais,
                        key=f"ed_div_{d.id}"
                    )
                    
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.form_submit_button("💾 Salvar", use_container_width=True):
                            valor = parse_valor(valor_txt)
                            if desc and valor and divisao:
                                d.descricao = desc
                                d.categoria = cat
                                d.valor = valor
                                d.pagador_id = pagador.id
                                d.data = data.strftime("%Y-%m-%d")
                                d.participantes_ids = [
                                    p.id for p in grupo.participantes
                                    if p.nome in divisao
                                ]
                                st.session_state.editando_despesa = None
                                salvar_dados()
                                alert_sucesso("Despesa atualizada")
                                st.rerun()
                            else:
                                alert_erro("Preencha todos os campos")
                    
                    with bc2:
                        if st.form_submit_button("❌ Cancelar", use_container_width=True):
                            st.session_state.editando_despesa = None
                            st.rerun()

def tela_adicionar_despesa():
    """Tela para adicionar nova despesa"""
    grupo = get_grupo_ativo()
    if not grupo:
        return
    
    if len(grupo.participantes) < 2:
        alert_aviso("Adicione mais participantes")
        if st.button("Ir para Participantes"):
            st.session_state.page = "participantes"
            st.rerun()
        return
    
    page_banner("🧾", "Nova Despesa", grupo.nome, "linear-gradient(135deg,#6366f1,#8b5cf6)")

    with st.form("form_despesa", clear_on_submit=True):
        c1, c2 = st.columns(2)
        
        with c1:
            desc = st.text_input("📝 Descrição", placeholder="Ex: Jantar")
            cat = st.selectbox("🏷️ Categoria", CATEGORIAS)
            valor_txt = st.text_input("💰 Valor", placeholder="Ex: 150,00")
        
        with c2:
            moeda = st.selectbox(
                "💱 Moeda",
                list(MOEDAS.keys()),
                format_func=lambda m: f"{MOEDAS[m]['simbolo']} {MOEDAS[m]['nome']}"
            )
            pagador = st.selectbox(
                "💳 Quem pagou?",
                grupo.participantes,
                format_func=lambda p: p.nome
            )
            data = st.date_input("📅 Data", value=date.today(), format="DD/MM/YYYY")
        
        st.markdown("**➗ Dividir entre:**")
        nomes = [p.nome for p in grupo.participantes]
        selecionados_nomes = st.multiselect(
            "Selecione participantes",
            nomes,
            default=nomes,
            label_visibility="collapsed"
        )
        selecionados = [p.id for p in grupo.participantes if p.nome in selecionados_nomes]
        
        if st.form_submit_button("💾 Salvar", use_container_width=True):
            valor = parse_valor(valor_txt)
            if desc and valor and selecionados:
                data_str = data.strftime("%Y-%m-%d")
                cotacao = obter_cotacao(moeda, data_str)
                valor_brl = round(valor * cotacao, 2)
                
                desc_final = desc
                if moeda != "BRL":
                    desc_final = (
                        f"{desc} ({MOEDAS[moeda]['simbolo']}{valor:.2f} "
                        f"@{cotacao:.4f})"
                    )
                
                nova = Despesa(
                    descricao=desc_final,
                    categoria=cat,
                    valor=valor_brl,
                    pagador_id=pagador.id,
                    participantes_ids=selecionados,
                    data=data_str,
                )
                
                grupo.adicionar_despesa(nova)
                salvar_dados()
                
                if moeda != "BRL":
                    st.toast(
                        f"✅ Convertido: {MOEDAS[moeda]['simbolo']}{valor:.2f} "
                        f"= R${valor_brl:.2f}"
                    )
                
                alert_sucesso(f'"{desc}" adicionada! 🎯')
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                alert_erro("Preencha todos os campos corretamente")

def tela_participantes():
    """Tela de gerenciamento de participantes"""
    grupo = get_grupo_ativo()
    if not grupo:
        return
    
    st.markdown("## 👥 Participantes")
    link_compartilhamento(st.session_state.grupo_ativo_id)
    divider()
    
    st.markdown("### ➕ Adicionar Participante")
    usuarios_fora = [
        uid for uid in st.session_state.usuarios
        if not any(p.id == uid for p in grupo.participantes)
    ]
    
    if usuarios_fora:
        user_sel = st.selectbox(
            "👤 Usuário",
            usuarios_fora,
            format_func=lambda uid: st.session_state.usuarios[uid].get("nome", uid),
        )
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Adicionar", key="btn_add", use_container_width=True):
                udata = st.session_state.usuarios[user_sel]
                novo_p = Participante(
                    nome=udata.get("nome", user_sel),
                    chave_pix=udata.get("pix", ""),
                    tipo_chave_pix=udata.get("tipo_pix", "CPF"),
                    id=user_sel,
                )
                grupo.adicionar_participante(novo_p)
                salvar_dados()
                alert_sucesso(f"{udata.get('nome', user_sel)} adicionado!")
                st.rerun()
        
        with c2:
            if st.button("➕ Nas despesas", key="btn_add_all", use_container_width=True):
                udata = st.session_state.usuarios[user_sel]
                if not any(p.id == user_sel for p in grupo.participantes):
                    novo_p = Participante(
                        nome=udata.get("nome", user_sel),
                        chave_pix=udata.get("pix", ""),
                        tipo_chave_pix=udata.get("tipo_pix", "CPF"),
                        id=user_sel,
                    )
                    grupo.adicionar_participante(novo_p)
                
                for d in grupo.despesas:
                    if user_sel not in d.participantes_ids:
                        d.participantes_ids.append(user_sel)
                
                salvar_dados()
                alert_sucesso(f"Adicionado em {len(grupo.despesas)} despesas!")
                st.rerun()
    else:
        alert_info("Sem usuários", "Todos já estão no grupo!")
    
    divider()
    
    if grupo.participantes:
        st.markdown("### 📋 Lista")
        n_cols = min(3, len(grupo.participantes))
        cols = st.columns(n_cols)
        
        for i, p in enumerate(grupo.participantes):
            with cols[i % n_cols]:
                if card_participante(p, grupo):
                    grupo.remover_participante(p.id)
                    salvar_dados()
                    alert_sucesso("Participante removido")
                    st.rerun()

def tela_fechamento():
    """Tela de fechamento e transferências"""
    grupo = get_grupo_ativo()
    if not grupo:
        return
    
    if not grupo.despesas:
        alert_info("Sem despesas", "Adicione despesas para ver o fechamento")
        return
    
    calc = Calculadora(grupo)
    transferencias = calcular_transferencias(grupo)
    grupo_id = st.session_state.grupo_ativo_id

    if grupo_id not in st.session_state.pagamentos:
        st.session_state.pagamentos[grupo_id] = {}

    # ─── Resumo do acerto (design Tailwind, read-only) ───
    altura = 600 + len(transferencias) * 150
    render_tailwind(Renderizador(grupo).render_fechamento(), height=altura)

    if not transferencias:
        st.success("🎉 Tudo acertado! Nenhuma transferência pendente.")
    else:
        st.markdown("### ✅ Marcar pagamentos")
        for idx, t in enumerate(transferencias):
            if card_pagamento(t, grupo, st.session_state.pagamentos[grupo_id], grupo_id, idx):
                transfer_key = f"{t['de']}->{t['para']}"
                
                if transfer_key in st.session_state.pagamentos[grupo_id]:
                    del st.session_state.pagamentos[grupo_id][transfer_key]
                    alert_sucesso("Marcado como não pago")
                else:
                    st.session_state.pagamentos[grupo_id][transfer_key] = {
                        "marcado_por": st.session_state.usuario_logado,
                        "data": datetime.now().strftime("%Y-%m-%d"),
                    }
                    alert_sucesso("Marcado como pago!")
                
                salvar_dados()
                st.rerun()
    
    divider()
    st.markdown("### 📊 Saldos")
    saldos = calc.saldos()
    pagamentos_grp = st.session_state.pagamentos.get(grupo_id, {})
    
    for p in grupo.participantes:
        s = saldos.get(p.id, 0)
        transfers_p = [t for t in transferencias if t["de"] == p.id or t["para"] == p.id]
        all_p_paid = all(
            f"{t['de']}->{t['para']}" in pagamentos_grp
            for t in transfers_p
        ) if transfers_p else False
        
        if all_p_paid and abs(s) > 0.01:
            st.markdown(f"~~⚪ {p.nome} — quitado~~ ✅")
        elif s > 0.01:
            st.markdown(f"🟢 **{p.nome}** recebe {formatar_valor(s)}")
        elif s < -0.01:
            st.markdown(f"🔴 **{p.nome}** deve {formatar_valor(abs(s))}")
        else:
            st.markdown(f"⚪ **{p.nome}** zerado")

def tela_perfil(target=None):
    """Tela de perfil do usuário"""
    user = target or st.session_state.usuario_logado
    if user != st.session_state.usuario_logado and not is_admin():
        alert_erro("Sem permissão")
        return
    
    uinfo = st.session_state.usuarios.get(user, {})
    titulo = "Meu Perfil" if user == st.session_state.usuario_logado else f"Editando: {uinfo.get('nome', user)}"
    st.markdown(f"## 👤 {titulo}")
    
    foto = uinfo.get("foto")
    if foto:
        st.markdown(
            f'<img src="data:image/png;base64,{foto}" '
            f'style="width:80px;height:80px;border-radius:50%;object-fit:cover">',
            unsafe_allow_html=True
        )
    
    with st.form(f"form_perfil_{user}"):
        nome_d = st.text_input("Nome", value=uinfo.get("nome", ""))
        tipo_pix = st.selectbox(
            "Tipo PIX",
            ["CPF", "E-mail", "Telefone", "Aleatória"],
            index=["CPF", "E-mail", "Telefone", "Aleatória"].index(
                uinfo.get("tipo_pix", "CPF")
            )
        )
        pix = st.text_input("Chave PIX", value=uinfo.get("pix", ""))
        nova_foto = st.file_uploader("Nova foto", type=["png", "jpg", "jpeg"])
        nova_senha = st.text_input("Nova senha (vazio = manter)", type="password")
        
        if st.form_submit_button("💾 Salvar", use_container_width=True):
            st.session_state.usuarios[user]["nome"] = nome_d
            st.session_state.usuarios[user]["tipo_pix"] = tipo_pix
            st.session_state.usuarios[user]["pix"] = pix
            
            if nova_foto:
                st.session_state.usuarios[user]["foto"] = base64.b64encode(nova_foto.read()).decode()
            
            if nova_senha:
                hash_senha, salt = AuthService.hash_senha(nova_senha)
                st.session_state.usuarios[user]["senha_hash"] = hash_senha
                st.session_state.usuarios[user]["senha_salt"] = salt
            
            for g in st.session_state.grupos.values():
                for part in g.participantes:
                    if part.id == user:
                        part.nome = nome_d
                        part.chave_pix = pix
                        part.tipo_chave_pix = tipo_pix
            
            salvar_dados()
            alert_sucesso("Perfil atualizado!")
            st.rerun()

def tela_admin():
    """Tela de administração"""
    if not is_admin():
        alert_erro("Acesso restrito")
        return
    
    st.markdown("## 🔑 Administração")
    st.markdown("### 👥 Gerenciar Usuários")
    
    for uid, data in st.session_state.usuarios.items():
        with st.expander(f"{'🔑' if data.get('admin') else '👤'} {data.get('nome', uid)} (@{uid})"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Editar", key=f"adm_edit_{uid}", use_container_width=True):
                    st.session_state.page = f"perfil_admin_{uid}"
                    st.rerun()
            with col2:
                if uid != ADMIN_USER:
                    if st.button(
                        "🗑️ Deletar",
                        key=f"adm_del_{uid}",
                        use_container_width=True
                    ):
                        del st.session_state.usuarios[uid]
                        salvar_dados()
                        alert_sucesso(f"{uid} deletado")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# ─── MAIN ───
# ═══════════════════════════════════════════════════════════════════

# Verifica URL para grupo
g = st.query_params.get("grupo")
if g and g in st.session_state.grupos:
    st.session_state.grupo_ativo_id = g

# ─── Redireciona para login se necessário ───
if not st.session_state.usuario_logado:
    tela_login()
    st.stop()

render_sidebar()

grupo = get_grupo_ativo()
page = st.session_state.page

# Roteamento de páginas (com rede de segurança contra erros inesperados).
# st.rerun()/st.stop() usam BaseException, então não são capturados aqui.
try:
    # Invitação para grupo
    if page == "convite":
        convite_gid = st.query_params.get("grupo")
        if convite_gid and convite_gid in st.session_state.grupos:
            grupo_convite = st.session_state.grupos[convite_gid]
            user = st.session_state.usuario_logado
            if not any(p.id == user for p in grupo_convite.participantes):
                st.markdown(f"## 🎉 Convite para {grupo_convite.nome}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Entrar", use_container_width=True):
                        uinfo = user_info()
                        grupo_convite.adicionar_participante(Participante(
                            nome=uinfo.get("nome", user),
                            chave_pix=uinfo.get("pix", ""),
                            tipo_chave_pix=uinfo.get("tipo_pix", "CPF"),
                            id=user,
                        ))
                        st.session_state.grupo_ativo_id = convite_gid
                        st.session_state.page = "dashboard"
                        salvar_dados()
                        alert_sucesso(f"Bem-vindo a {grupo_convite.nome}!")
                        st.rerun()
                with c2:
                    if st.button("❌ Voltar", use_container_width=True):
                        st.query_params.clear()
                        st.rerun()
            else:
                st.session_state.grupo_ativo_id = convite_gid
                st.session_state.page = "dashboard"
                st.rerun()

    elif page == "criar_grupo":
        tela_criar_grupo()

    elif page == "perfil":
        tela_perfil()

    elif page == "admin":
        tela_admin()

    elif page.startswith("perfil_admin_"):
        tela_perfil(target=page.replace("perfil_admin_", ""))

    elif grupo is None:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            logo = load_image_b64("logo.png")
            if logo:
                st.markdown(
                    f'<div style="text-align:center">'
                    f'<img src="data:image/png;base64,{logo}" style="max-width:200px">'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown("# 💸 Bem-vindo!")
            st.markdown("Crie um novo grupo ou entre por um link de convite.")
            if st.button("➕ Novo Grupo", key="criar_inicio", use_container_width=True):
                st.session_state.page = "criar_grupo"
                st.rerun()

    elif page == "dashboard":
        tela_dashboard()

    elif page == "adicionar":
        tela_adicionar_despesa()

    elif page == "participantes":
        tela_participantes()

    elif page == "fechamento":
        tela_fechamento()

except Exception as _err:
    logger.exception("Erro inesperado ao renderizar a página")
    st.error("⚠️ Ops! Algo deu errado ao carregar esta tela. Seus dados estão salvos.")
    col_retry, col_home = st.columns(2)
    with col_retry:
        if st.button("🔄 Tentar de novo", use_container_width=True):
            st.rerun()
    with col_home:
        if st.button("🏠 Voltar ao início", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    with st.expander("Detalhes técnicos (para suporte)"):
        st.exception(_err)

# DEBUG: Monitor de cache e performance (opcional)
if st.session_state.get("debug"):
    with st.expander("🔧 Debug", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Usuários", len(st.session_state.usuarios))
            st.metric("Grupos", len(st.session_state.grupos))
        with col2:
            st.metric("Despesas", sum(len(g.despesas) for g in st.session_state.grupos.values()))
            st.metric("Pagamentos", sum(len(p) for p in st.session_state.pagamentos.values()))
