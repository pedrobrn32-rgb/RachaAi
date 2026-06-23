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

# Configuration for GCS Bucket
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "rachaai-data-bucket")

def _get_bucket():
    return storage.Client().bucket(GCS_BUCKET_NAME)

def salvar_usuarios(usuarios: dict):
    users_data = {}
    for uid, uinfo in usuarios.items():
        entry = {k: v for k, v in uinfo.items() if k != "foto"}
        users_data[uid] = entry
    photos_data = {uid: uinfo.get("foto") for uid, uinfo in usuarios.items() if uinfo.get("foto")}
    bucket = _get_bucket()
    bucket.blob("usuarios.json").upload_from_string(json.dumps(users_data, ensure_ascii=False, indent=2), content_type="application/json")
    bucket.blob("fotos.json").upload_from_string(json.dumps(photos_data, ensure_ascii=False), content_type="application/json")


def carregar_usuarios() -> dict:
    bucket = _get_bucket()
    blob = bucket.blob("usuarios.json")
    if not blob.exists():
        return {}
    try:
        users_data = json.loads(blob.download_as_string())
        blob_photos = bucket.blob("fotos.json")
        photos_data = json.loads(blob_photos.download_as_string()) if blob_photos.exists() else {}
        for uid in users_data:
            users_data[uid]["foto"] = photos_data.get(uid)
        return users_data
    except (json.JSONDecodeError, Exception):
        return {}


def salvar_grupos(grupos: dict):
    groups_data = {}
    for slug, grupo in grupos.items():
        groups_data[slug] = grupo.to_dict()
    groups_data["_salvo_em"] = datetime.now().isoformat()
    _get_bucket().blob("grupos.json").upload_from_string(json.dumps(groups_data, ensure_ascii=False, indent=2), content_type="application/json")


def carregar_grupos() -> dict:
    bucket = _get_bucket()
    blob = bucket.blob("grupos.json")
    if not blob.exists():
        return {}
    try:
        groups_data = json.loads(blob.download_as_string())
        groups_data.pop("_salvo_em", None)
        return {slug: Grupo.from_dict(gdict) for slug, gdict in groups_data.items()}
    except (json.JSONDecodeError, Exception):
        return {}


def salvar_pagamentos(pagamentos: dict):
    _get_bucket().blob("pagamentos.json").upload_from_string(json.dumps(pagamentos, ensure_ascii=False, indent=2), content_type="application/json")


def carregar_pagamentos() -> dict:
    bucket = _get_bucket()
    blob = bucket.blob("pagamentos.json")
    if not blob.exists():
        return {}
    try:
        return json.loads(blob.download_as_string())
    except (json.JSONDecodeError, Exception):
        return {}


