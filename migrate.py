#!/usr/bin/env python3
"""
Script de migração de dados antigos para novo formato
Migra arquivos individuais do GCS para arquivo único (data.json)
"""

import json
import sys
from google.cloud import storage
from config import GCS_BUCKET_NAME, logger

def migrate_to_single_file():
    """
    Migra estrutura antiga (múltiplos blobs) para estrutura nova (arquivo único)
    
    Antes:
        - usuarios.json
        - fotos.json
        - grupos.json
        - pagamentos.json
    
    Depois:
        - data.json (único, atomicamente)
        - backups/YYYYMMDD_HHMMSS.json (automático)
    """
    
    print("\n" + "=" * 60)
    print("🔄 Migração de Dados - Racha Ai! v2.0")
    print("=" * 60)
    
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        
        print(f"\n📦 Bucket: {GCS_BUCKET_NAME}")
        
        # ─── 1. Verificar estrutura atual ───
        print("\n1️⃣  Verificando estrutura atual...")
        
        blobs_antigos = {
            "usuarios": "usuarios.json",
            "fotos": "fotos.json",
            "grupos": "grupos.json",
            "pagamentos": "pagamentos.json",
        }
        
        dados_encontrados = {}
        
        for tipo, blob_name in blobs_antigos.items():
            blob = bucket.blob(blob_name)
            if blob.exists():
                try:
                    content = json.loads(blob.download_as_string())
                    dados_encontrados[tipo] = content
                    print(f"   ✅ {blob_name} encontrado ({len(str(content))} bytes)")
                except Exception as e:
                    print(f"   ⚠️  {blob_name} não conseguiu ler: {e}")
            else:
                print(f"   ℹ️  {blob_name} não existe")
        
        if not dados_encontrados:
            print("\n⚠️  Nenhum arquivo antigo encontrado!")
            print("   Seu bucket já usa a estrutura nova ou está vazio.")
            
            # Verificar se já existe data.json
            blob_novo = bucket.blob("data.json")
            if blob_novo.exists():
                print("   ✅ data.json já existe (migração já feita)")
                return True
            else:
                print("   ℹ️  Inicializando com estrutura padrão...")
                dados_encontrados = {
                    "usuarios": {},
                    "grupos": {},
                    "pagamentos": {},
                }
        
        # ─── 2. Processar dados ───
        print("\n2️⃣  Processando dados...")
        
        # Combinar dados
        dados_novo = {
            "usuarios": dados_encontrados.get("usuarios", {}),
            "grupos": dados_encontrados.get("grupos", {}),
            "pagamentos": dados_encontrados.get("pagamentos", {}),
        }
        
        # Reintegrar fotos em usuários
        if "fotos" in dados_encontrados:
            fotos = dados_encontrados["fotos"]
            for uid in dados_novo["usuarios"]:
                if uid in fotos:
                    dados_novo["usuarios"][uid]["foto"] = fotos[uid]
            print(f"   ✅ {len(fotos)} fotos reintegradas")
        
        print(f"   ✅ Usuários: {len(dados_novo['usuarios'])}")
        print(f"   ✅ Grupos: {len(dados_novo['grupos'])}")
        print(f"   ✅ Pagamentos: {len(dados_novo['pagamentos'])}")
        
        # ─── 3. Salvar novo arquivo ───
        print("\n3️⃣  Salvando em arquivo único...")
        
        blob_novo = bucket.blob("data.json")
        blob_novo.upload_from_string(
            json.dumps(dados_novo, ensure_ascii=False, indent=2),
            content_type="application/json"
        )
        print("   ✅ data.json criado com sucesso")
        
        # Backup automático
        from datetime import datetime
        backup_name = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}_migracao.json"
        bucket.blob(backup_name).upload_from_string(
            json.dumps(dados_novo, ensure_ascii=False),
            content_type="application/json"
        )
        print(f"   ✅ Backup automático: {backup_name}")
        
        # ─── 4. Arquivar/Deletar antigos (opcional) ───
        print("\n4️⃣  Arquivando dados antigos...")
        
        arquivo_antigo = f"ARQUIVADO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        arquivos_antigos = {}
        
        for tipo, blob_name in blobs_antigos.items():
            blob = bucket.blob(blob_name)
            if blob.exists():
                try:
                    content = json.loads(blob.download_as_string())
                    arquivos_antigos[blob_name] = content
                except:
                    pass
        
        if arquivos_antigos:
            bucket.blob(f"ARCHIVE/{arquivo_antigo}").upload_from_string(
                json.dumps(arquivos_antigos, ensure_ascii=False),
                content_type="application/json"
            )
            print(f"   ✅ Arquivos antigos em: ARCHIVE/{arquivo_antigo}")
        
        # ─── 5. Resumo ───
        print("\n" + "=" * 60)
        print("✅ Migração Concluída com Sucesso!")
        print("=" * 60)
        
        print("\n📊 Resumo da Migração:")
        print(f"   • Usuários: {len(dados_novo['usuarios'])}")
        print(f"   • Grupos: {len(dados_novo['grupos'])}")
        print(f"   • Pagamentos: {sum(len(p) for p in dados_novo['pagamentos'].values())}")
        
        print("\n📁 Estrutura Nova:")
        print("   ✅ data.json (arquivo único, atomicamente)")
        print("   ✅ backups/ (automáticos)")
        print("   ✅ ARCHIVE/ (dados antigos)")
        
        print("\n🚀 Próximos passos:")
        print("   1. Usar app_v2.py")
        print("   2. Testar login (senhas serão automigradas)")
        print("   3. Verificar que tudo funciona")
        print("   4. Deletar manualmente ARCHIVE/ se desejar (backup em segurança)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        print(f"\n❌ Erro na migração: {e}")
        print("\n⚠️  Tente:")
        print("   1. Verificar credenciais GCP")
        print("   2. Confirmar bucket existe")
        print("   3. Confirmar permissões de read/write")
        return False

def print_structure():
    """Mostra estrutura atual do bucket"""
    print("\n📂 Estrutura do Bucket:")
    print("=" * 60)
    
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        
        blobs = list(bucket.list_blobs())
        
        if not blobs:
            print("   (vazio)")
            return
        
        arquivos = {}
        for blob in blobs:
            path = blob.name
            prefix = path.split('/')[0] if '/' in path else 'root'
            if prefix not in arquivos:
                arquivos[prefix] = []
            arquivos[prefix].append(path)
        
        for prefix in sorted(arquivos.keys()):
            print(f"\n   📁 {prefix}/")
            for arquivo in arquivos[prefix]:
                tamanho = blobs[[b.name for b in blobs].index(arquivo)].size
                print(f"      • {arquivo} ({tamanho:,} bytes)")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    print_structure()
    
    resposta = input("\n🔄 Deseja executar a migração? (s/n): ").lower()
    
    if resposta == 's':
        sucesso = migrate_to_single_file()
        sys.exit(0 if sucesso else 1)
    else:
        print("\n⏭️  Migração cancelada")
        sys.exit(0)
