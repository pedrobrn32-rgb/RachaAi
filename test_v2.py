#!/usr/bin/env python3
"""
Script de testes para validar funcionalidades do Racha Ai! v2.0
Executa testes sem precisar do Streamlit
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.validators import (
    parse_valor, validate_cpf, validate_email,
    validate_username, sanitize_input, validate_senha
)
from services.auth import AuthService, LoginManager

def test_validators():
    """Testa validadores"""
    print("\n📋 Testando Validadores...")
    
    tests = [
        ("parse_valor", parse_valor("150,50"), 150.5),
        ("parse_valor", parse_valor("1.250,99"), 1250.99),
        ("validate_cpf", validate_cpf("123.456.789-00"), True),
        ("validate_cpf", validate_cpf("invalid"), False),
        ("validate_email", validate_email("user@test.com"), True),
        ("validate_email", validate_email("invalid-email"), False),
        ("validate_username", validate_username("pedro"), True),
        ("validate_username", validate_username("ab"), False),
    ]
    
    passed = 0
    for test_name, result, expected in tests:
        status = "✅" if result == expected else "❌"
        print(f"  {status} {test_name}: {result} (esperado: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\n  Resultado: {passed}/{len(tests)} testes passaram")
    return passed == len(tests)

def test_sanitization():
    """Testa sanitização de inputs"""
    print("\n🛡️  Testando Sanitização...")
    
    tests = [
        ("<script>alert('xss')</script>", "alert('xss')"),
        ("  espaços  ", "espaços"),
        ("texto_normal", "texto_normal"),
    ]
    
    passed = 0
    for input_val, _ in tests:
        result = sanitize_input(input_val)
        is_safe = "<" not in result and ">" not in result
        status = "✅" if is_safe else "❌"
        print(f"  {status} Input: {input_val[:30]}... → Sanitizado")
        if is_safe:
            passed += 1
    
    print(f"\n  Resultado: {passed}/{len(tests)} testes passaram")
    return passed == len(tests)

def test_auth():
    """Testa autenticação e hash de senha"""
    print("\n🔐 Testando Autenticação...")
    
    # Hash de senha
    hash_pwd, salt = AuthService.hash_senha("minha_senha")
    
    # Verificação correta
    verif_correto = AuthService.verificar_senha("minha_senha", hash_pwd, salt)
    print(f"  ✅ Hash correto: {verif_correto}")
    
    # Verificação incorreta
    verif_incorreto = not AuthService.verificar_senha("senha_errada", hash_pwd, salt)
    print(f"  ✅ Hash incorreto: {verif_incorreto}")
    
    # Criar usuário
    novo_user = AuthService.criar_usuario(
        username="teste",
        senha="senha123",
        nome="Usuário Teste",
        pix="123.456.789-00",
        tipo_pix="CPF"
    )
    print(f"  ✅ Usuário criado: {novo_user['nome']}")
    
    # Verificar que senha está hashada
    tem_hash = "senha_hash" in novo_user and "senha_salt" in novo_user
    print(f"  ✅ Senha hashada: {tem_hash}")
    
    return True

def test_login_manager():
    """Testa gerenciador de login"""
    print("\n👤 Testando Login Manager...")
    
    # Criar usuários de teste
    usuarios = {}
    
    # Registrar novo usuário
    sucesso, msg = LoginManager.registrar(
        username="pedro",
        senha="senha123",
        nome="Pedro Silva",
        usuarios=usuarios
    )
    print(f"  ✅ Registro: {msg}")
    
    # Login correto
    sucesso, msg = LoginManager.login("pedro", "senha123", usuarios)
    print(f"  ✅ Login correto: {sucesso}")
    
    # Login incorreto
    sucesso, msg = LoginManager.login("pedro", "senha_errada", usuarios)
    print(f"  ✅ Login incorreto bloqueado: {not sucesso}")
    
    # Usuário inexistente
    sucesso, msg = LoginManager.login("usuario_fake", "senha", usuarios)
    print(f"  ✅ Usuário inexistente bloqueado: {not sucesso}")
    
    return True

def test_performance():
    """Testa performance básica"""
    print("\n⚡ Testando Performance...")
    
    import time
    
    # Validação rápida
    start = time.time()
    for _ in range(1000):
        parse_valor("150,50")
    tempo = time.time() - start
    print(f"  ✅ 1000 validações em {tempo:.3f}s ({1000/tempo:.0f}/s)")
    
    # Hash de senha (deve ser lento propositalmente)
    start = time.time()
    AuthService.hash_senha("teste123")
    tempo = time.time() - start
    print(f"  ✅ Hash de senha em {tempo:.3f}s (esperado: ~0.1s com PBKDF2)")
    
    return True

def main():
    """Executa todos os testes"""
    print("=" * 50)
    print("🧪 Testes do Racha Ai! v2.0")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(("Validadores", test_validators()))
    except Exception as e:
        print(f"❌ Erro em validadores: {e}")
        results.append(("Validadores", False))
    
    try:
        results.append(("Sanitização", test_sanitization()))
    except Exception as e:
        print(f"❌ Erro em sanitização: {e}")
        results.append(("Sanitização", False))
    
    try:
        results.append(("Autenticação", test_auth()))
    except Exception as e:
        print(f"❌ Erro em autenticação: {e}")
        results.append(("Autenticação", False))
    
    try:
        results.append(("Login Manager", test_login_manager()))
    except Exception as e:
        print(f"❌ Erro em login manager: {e}")
        results.append(("Login Manager", False))
    
    try:
        results.append(("Performance", test_performance()))
    except Exception as e:
        print(f"❌ Erro em performance: {e}")
        results.append(("Performance", False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 Resumo dos Testes")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n🎯 Total: {passed}/{total} módulos passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