# ─── Config (roda 1x) ───
st.set_page_config(
    page_title="Racha Ai!",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS — FORÇA LIGHT MODE + FIX NUCLEAR BOTOES + SIDEBAR
st.markdown("""<style>
:root{color-scheme:light only !important;
    --primary-color:#006c49 !important;
    --background-color:#f8f9ff !important;
    --text-color:#1f2937 !important}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],.main,.block-container,header,
[data-testid="stHeader"],[data-testid="stToolbar"]{
    background-color:#f8f9ff !important;color:#1f2937 !important;color-scheme:light !important}
.main .block-container{padding-top:1rem;max-width:100%}
iframe{border:none}
p,span,h1,h2,h3,h4,h5,h6,li,td,th,label,caption,
.stMarkdown,.stCaption,.stMetricValue,.stMetricLabel,
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,
[data-baseweb="tab"]{color:#1f2937 !important}
input,textarea,[data-baseweb="input"] input,[data-baseweb="select"] span,
[data-baseweb="select"] div,[data-baseweb="select"] p,
.stSelectbox div[data-baseweb="select"] > div > div,
.stSelectbox div[data-baseweb="select"] > div > div > div,
.stSelectbox [class*="singleValue"],[class*="placeholder"]{color:#1f2937 !important}
[data-baseweb="input"],[data-baseweb="select"],
.stTextInput>div>div,.stSelectbox>div>div,.stMultiSelect>div>div{background:#ffffff !important;border-color:#d1d5db !important}
[data-baseweb="popover"],[data-baseweb="menu"],[data-baseweb="select"] ul,
[role="listbox"]{background:#ffffff !important}
[data-baseweb="menu"] li,[role="option"]{color:#1f2937 !important;background:#ffffff !important}
[data-baseweb="menu"] li:hover,[role="option"]:hover{background:#f3f4f6 !important}
[data-baseweb="tag"]{background:#e8f5e9 !important;color:#1f2937 !important}
[data-baseweb="tag"] span{color:#1f2937 !important}
.stTabs [data-baseweb="tab"]{opacity:0.7}
.stTabs [aria-selected="true"]{opacity:1 !important}
/* ═══ BOTOES MAIN — NUCLEAR FIX ═══ */
html body [data-testid="stApp"] .main button,
html body [data-testid="stApp"] [data-testid="stMainBlockContainer"] button{
    background-color:#ffffff !important;color:#1f2937 !important;
    border:1px solid #d1d5db !important;border-radius:9999px;font-weight:600}
html body [data-testid="stApp"] .main button *,
html body [data-testid="stApp"] [data-testid="stMainBlockContainer"] button *{
    color:inherit !important;background-color:transparent !important}
html body [data-testid="stApp"] .main button:hover{
    background-color:#f0fdf4 !important;border-color:#006c49 !important;color:#006c49 !important}
/* Submit/primary — verde + texto BRANCO */
html body [data-testid="stApp"] .main .stFormSubmitButton button,
html body [data-testid="stApp"] .main [data-testid="baseButton-primary"],
html body [data-testid="stApp"] .main [data-testid="baseButton-primaryFormSubmit"]{
    background-color:#006c49 !important;color:#ffffff !important;border:none !important;border-radius:9999px}
html body [data-testid="stApp"] .main .stFormSubmitButton button *{
    color:#ffffff !important}
html body [data-testid="stApp"] .main .stFormSubmitButton button:hover{background-color:#004d2e !important}
/* ═══ SIDEBAR ═══ */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#006c49 0%,#004d2e 100%) !important;min-width:230px !important;max-width:230px !important}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]{padding:0.5rem 0.75rem !important}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:0.5rem !important}
[data-testid="stSidebar"] hr{margin:0.6rem 0 !important;border-color:rgba(255,255,255,0.2) !important}
[data-testid="stSidebar"] h4{margin:0.2rem 0 0.3rem 0 !important;font-size:1.05rem !important}
[data-testid="stSidebar"] h5{margin:0.3rem 0 !important;font-size:0.9rem !important}
[data-testid="stSidebar"] .stMarkdown p{margin-bottom:0.15rem !important;font-size:0.85rem !important}
[data-testid="stSidebar"] .stCaption{font-size:0.73rem !important}
[data-testid="stSidebar"],[data-testid="stSidebar"] *{color:#fff !important}
[data-testid="stSidebar"] button{
    background:rgba(255,255,255,0.15) !important;border:1px solid rgba(255,255,255,0.3) !important;
    color:#ffffff !important;border-radius:12px;font-weight:600;width:100%;margin-bottom:5px;padding:8px 14px;font-size:13px}
[data-testid="stSidebar"] button *{color:#ffffff !important;background-color:transparent !important}
[data-testid="stSidebar"] button:hover{background:rgba(255,255,255,0.25) !important}
/* Toggle sidebar */
[data-testid="collapsedControl"]{display:flex !important;align-items:center}
[data-testid="collapsedControl"] button{background:#006c49 !important;color:#fff !important;border-radius:8px !important;padding:6px 12px !important}
/* Sidebar columns — sempre mesma linha */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:2px !important}
/* Botao lixeira — icone puro (sibling selector) */
[data-testid="stSidebar"] [data-testid="column"] + [data-testid="column"] button{
    background:transparent !important;border:none !important;padding:2px 4px !important;
    margin:0 !important;min-height:auto !important;width:auto !important;
    font-size:14px !important;line-height:1 !important}
[data-testid="stSidebar"] [data-testid="column"] + [data-testid="column"] button:hover{
    background:rgba(255,255,255,0.2) !important;border-radius:8px}
</style>""", unsafe_allow_html=True)

# ─── Constantes ───
ADMIN_USER = "pedro"
BASE_URL = "https://rachaai.streamlit.app/"

MOEDAS = {
    "BRL": {"simbolo": "R$", "nome": "Real"},
    "USD": {"simbolo": "US$", "nome": "Dolar"},
    "EUR": {"simbolo": "€", "nome": "Euro"},
    "ARS": {"simbolo": "AR$", "nome": "Peso Argentino"},
    "CLP": {"simbolo": "CL$", "nome": "Peso Chileno"},
    "COP": {"simbolo": "CO$", "nome": "Peso Colombiano"},
    "PYG": {"simbolo": "₲", "nome": "Guarani"},
    "UYU": {"simbolo": "U$", "nome": "Peso Uruguaio"},
    "PEN": {"simbolo": "S/", "nome": "Sol Peruano"},
    "BOB": {"simbolo": "Bs", "nome": "Boliviano"},
}


# ─── Helpers com cache ───
@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def obter_cotacao(moeda: str, data_str: str) -> float:
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
    except Exception:
        pass
    return 1.0


def formatar_valor(valor, moeda="BRL"):
    s = MOEDAS.get(moeda, {}).get("simbolo", "R$")
    if valor < 0:
        return f"- {s} {abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return data_str


def link_grupo(grupo_id):
    return f"{BASE_URL}?grupo={grupo_id}"


def parse_valor(texto):
    txt = texto.strip().replace(" ", "")
    if not txt:
        return None
    if "," in txt and "." in txt:
        if txt.rfind(",") > txt.rfind("."):
            txt = txt.replace(".", "").replace(",", ".")
        else:
            txt = txt.replace(",", "")
    elif "," in txt:
        txt = txt.replace(",", ".")
    try:
        v = float(txt)
        return v if v > 0 else None
    except ValueError:
        return None


def calcular_transferencias(grupo):
    """Calcula lista minima de transferencias para zerar saldos."""
    calc = Calculadora(grupo)
    saldos = calc.saldos()
    devedores = []
    credores = []
    for pid, saldo in saldos.items():
        if saldo < -0.01:
            devedores.append([pid, -saldo])
        elif saldo > 0.01:
            credores.append([pid, saldo])
    devedores.sort(key=lambda x: x[1], reverse=True)
    credores.sort(key=lambda x: x[1], reverse=True)
    transferencias = []
    i, j = 0, 0
    while i < len(devedores) and j < len(credores):
        devedor_id, deve = devedores[i]
        credor_id, recebe = credores[j]
        valor = min(deve, recebe)
        if valor > 0.01:
            transferencias.append({
                "de": devedor_id,
                "para": credor_id,
                "valor": round(valor, 2),
            })
        devedores[i][1] -= valor
        credores[j][1] -= valor
        if devedores[i][1] < 0.01:
            i += 1
        if credores[j][1] < 0.01:
            j += 1
    return transferencias


# ─── Persistencia: auto-save helper ───
def persist():
    salvar_usuarios(st.session_state.usuarios)
    salvar_grupos(st.session_state.grupos)
    salvar_pagamentos(st.session_state.pagamentos)


# ─── Session State (init 1x — carrega do GCS se existir) ───
if "usuarios" not in st.session_state:
    loaded_users = carregar_usuarios()
    if loaded_users:
        st.session_state.usuarios = loaded_users
    else:
        st.session_state.usuarios = {
            ADMIN_USER: {
                "senha": "pedro",
                "nome": "Pedro",
                "pix": "",
                "tipo_pix": "CPF",
                "foto": None,
                "admin": True,
            }
        }
if "grupos" not in st.session_state:
    loaded_groups = carregar_grupos()
    st.session_state.grupos = loaded_groups if loaded_groups else {}
if "pagamentos" not in st.session_state:
    loaded_pag = carregar_pagamentos()
    st.session_state.pagamentos = loaded_pag if loaded_pag else {}
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "grupo_ativo_id" not in st.session_state:
    st.session_state.grupo_ativo_id = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "editando_despesa" not in st.session_state:
    st.session_state.editando_despesa = None

fmt = Formatador()


def user_info(username=None):
    u = username or st.session_state.usuario_logado
    return st.session_state.usuarios.get(u, {})


def is_admin():
    return st.session_state.usuario_logado == ADMIN_USER


# ─── Login ───
def tela_login():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        inicio = load_image_b64("inicio.png")
        if inicio:
            st.markdown(f'<div style="text-align:center;margin:16px 0"><img src="data:image/png;base64,{inicio}" style="max-width:320px;border-radius:16px"></div>', unsafe_allow_html=True)
        else:
            st.markdown("## 💸 Racha Ai!")

        st.markdown("Entre ou crie sua conta.")
        tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])

        with tab1:
            with st.form("login_form"):
                user = st.text_input("Usuario", placeholder="seu nome").strip().lower()
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    if user and senha:
                        if user in st.session_state.usuarios:
                            if st.session_state.usuarios[user]["senha"] == senha:
                                st.session_state.usuario_logado = user
                                st.rerun()
                            else:
                                st.error("Senha incorreta.")
                        else:
                            st.error("Usuario nao encontrado.")
                    else:
                        st.error("Preencha tudo.")

        with tab2:
            with st.form("registro_form"):
                novo_user = st.text_input("Nome de usuario (login)", placeholder="ex: pedro").strip().lower()
                nome_display = st.text_input("Nome completo", placeholder="Ex: Pedro Silva")
                nova_senha = st.text_input("Senha", type="password", placeholder="ex: pedro")
                tipo_pix = st.selectbox("Tipo Chave PIX", ["CPF", "E-mail", "Telefone", "Aleatoria"])
                chave_pix = st.text_input("Chave PIX", placeholder="123.456.789-00")
                foto = st.file_uploader("Foto de perfil", type=["png", "jpg", "jpeg"])
                st.caption("Padrao: usuario = seu nome, senha = seu nome")
                if st.form_submit_button("Criar Conta", use_container_width=True):
                    if novo_user and nova_senha and nome_display:
                        if novo_user in st.session_state.usuarios:
                            st.error("Usuario ja existe.")
                        else:
                            foto_b64 = None
                            if foto:
                                foto_b64 = base64.b64encode(foto.read()).decode()
                            st.session_state.usuarios[novo_user] = {
                                "senha": nova_senha,
                                "nome": nome_display,
                                "pix": chave_pix,
                                "tipo_pix": tipo_pix,
                                "foto": foto_b64,
                                "admin": False,
                            }
                            persist()
                            st.session_state.usuario_logado = novo_user
                            st.toast(f"Bem-vindo, {nome_display}!")
                            st.rerun()
                    else:
                        st.error("Preencha todos os campos.")


