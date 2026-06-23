import json
import os
from datetime import datetime
from google.cloud import storage
from models.grupo import Grupo

# Diretorio GCS bucket
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "rachaai-data-bucket")


def _get_bucket():
    """Retorna bucket GCS. Client() sem args usa credenciais do ambiente (Cloud Run SA)."""
    client = storage.Client()
    return client.bucket(GCS_BUCKET_NAME)


def salvar_usuarios(usuarios: dict):
    """Salva dict de usuarios em JSON no GCS. Fotos separadas (base64 grande)."""
    users_data = {}
    for uid, uinfo in usuarios.items():
        entry = {k: v for k, v in uinfo.items() if k != "foto"}
        users_data[uid] = entry

    photos_data = {uid: uinfo.get("foto") for uid, uinfo in usuarios.items() if uinfo.get("foto")}

    bucket = _get_bucket()

    blob_users = bucket.blob("usuarios.json")
    blob_users.upload_from_string(
        json.dumps(users_data, ensure_ascii=False, indent=2),
        content_type="application/json",
    )

    blob_photos = bucket.blob("fotos.json")
    blob_photos.upload_from_string(
        json.dumps(photos_data, ensure_ascii=False),
        content_type="application/json",
    )


def carregar_usuarios() -> dict:
    """Carrega usuarios do GCS. Retorna {} se nao existir."""
    bucket = _get_bucket()
    blob_users = bucket.blob("usuarios.json")

    if not blob_users.exists():
        return {}

    try:
        users_data = json.loads(blob_users.download_as_string())

        blob_photos = bucket.blob("fotos.json")
        photos_data = {}
        if blob_photos.exists():
            photos_data = json.loads(blob_photos.download_as_string())

        for uid in users_data:
            users_data[uid]["foto"] = photos_data.get(uid)

        return users_data
    except (json.JSONDecodeError, Exception):
        return {}


def salvar_grupos(grupos: dict):
    """Salva dict de grupos {slug: Grupo} em JSON no GCS."""
    groups_data = {}
    for slug, grupo in grupos.items():
        groups_data[slug] = grupo.to_dict()
    groups_data["_salvo_em"] = datetime.now().isoformat()

    bucket = _get_bucket()
    blob_groups = bucket.blob("grupos.json")
    blob_groups.upload_from_string(
        json.dumps(groups_data, ensure_ascii=False, indent=2),
        content_type="application/json",
    )


def carregar_grupos() -> dict:
    """Carrega grupos do GCS. Retorna {} se nao existir."""
    bucket = _get_bucket()
    blob_groups = bucket.blob("grupos.json")

    if not blob_groups.exists():
        return {}

    try:
        groups_data = json.loads(blob_groups.download_as_string())
        groups_data.pop("_salvo_em", None)

        grupos_dict = {}
        for slug, gdict in groups_data.items():
            grupos_dict[slug] = Grupo.from_dict(gdict)
        return grupos_dict
    except (json.JSONDecodeError, Exception):
        return {}


# ─── Classe de compatibilidade (importada por __init__.py) ───
class Persistencia:
    """Wrapper para manter compatibilidade com utils/__init__.py."""
    salvar_usuarios = staticmethod(salvar_usuarios)
    carregar_usuarios = staticmethod(carregar_usuarios)
    salvar_grupos = staticmethod(salvar_grupos)
    carregar_grupos = staticmethod(carregar_grupos)
