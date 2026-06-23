"""
Validações e sanitizações de entrada
"""
import re
from decimal import Decimal
from typing import Optional

def sanitize_input(texto: str, max_len: int = 500) -> str:
    """Remove caracteres perigosos e limita tamanho"""
    if not texto:
        return ""
    
    texto = texto.strip()
    # Remove tags HTML/JS
    texto = re.sub(r'<[^>]*>', '', texto)
    # Remove caracteres de controle
    texto = ''.join(c for c in texto if ord(c) >= 32)
    # Limita tamanho
    return texto[:max_len]

def validate_username(username: str) -> bool:
    """Username válido: 3-20 chars, apenas alphanumério e underscore"""
    if not username:
        return False
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username.lower()) is not None

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cpf(cpf: str) -> bool:
    """Valida CPF (formato básico, sem verificador)"""
    if not cpf:
        return False
    cpf = cpf.replace('.', '').replace('-', '').replace('/', '')
    return len(cpf) == 11 and cpf.isdigit()

def validate_phone(telefone: str) -> bool:
    """Valida telefone (11 dígitos)"""
    if not telefone:
        return False
    phone = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
    return len(phone) == 11 and phone.isdigit()

def parse_valor(texto: str) -> Optional[float]:
    """Converte entrada de usuário em float
    Aceita: 150, 150,00, 150.50, 1.250,50
    """
    if not texto:
        return None
    
    txt = texto.strip().replace(" ", "")
    
    if not txt:
        return None
    
    # Lógica: se tem . e , usa o último como decimal
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

def validate_data(data_str: str) -> bool:
    """Valida formato de data YYYY-MM-DD"""
    if not data_str:
        return False
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, data_str) is not None

def validate_senha(senha: str) -> tuple[bool, str]:
    """
    Valida força de senha
    Retorna: (válido, mensagem)
    """
    if not senha or len(senha) < 6:
        return False, "Senha deve ter no mínimo 6 caracteres"
    
    if len(senha) > 100:
        return False, "Senha muito longa (máx 100 chars)"
    
    return True, "✅ Senha válida"

def sanitize_categoria(categoria: str, categorias_validas: list) -> str:
    """Valida categoria contra lista branca"""
    if categoria in categorias_validas:
        return categoria
    return categorias_validas[0] if categorias_validas else "Outro"

def sanitize_moeda(moeda: str, moedas_validas: dict) -> str:
    """Valida moeda contra lista branca"""
    if moeda in moedas_validas:
        return moeda
    return "BRL"