# ─── URL / Grupo ───
def check_url_grupo():
    g = st.query_params.get("grupo")
    if g and g in st.session_state.grupos:
        st.session_state.grupo_ativo_id = g
        return g
    return None


def get_grupo_ativo():
    gid = st.session_state.grupo_ativo_id
    if gid and gid in st.session_state.grupos:
        return st.session_state.grupos[gid]
    return None


# ─── Sidebar ───
def render_sidebar():
    user = st.session_state.usuario_logado
    uinfo = user_info()
    grupo = get_grupo_ativo()

    with st.sidebar:
        logo = load_image_b64("logo.png")
        if logo:
            st.markdown(f'<div style="text-align:center;margin-bottom:0"><img src="data:image/png;base64,{logo}" style="max-width:55px"></div>', unsafe_allow_html=True)
        st.markdown('<h4 style="text-align:center;margin:0 0 8px 0">💸 Racha Ai!</h4>', unsafe_allow_html=True)

        foto = uinfo.get("foto")
        nome = uinfo.get("nome", user)
        if foto:
            st.markdown(f'<img src="data:image/png;base64,{foto}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.5);vertical-align:middle"> <b>{nome}</b>', unsafe_allow_html=True)
        else:
            st.markdown(f'👤 <b>{nome}</b>', unsafe_allow_html=True)
        if is_admin():
            st.caption("🔑 Admin")
        st.markdown("---")

        if grupo:
            st.markdown(f"##### 📌 {grupo.nome}")
            st.caption(f"{grupo.tipo_evento} • {len(grupo.participantes)} pessoas")
            st.markdown("---")

            for key, label in {"dashboard": "📊 Despesas", "adicionar": "➕ Nova Despesa", "participantes": "👥 Participantes", "fechamento": "💰 Fechamento"}.items():
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.session_state._collapse_sidebar = True
                    st.rerun()

        st.markdown("---")
        if st.button("👤 Meu Perfil", key="nav_perfil", use_container_width=True):
            st.session_state.page = "perfil"
            st.session_state._collapse_sidebar = True
            st.rerun()

        if is_admin():
            if st.button("🔑 Admin", key="nav_admin", use_container_width=True):
                st.session_state.page = "admin"
                st.session_state._collapse_sidebar = True
                st.rerun()

        st.markdown("---")
        st.markdown('<p style="margin:12px 0 10px 0;font-weight:700;font-size:0.85rem">📁 Grupos:</p>', unsafe_allow_html=True)

        meus_grupos = {gid: g for gid, g in st.session_state.grupos.items() if any(p.id == user for p in g.participantes)}

        if meus_grupos:
            for gid, g in meus_grupos.items():
                is_ativo = (gid == st.session_state.grupo_ativo_id)
                # Verifica se grupo ta quitado
                transferencias_grp = calcular_transferencias(g)
                pagamentos_grp = st.session_state.pagamentos.get(gid, {})
                all_paid = len(transferencias_grp) > 0 and all(
                    f"{t['de']}->{t['para']}" in pagamentos_grp for t in transferencias_grp
                )
                icon = "✅" if all_paid else ("📌" if is_ativo else "📂")
                # So criador ou admin pode deletar
                pode_deletar = (g.criado_por == user) or is_admin()
                if pode_deletar:
                    c1, c2 = st.columns([6, 1], gap="small")
                    with c1:
                        if st.button(f"{icon} {g.nome}", key=f"grp_{gid}", use_container_width=True):
                            st.session_state.grupo_ativo_id = gid
                            st.session_state.page = "dashboard"
                            st.session_state._collapse_sidebar = True
                            st.query_params["grupo"] = gid
                            st.rerun()
                    with c2:
                        if st.button("🗑️", key=f"delgrp_{gid}"):
                            del st.session_state.grupos[gid]
                            if st.session_state.grupo_ativo_id == gid:
                                st.session_state.grupo_ativo_id = None
                            persist()
                            st.toast("✅ Grupo deletado!")
                            st.rerun()
                else:
                    if st.button(f"{icon} {g.nome}", key=f"grp_{gid}", use_container_width=True):
                        st.session_state.grupo_ativo_id = gid
                        st.session_state.page = "dashboard"
                        st.session_state._collapse_sidebar = True
                        st.query_params["grupo"] = gid
                        st.rerun()
                st.markdown('<div style="margin-bottom:8px"></div>', unsafe_allow_html=True)
        else:
            st.caption("Nenhum grupo ainda.")

        if st.button("➕ Novo Grupo", key="criar_grupo_btn", use_container_width=True):
            st.session_state.page = "criar_grupo"
            st.session_state._collapse_sidebar = True
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Sair", key="logout_btn", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()


