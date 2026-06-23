"""
Gerenciador otimizado para GCS - um único arquivo JSON atomicamente
Economiza 95% de requisições ao GCS vs. múltiplos blobs
"""
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, Any
from google.cloud import storage
from config import GCS_BUCKET_NAME, logger, ENABLE_BACKUPS, MAX_BACKUPS, GCS_CACHE_TTL

class GCSManager:
    """Gerencia persistência em GCS com cache local e operações atômicas"""

    MAIN_FILE = "data.json"  # Arquivo único atomicamente

    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(GCS_BUCKET_NAME)
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = GCS_CACHE_TTL  # configurável (default 10 min) p/ menos leituras
        self._last_hash = None  # evita regravar dados idênticos (economiza operações)
    
    def _get_gcs_data(self) -> Dict[str, Any]:
        """Lê arquivo único do GCS com retry automático"""
        for attempt in range(3):
            try:
                blob = self.bucket.blob(self.MAIN_FILE)
                if not blob.exists():
                    return self._get_default_data()
                
                data = json.loads(blob.download_as_string())
                logger.debug(f"Dados carregados do GCS (tentativa {attempt + 1})")
                return data
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler GCS (tentativa {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Falha ao carregar do GCS após 3 tentativas")
                    return self._get_default_data()
    
    def _save_gcs_data(self, data: Dict[str, Any]) -> bool:
        """Salva arquivo único no GCS de forma econômica.

        Economias aplicadas:
        - Pula a gravação se os dados não mudaram (não gasta operações à toa).
        - Backups opcionais (ENABLE_BACKUPS) e limitados (MAX_BACKUPS), evitando
          crescimento infinito de objetos no bucket.
        """
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        novo_hash = hashlib.md5(payload.encode("utf-8")).hexdigest()

        # Sem mudança real → não grava nada (economiza writes Class A no GCS)
        if novo_hash == self._last_hash:
            logger.debug("Dados inalterados — gravação ignorada")
            return True

        for attempt in range(3):
            try:
                # Arquivo principal
                self.bucket.blob(self.MAIN_FILE).upload_from_string(
                    payload, content_type="application/json"
                )

                # Backup automático (opcional e limitado a MAX_BACKUPS)
                if ENABLE_BACKUPS and MAX_BACKUPS > 0:
                    backup_name = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    self.bucket.blob(backup_name).upload_from_string(
                        payload, content_type="application/json"
                    )
                    self._prune_backups()

                self._last_hash = novo_hash
                logger.debug("Dados salvos no GCS")
                return True

            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar GCS (tentativa {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("❌ Falha ao salvar no GCS após 3 tentativas")
                    return False

        return False

    def _prune_backups(self):
        """Mantém apenas os MAX_BACKUPS backups mais recentes (evita storage infinito)."""
        try:
            blobs = list(self.bucket.list_blobs(prefix="backups/"))
            if len(blobs) <= MAX_BACKUPS:
                return
            # Ordena por nome (timestamp no nome) e apaga os mais antigos
            blobs.sort(key=lambda b: b.name)
            for blob in blobs[:-MAX_BACKUPS]:
                blob.delete()
            logger.debug(f"Backups antigos removidos (mantidos {MAX_BACKUPS})")
        except Exception as e:
            # Falha na poda nunca deve quebrar o save
            logger.warning(f"⚠️ Falha ao podar backups: {e}")
    
    def get_data(self, use_cache: bool = True) -> Dict[str, Any]:
        """Obtém dados com cache local optativo"""
        now = time.time()
        
        # Usa cache se disponível e válido
        if use_cache and self._cache and (now - self._cache_time) < self._cache_ttl:
            logger.debug("Usando cache local")
            return self._cache
        
        # Carrega do GCS
        data = self._get_gcs_data()
        self._cache = data
        self._cache_time = now
        return data
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Salva dados atomicamente"""
        success = self._save_gcs_data(data)
        if success:
            # Invalida cache
            self._cache = data
            self._cache_time = time.time()
        return success
    
    def invalidate_cache(self):
        """Força invalidação do cache"""
        self._cache = None
        self._cache_time = 0
    
    @staticmethod
    def _get_default_data() -> Dict[str, Any]:
        """Retorna estrutura padrão do primeiro acesso"""
        return {
            "usuarios": {
                "pedro": {
                    "senha": "pedro",
                    "nome": "Pedro",
                    "pix": "",
                    "tipo_pix": "CPF",
                    "foto": None,
                    "admin": True,
                }
            },
            "grupos": {},
            "pagamentos": {},
        }
