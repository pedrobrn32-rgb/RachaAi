"""
Autenticação segura com hash de senhas
"""
import hashlib
import hmac
import secrets
import streamlit as st
from typing import Optional
from config import logger

class AuthService:
    """Serviço seguro de autenticação"""
    
    @staticmethod
    def hash_senha(senha: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hasheia senha com salt usando PBKDF2
        Retorna: (hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)
        
        # PBKDF2 com 100k iterações (seguro)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            senha.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return hash_obj.hex(), salt
    
    @staticmethod
    def verificar_senha(senha: str, hash_stored: str, salt: str) -> bool:
        """Verifica se senha corresponde ao hash armazenado"""
        hash_input, _ = AuthService.hash_senha(senha, salt)
        # Comparação timing-safe
        return hmac.compare_digest(hash_input, hash_stored)
    
    @staticmethod
    def criar_usuario(
        username: str,
        senha: str,
        nome: str,
        pix: str = "",
        tipo_pix: str = "CPF",
        foto: Optional[str] = None
    ) -> dict:
        """Cria novo usuário com senha hashada"""
        hash_senha, salt = AuthService.hash_senha(senha)
        
        return {
            "nome": nome,
            "senha_hash": hash_senha,
            "senha_salt": salt,
            "pix": pix,
            "tipo_pix": tipo_pix,
            "foto": foto,
            "admin": False,
            "criado_em": __import__('datetime').datetime.now().isoformat(),
        }
    
    @staticmethod
    def migrar_senha_legada(senha_texto: str) -> dict:
        """Migra senhas antigas (texto plano) para hash seguro"""
        hash_senha, salt = AuthService.hash_senha(senha_texto)
        return {
            "senha_hash": hash_senha,
            "senha_salt": salt,
        }
    
    @staticmethod
    def session_timeout_check(timeout_mins: int = 30) -> bool:
        """Verifica se session expirou por inatividade"""
        from datetime import datetime, timedelta
        
        if "ultima_atividade" not in st.session_state:
            st.session_state.ultima_atividade = datetime.now()
            return False
        
        elapsed = (datetime.now() - st.session_state.ultima_atividade).total_seconds() / 60
        
        if elapsed > timeout_mins:
            logger.warning(f"⏰ Sessão expirada após {elapsed:.0f} minutos")
            return True
        
        # Atualiza timestamp
        st.session_state.ultima_atividade = datetime.now()
        return False

class LoginManager:
    """Gerencia login/logout de usuários"""
    
    @staticmethod
    def login(username: str, senha: str, usuarios: dict) -> tuple[bool, str]:
        """
        Tenta fazer login
        Retorna: (sucesso, mensagem)
        """
        if username not in usuarios:
            logger.warning(f"🚫 Tentativa de login com usuário inexistente: {username}")
            return False, "❌ Usuário não encontrado"
        
        user_data = usuarios[username]
        
        # Suporta senhas antigas (texto plano) e novas (hash)
        if "senha_hash" in user_data:
            # Nova autenticação com hash
            if not AuthService.verificar_senha(
                senha,
                user_data["senha_hash"],
                user_data.get("senha_salt", "")
            ):
                logger.warning(f"🚫 Senha incorreta para: {username}")
                return False, "❌ Senha incorreta"
        else:
            # Autenticação legada (texto plano)
            if user_data.get("senha") != senha:
                logger.warning(f"🚫 Senha incorreta (legada) para: {username}")
                return False, "❌ Senha incorreta"
            
            # Migra para hash seguro automaticamente
            migration = AuthService.migrar_senha_legada(senha)
            usuarios[username].update(migration)
            # Remove campo legado
            usuarios[username].pop("senha", None)
            logger.info(f"🔐 Migrado para hash: {username}")
        
        logger.info(f"✅ Login bem-sucedido: {username}")
        return True, f"✅ Bem-vindo, {user_data.get('nome', username)}!"
    
    @staticmethod
    def registrar(
        username: str,
        senha: str,
        nome: str,
        usuarios: dict,
        **kwargs
    ) -> tuple[bool, str]:
        """
        Registra novo usuário
        Retorna: (sucesso, mensagem)
        """
        # Validações
        if username in usuarios:
            return False, "❌ Usuário já existe"
        
        if len(username) < 3:
            return False, "❌ Username deve ter no mínimo 3 caracteres"
        
        if len(senha) < 6:
            return False, "❌ Senha deve ter no mínimo 6 caracteres"
        
        if not nome or len(nome) < 2:
            return False, "❌ Nome deve ter no mínimo 2 caracteres"
        
        # Cria usuário
        novo_usuario = AuthService.criar_usuario(
            username=username,
            senha=senha,
            nome=nome,
            **kwargs
        )
        
        usuarios[username] = novo_usuario
        logger.info(f"🆕 Novo usuário registrado: {username}")
        return True, f"✅ Bem-vindo, {nome}!"