# ─── Criar Grupo ───
def tela_criar_grupo():
    st.markdown("## ➕ Criar Novo Grupo")
    with st.form("form_novo_grupo"):
        nome = st.text_input("Nome do grupo", placeholder="Ex: Viagem Rio 2026")
        desc = st.text_input("Descricao", placeholder="Ex: Gastos da viagem")
        tipo = st.selectbox("Tipo de evento", TIPOS_EVENTO)
        if st.form_submit_button("Criar Grupo", use_container_width=True):
            if nome:
                slug = "".join(c for c in nome.lower().replace(" ", "-") if c.isalnum() or c == "-")[:30]
                if slug in st.session_state.grupos:
                    slug += f"-{len(st.session_state.grupos)}"
                user = st.session_state.usuario_logado
                novo = Grupo(nome=nome, descricao=desc, tipo_evento=tipo, id=slug, criado_por=user)
                uinfo = user_info()
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
                persist()
                st.session_state._msg_sucesso = f'✅ Grupo "{nome}" criado com sucesso!'
                st.rerun()
            else:
                st.error("Informe o nome.")

    if st.session_state.grupo_ativo_id:
        st.markdown("---")
        st.markdown("**🔗 Link para compartilhar:**")
        st.code(link_grupo(st.session_state.grupo_ativo_id), language=None)


