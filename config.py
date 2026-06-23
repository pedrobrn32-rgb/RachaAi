"""
Configurações centralizadas do Racha Ai!
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── GCP ───
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "rachaai-data-bucket")

# ─── App ───
ADMIN_USER = "pedro"
BASE_URL = "https://rachaai.streamlit.app/"
SESSION_TIMEOUT_MINS = 30
PAGE_SIZE_DESPESAS = 15
PAGE_SIZE_GRUPOS = 10

# ─── Custo / Economia na nuvem ───
# Backups no GCS: limitados para não crescer infinitamente (custo de storage/operações).
ENABLE_BACKUPS = os.getenv("ENABLE_BACKUPS", "true").lower() == "true"
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "5"))
# TTL do cache em memória do GCS: quanto maior, menos leituras no bucket (mais barato).
GCS_CACHE_TTL = int(os.getenv("GCS_CACHE_TTL", "600"))
# Nível de log: WARNING em produção reduz a ingestão no Cloud Logging (mais barato).
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()

# ─── Moedas ───
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

# ─── Logging ───
import logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.WARNING),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
