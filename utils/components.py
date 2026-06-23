"""
Componentes UI reutilizáveis para manter consistência visual
"""
import streamlit as st
from utils.formatacao import Formatador

fmt = Formatador()

def card_despesa(despesa, grupo, show_actions: bool = True):
    """Card reutilizável para exibir despesa"""
    pag = grupo.get_participante(despesa.pagador_id)
    nomes_divisao = [
        grupo.get_participante(pid).nome 
        for pid in despesa.participantes_ids 
        if grupo.get_participante(pid)
    ]
    valor_pp = despesa.valor / len(despesa.participantes_ids) if despesa.participantes_ids else 0
    
    with st.container(border=True):
        col_card, col_valor, col_actions = st.columns([7, 2, 1], gap="small")
        
        with col_card:
            st.markdown(f"**{despesa.descricao}**")
            st.caption(
                f"🏷️ {despesa.categoria} • 📅 {fmt.formatar_data(despesa.data)} • "
                f"💳 {pag.nome if pag else '-'}"
            )
            st.caption(f"➗ {', '.join(nomes_divisao)} ({fmt.formatar_valor(valor_pp)}/pp)")
        
        with col_valor:
            st.metric("", fmt.formatar_valor(despesa.valor), label_visibility="collapsed")
        
        if show_actions:
            with col_actions:
                col_e, col_d = st.columns(2, gap="small")
                with col_e:
                    return st.button("✏️", key=f"edit_{despesa.id}", help="Editar", use_container_width=True)
                with col_d:
                    return st.button("🗑️", key=f"del_{despesa.id}", help="Deletar", use_container_width=True)

def card_participante(participante, grupo, show_saldo: bool = True):
    """Card para exibir participante com saldo"""
    from utils.calculos import Calculadora
    
    calc = Calculadora(grupo)
    saldo = calc.saldo_participante(participante.id)
    
    with st.container(border=True):
        col_info, col_saldo, col_action = st.columns([6, 2, 1], gap="small")
        
        with col_info:
            # Foto se existir
            foto = None
            if participante.id in st.session_state.usuarios:
                foto = st.session_state.usuarios[participante.id].get("foto")
            
            if foto:
                st.markdown(
                    f'<img src="data:image/png;base64,{foto}" '
                    f'style="width:32px;height:32px;border-radius:50%;object-fit:cover">',
                    unsafe_allow_html=True
                )
            
            st.markdown(f"**{participante.nome}**")
            st.caption(f"PIX ({participante.tipo_chave_pix}): {participante.chave_pix_formatada}")
        
        if show_saldo:
            with col_saldo:
                cor = "🟢" if saldo >= 0 else "🔴"
                st.metric(cor, fmt.formatar_valor(saldo), label_visibility="collapsed")
        
        with col_action:
            return st.button("❌", key=f"rm_{participante.id}", help="Remover", use_container_width=True)

def card_pagamento(transferencia, grupo, pagamentos_grp: dict, grupo_id: str, idx: int):
    """Card para exibir transferência pendente/paga"""
    de_p = grupo.get_participante(transferencia["de"])
    para_p = grupo.get_participante(transferencia["para"])
    de_nome = de_p.nome if de_p else transferencia["de"]
    para_nome = para_p.nome if para_p else transferencia["para"]
    transfer_key = f"{transferencia['de']}->{transferencia['para']}"
    
    pag_info = pagamentos_grp.get(transfer_key)
    is_pago = pag_info is not None
    
    with st.container(border=True):
        col_info, col_valor, col_action = st.columns([6, 2, 2], gap="small")
        
        with col_info:
            if is_pago:
                marcado_nome = st.session_state.usuarios.get(
                    pag_info["marcado_por"], {}
                ).get("nome", pag_info["marcado_por"])
                st.markdown(
                    f"~~{de_nome} → {para_nome}~~ ✅ **PAGO**",
                    unsafe_allow_html=True
                )
                st.caption(f"por {marcado_nome} em {fmt.formatar_data(pag_info.get('data', ''))}")
            else:
                st.markdown(f"**{de_nome}** → **{para_nome}**")
                if para_p and para_p.chave_pix:
                    st.caption(f"📱 PIX: {para_p.chave_pix_formatada}")
        
        with col_valor:
            st.metric("", fmt.formatar_valor(transferencia["valor"]), label_visibility="collapsed")
        
        with col_action:
            if is_pago:
                return st.button("↩️ Desfazer", key=f"unpay_{idx}", use_container_width=True)
            else:
                return st.button("✅ Pago", key=f"pay_{idx}", use_container_width=True)

def alert_info(titulo: str, mensagem: str):
    """Alerta informativo customizado"""
    st.info(f"**{titulo}**\n\n{mensagem}")

def alert_sucesso(mensagem: str):
    """Alerta de sucesso customizado"""
    st.success(f"✅ {mensagem}")

def alert_erro(mensagem: str):
    """Alerta de erro customizado"""
    st.error(f"❌ {mensagem}")

def alert_aviso(mensagem: str):
    """Alerta de aviso customizado"""
    st.warning(f"⚠️ {mensagem}")

def divider():
    """Divider customizado"""
    st.markdown("---")

def link_compartilhamento(grupo_id: str):
    """Mostra link de compartilhamento"""
    from config import BASE_URL
    link = f"{BASE_URL}?grupo={grupo_id}"
    st.markdown("**🔗 Link para compartilhar:**")
    st.code(link, language=None)
    return link