# ─── Convite ───
def tela_convite(grupo_id):
    grupo = st.session_state.grupos.get(grupo_id)
    user = st.session_state.usuario_logado
    if not grupo:
        st.error("Grupo nao encontrado.")
        return
    if any(p.id == user for p in grupo.participantes):
        st.session_state.grupo_ativo_id = grupo_id
        st.session_state.page = "dashboard"
        st.rerun()
        return

    st.markdown(f"## 🎉 Voce foi convidado!")
    st.markdown(f"### {grupo.nome}")
    st.caption(f"{grupo.tipo_evento} • {len(grupo.participantes)} participantes")
    st.markdown(f"**Participantes:** {', '.join(p.nome for p in grupo.participantes)}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Entrar no Grupo", use_container_width=True):
            uinfo = user_info()
            grupo.adicionar_participante(Participante(
                nome=uinfo.get("nome", user),
                chave_pix=uinfo.get("pix", ""),
                tipo_chave_pix=uinfo.get("tipo_pix", "CPF"),
                id=user,
            ))
            st.session_state.grupo_ativo_id = grupo_id
            st.session_state.page = "dashboard"
            persist()
            st.toast(f"Entrou no grupo {grupo.nome}!")
            st.rerun()
    with c2:
        if st.button("❌ Voltar", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()


# ─── Perfil ───
def tela_perfil(target=None):
    user = target or st.session_state.usuario_logado
    if user != st.session_state.usuario_logado and not is_admin():
        st.error("Sem permissao.")
        return

    uinfo = st.session_state.usuarios.get(user, {})
    titulo = "Meu Perfil" if user == st.session_state.usuario_logado else f"Editando: {uinfo.get('nome', user)}"
    st.markdown(f"## 👤 {titulo}")

    foto = uinfo.get("foto")
    if foto:
        st.markdown(f'<img src="data:image/png;base64,{foto}" style="width:80px;height:80px;border-radius:50%;object-fit:cover">', unsafe_allow_html=True)

    with st.form(f"form_perfil_{user}"):
        nome_d = st.text_input("Nome", value=uinfo.get("nome", ""))
        tipo_pix = st.selectbox("Tipo PIX", ["CPF", "E-mail", "Telefone", "Aleatoria"],
                                index=["CPF", "E-mail", "Telefone", "Aleatoria"].index(uinfo.get("tipo_pix", "CPF")))
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
                st.session_state.usuarios[user]["senha"] = nova_senha
            for g in st.session_state.grupos.values():
                for p in g.participantes:
                    if p.id == user:
                        p.nome = nome_d
                        p.chave_pix = pix
                        p.tipo_chave_pix = tipo_pix
            persist()
            st.session_state._msg_sucesso = "✅ Perfil salvo com sucesso!"
            st.rerun()


# ─── Admin ───
def tela_admin():
    if not is_admin():
        st.error("Acesso restrito.")
        return
    st.markdown("## 🔑 Gerenciar Usuarios")
    for uid, data in st.session_state.usuarios.items():
        with st.expander(f"{'🔑' if data.get('admin') else '👤'} {data.get('nome', uid)} (@{uid})"):
            if st.button(f"Editar {uid}", key=f"adm_edit_{uid}"):
                st.session_state.page = f"perfil_admin_{uid}"
                st.rerun()


def render_html(html, height=900):
    components.html(html, height=height, scrolling=True)


# ═══════════════════════════════
# MAIN
# ═══════════════════════════════

if not st.session_state.usuario_logado:
    tela_login()
    st.stop()

url_grupo = check_url_grupo()
if url_grupo:
    grupo = st.session_state.grupos.get(url_grupo)
    if grupo and not any(p.id == st.session_state.usuario_logado for p in grupo.participantes):
        render_sidebar()
        tela_convite(url_grupo)
        st.stop()

render_sidebar()

# Sidebar: initial_sidebar_state="collapsed" garante que ao rerun() ela fecha

grupo = get_grupo_ativo()
page = st.session_state.page

# Mensagem de sucesso global
if st.session_state.get("_msg_sucesso"):
    st.success(st.session_state._msg_sucesso)
    st.session_state._msg_sucesso = None

if page == "criar_grupo":
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
            st.markdown(f'<div style="text-align:center"><img src="data:image/png;base64,{logo}" style="max-width:200px"></div>', unsafe_allow_html=True)
        st.markdown("## 💸 Bem-vindo ao Racha Ai!")
        st.markdown("Crie um grupo ou entre pelo link de convite.")
        inicio = load_image_b64("inicio.png")
        if inicio:
            st.markdown(f'<div style="text-align:center;margin:16px 0"><img src="data:image/png;base64,{inicio}" style="max-width:350px;border-radius:16px"></div>', unsafe_allow_html=True)
        if st.button("➕ Criar Novo Grupo", key="criar_inicio", use_container_width=True):
            st.session_state.page = "criar_grupo"
            st.rerun()

elif page == "dashboard":
    st.markdown(f"## 📊 Despesas — {grupo.nome}")
    if not grupo.despesas:
        st.info("Nenhuma despesa cadastrada.")
        st.markdown("**🔗 Link do grupo:**")
        st.code(link_grupo(st.session_state.grupo_ativo_id), language=None)
    else:
        calc = Calculadora(grupo)
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total", formatar_valor(calc.total_gasto()))
        with k2:
            st.metric("Despesas", len(grupo.despesas))
        with k3:
            st.metric("Pessoas", len(grupo.participantes))

        st.markdown('<div style="margin-top:2px"></div>', unsafe_allow_html=True)

        for d in sorted(grupo.despesas, key=lambda x: x.data, reverse=True):
            pag = grupo.get_participante(d.pagador_id)
            nomes_divisao = [grupo.get_participante(pid).nome for pid in d.participantes_ids if grupo.get_participante(pid)]
            valor_pp = d.valor / len(d.participantes_ids) if d.participantes_ids else 0

            with st.container():
                card_col, btn_e, btn_d = st.columns([10, 1, 1], gap="small")
                with card_col:
                    st.markdown(f"""<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:10px 14px;display:flex;align-items:center;justify-content:space-between">
                        <div style="flex:1">
                            <span style="font-weight:700;color:#1f2937">{d.descricao}</span>
                            <span style="color:#6b7280;font-size:0.85em"> • {d.categoria} • {formatar_data(d.data)}</span>
                            <br><span style="color:#6b7280;font-size:0.8em">💳 {pag.nome if pag else '-'} → {', '.join(nomes_divisao)} ({formatar_valor(valor_pp)}/pp)</span>
                        </div>
                        <div style="font-weight:700;font-size:1.1em;color:#006c49;margin:0 8px">{formatar_valor(d.valor)}</div>
                    </div>""", unsafe_allow_html=True)
                with btn_e:
                    if st.button("✏️", key=f"edit_{d.id}"):
                        st.session_state.editando_despesa = d.id
                        st.rerun()
                with btn_d:
                    if st.button("🗑️", key=f"del_dash_{d.id}"):
                        grupo.remover_despesa(d.id)
                        persist()
                        st.session_state._msg_sucesso = "✅ Despesa removida!"
                        st.rerun()

                if st.session_state.editando_despesa == d.id:
                    st.markdown("---")
                    with st.form(f"form_edit_{d.id}"):
                        st.markdown("**✏️ Editando despesa:**")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            new_desc = st.text_input("Descricao", value=d.descricao, key=f"ed_desc_{d.id}")
                            new_cat = st.selectbox("Categoria", CATEGORIAS,
                                                   index=CATEGORIAS.index(d.categoria) if d.categoria in CATEGORIAS else 0,
                                                   key=f"ed_cat_{d.id}")
                            new_valor_txt = st.text_input("Valor", value=str(d.valor).replace(".", ","), key=f"ed_val_{d.id}")
                        with ec2:
                            pagadores = grupo.participantes
                            pag_idx = next((i for i, p in enumerate(pagadores) if p.id == d.pagador_id), 0)
                            new_pagador = st.selectbox("Quem pagou?", pagadores,
                                                       index=pag_idx,
                                                       format_func=lambda p: p.nome,
                                                       key=f"ed_pag_{d.id}")
                            new_data = st.date_input("Data",
                                                     value=datetime.strptime(d.data, "%Y-%m-%d").date(),
                                                     format="DD/MM/YYYY",
                                                     key=f"ed_data_{d.id}")

                        nomes_todos = [p.nome for p in grupo.participantes]
                        nomes_atuais = [grupo.get_participante(pid).nome for pid in d.participantes_ids if grupo.get_participante(pid)]
                        new_divisao = st.multiselect("Dividir entre", nomes_todos, default=nomes_atuais, key=f"ed_div_{d.id}")

                        bc1, bc2 = st.columns(2)
                        with bc1:
                            salvar = st.form_submit_button("💾 Salvar alteracoes", use_container_width=True)
                        with bc2:
                            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

                        if salvar:
                            new_valor = parse_valor(new_valor_txt)
                            if new_desc and new_valor and new_divisao:
                                d.descricao = new_desc
                                d.categoria = new_cat
                                d.valor = new_valor
                                d.pagador_id = new_pagador.id
                                d.data = new_data.strftime("%Y-%m-%d")
                                d.participantes_ids = [p.id for p in grupo.participantes if p.nome in new_divisao]
                                st.session_state.editando_despesa = None
                                persist()
                                st.session_state._msg_sucesso = "✅ Despesa atualizada com sucesso!"
                                st.rerun()
                            else:
                                st.error("Preencha todos os campos com valores validos.")
                        if cancelar:
                            st.session_state.editando_despesa = None
                            st.rerun()

                pass  # cards already have visual separation

elif page == "adicionar":
    if len(grupo.participantes) < 2:
        st.warning("Adicione pelo menos 2 participantes.")
        if st.button("Ir para Participantes"):
            st.session_state.page = "participantes"
            st.rerun()
    else:
        st.markdown("## ➕ Nova Despesa")
        with st.form("form_despesa", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                descricao = st.text_input("Descricao", placeholder="Ex: Jantar")
                categoria = st.selectbox("Categoria", CATEGORIAS)
                valor_txt = st.text_input("Valor", placeholder="Ex: 150,00 ou 1.250,50")
            with c2:
                moeda_pag = st.selectbox("Moeda paga", list(MOEDAS.keys()),
                                         format_func=lambda m: f"{MOEDAS[m]['simbolo']} {MOEDAS[m]['nome']}")
                pagador = st.selectbox("Quem pagou?", grupo.participantes, format_func=lambda p: p.nome)
                data_desp = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")

            st.markdown("**Dividir entre:**")
            nomes_participantes = [p.nome for p in grupo.participantes]
            selecionados_nomes = st.multiselect(
                "Selecione quem participa desta despesa",
                options=nomes_participantes,
                default=nomes_participantes,
            )
            selecionados = [p.id for p in grupo.participantes if p.nome in selecionados_nomes]

            if st.form_submit_button("💾 Salvar Despesa", use_container_width=True):
                valor = parse_valor(valor_txt)
                if descricao and valor and selecionados:
                    data_str = data_desp.strftime("%Y-%m-%d")
                    cotacao = obter_cotacao(moeda_pag, data_str)
                    valor_brl = round(valor * cotacao, 2)
                    desc_final = descricao
                    if moeda_pag != "BRL":
                        desc_final = f"{descricao} ({MOEDAS[moeda_pag]['simbolo']}{valor:.2f} @{cotacao:.4f})"
                    nova = Despesa(
                        descricao=desc_final, categoria=categoria, valor=valor_brl,
                        pagador_id=pagador.id, participantes_ids=selecionados,
                        data=data_str,
                    )
                    grupo.adicionar_despesa(nova)
                    persist()
                    if moeda_pag != "BRL":
                        st.toast(f"Convertido: {MOEDAS[moeda_pag]['simbolo']}{valor:.2f} = R${valor_brl:.2f}")
                    st.session_state._msg_sucesso = f'✅ Despesa "{descricao}" adicionada com sucesso!'
                    st.session_state.page = "dashboard"
                    st.rerun()
                elif not valor:
                    st.error("Valor invalido. Use virgula ou ponto como decimal (ex: 150,00).")
                elif not selecionados:
                    st.error("Selecione pelo menos uma pessoa para dividir.")
                else:
                    st.error("Preencha todos os campos.")

elif page == "participantes":
    st.markdown("## 👥 Participantes")
    st.markdown("**🔗 Link de convite:**")
    st.code(link_grupo(st.session_state.grupo_ativo_id), language=None)
    st.markdown("---")

    st.markdown("**➕ Adicionar participante:**")
    usuarios_fora = [
        uid for uid in st.session_state.usuarios
        if not any(p.id == uid for p in grupo.participantes)
    ]
    if usuarios_fora:
        user_sel = st.selectbox(
            "Selecione um usuario cadastrado",
            usuarios_fora,
            format_func=lambda uid: st.session_state.usuarios[uid].get("nome", uid),
            key="sel_user_add",
        )
        add_col1, add_col2 = st.columns(2)
        with add_col1:
            if st.button("➕ Adicionar ao grupo", key="btn_add_existing", use_container_width=True):
                udata = st.session_state.usuarios[user_sel]
                novo_p = Participante(
                    nome=udata.get("nome", user_sel),
                    chave_pix=udata.get("pix", ""),
                    tipo_chave_pix=udata.get("tipo_pix", "CPF"),
                    id=user_sel,
                )
                grupo.adicionar_participante(novo_p)
                persist()
                st.toast(f"✅ {udata.get('nome', user_sel)} adicionado ao grupo!")
                st.rerun()
        with add_col2:
            if st.button("➕ Adicionar a TODAS despesas", key="btn_add_all_desp", use_container_width=True):
                udata = st.session_state.usuarios[user_sel]
                # Adiciona ao grupo se ainda nao esta
                if not any(p.id == user_sel for p in grupo.participantes):
                    novo_p = Participante(
                        nome=udata.get("nome", user_sel),
                        chave_pix=udata.get("pix", ""),
                        tipo_chave_pix=udata.get("tipo_pix", "CPF"),
                        id=user_sel,
                    )
                    grupo.adicionar_participante(novo_p)
                # Adiciona a todas as despesas existentes
                for d in grupo.despesas:
                    if user_sel not in d.participantes_ids:
                        d.participantes_ids.append(user_sel)
                persist()
                st.toast(f"✅ {udata.get('nome', user_sel)} adicionado ao grupo e a todas as {len(grupo.despesas)} despesas!")
                st.rerun()
    else:
        st.info("✅ Todos os usuarios cadastrados ja estao neste grupo.")
    st.markdown("---")

    if grupo.participantes:
        n_cols = min(3, max(1, len(grupo.participantes)))
        cols = st.columns(n_cols)
        calc = Calculadora(grupo)
        for i, p in enumerate(grupo.participantes):
            with cols[i % n_cols]:
                saldo = calc.saldo_participante(p.id)
                cor = "🟢" if saldo >= 0 else "🔴"
                if p.id in st.session_state.usuarios and st.session_state.usuarios[p.id].get("foto"):
                    st.markdown(f'<img src="data:image/png;base64,{st.session_state.usuarios[p.id]["foto"]}" style="width:48px;height:48px;border-radius:50%;object-fit:cover">', unsafe_allow_html=True)
                else:
                    st.markdown(f"### {p.iniciais}")
                st.markdown(f'<b>{p.nome}</b>', unsafe_allow_html=True)
                st.caption(f"PIX ({p.tipo_chave_pix}): {p.chave_pix_formatada}")
                if grupo.despesas:
                    st.markdown(f"{cor} Saldo: {formatar_valor(saldo)}")
                if st.button("Remover", key=f"rm_{p.id}"):
                    grupo.remover_participante(p.id)
                    persist()
                    st.rerun()

elif page == "fechamento":
    if not grupo.despesas:
        st.info("Adicione despesas para ver o fechamento.")
    else:
        st.markdown("## 💰 Fechamento")
        calc = Calculadora(grupo)
        st.markdown(f"**Total gasto:** {formatar_valor(calc.total_gasto())} • **Participantes:** {len(grupo.participantes)}")
        st.markdown("---")

        # Calcula transferencias minimas
        transferencias = calcular_transferencias(grupo)
        grupo_id = st.session_state.grupo_ativo_id

        # Garante dict de pagamentos do grupo
        if grupo_id not in st.session_state.pagamentos:
            st.session_state.pagamentos[grupo_id] = {}

        if not transferencias:
            st.success("🎉 Tudo acertado! Nenhuma transferencia pendente.")
        else:
            st.markdown("### 📋 Transferencias necessarias")
            for idx, t in enumerate(transferencias):
                de_p = grupo.get_participante(t["de"])
                para_p = grupo.get_participante(t["para"])
                de_nome = de_p.nome if de_p else t["de"]
                para_nome = para_p.nome if para_p else t["para"]
                transfer_key = f"{t['de']}->{t['para']}"

                pag_info = st.session_state.pagamentos[grupo_id].get(transfer_key)
                is_pago = pag_info is not None

                with st.container():
                    c1, c2, c3 = st.columns([5, 2, 2])
                    with c1:
                        if is_pago:
                            marcado_nome = st.session_state.usuarios.get(pag_info["marcado_por"], {}).get("nome", pag_info["marcado_por"])
                            st.markdown(f"~~{de_nome} → {para_nome}~~ &nbsp; <span style='background:#006c49;color:#fff;padding:2px 8px;border-radius:12px;font-size:0.75rem;font-weight:700'>✅ PAGO</span>", unsafe_allow_html=True)
                            st.markdown(f'<small style="color:#6b7280">Marcado por <b>{marcado_nome}</b> em {formatar_data(pag_info.get("data", ""))}</small>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<b>{de_nome}</b> → <b>{para_nome}</b>', unsafe_allow_html=True)
                            if para_p and para_p.chave_pix:
                                st.caption(f"PIX ({para_p.tipo_chave_pix}): {para_p.chave_pix_formatada}")
                    with c2:
                        st.markdown(f"### {formatar_valor(t['valor'])}")
                    with c3:
                        if is_pago:
                            if st.button("↩️ Desfazer", key=f"unpay_{idx}"):
                                del st.session_state.pagamentos[grupo_id][transfer_key]
                                persist()
                                st.rerun()
                        else:
                            if st.button("✅ Marcar Pago", key=f"pay_{idx}"):
                                st.session_state.pagamentos[grupo_id][transfer_key] = {
                                    "marcado_por": st.session_state.usuario_logado,
                                    "data": datetime.now().strftime("%Y-%m-%d"),
                                }
                                persist()
                                st.toast(f"✅ Pagamento de {de_nome} para {para_nome} confirmado!")
                                st.rerun()
                    st.markdown("---")

        # Resumo de saldos (risca quem ja quitou)
        st.markdown("### 📊 Saldos")
        saldos = calc.saldos()
        pagamentos_grp = st.session_state.pagamentos.get(grupo_id, {})
        for p in grupo.participantes:
            s = saldos.get(p.id, 0)
            # Verifica se transfers deste participante estao todas pagas
            transfers_p = [t for t in transferencias if t["de"] == p.id or t["para"] == p.id]
            all_p_paid = all(f"{t['de']}->{t['para']}" in pagamentos_grp for t in transfers_p) if transfers_p else False
            if all_p_paid and abs(s) > 0.01:
                st.markdown(f"~~⚪ {p.nome} — quitado~~ ✅")
            elif s > 0.01:
                st.markdown(f'🟢 <b>{p.nome}</b> recebe {formatar_valor(s)}', unsafe_allow_html=True)
            elif s < -0.01:
                st.markdown(f'🔴 <b>{p.nome}</b> deve {formatar_valor(abs(s))}', unsafe_allow_html=True)
            else:
                st.markdown(f'⚪ <b>{p.nome}</b> zerado', unsafe_allow_html=True)
