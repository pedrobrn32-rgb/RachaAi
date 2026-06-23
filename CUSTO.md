# 💸 Guia de custo zero (Racha Ai!)

Objetivo: manter o app **o mais barato possível** no Google Cloud — idealmente dentro do free tier / centavos.

## ✅ O que já está no código (automático)

| Onde | Economia |
|---|---|
| [services/gcs.py](services/gcs.py) | **Não regrava** dados se nada mudou (hash) → menos operações Class A no GCS. |
| [services/gcs.py](services/gcs.py) | Backups **limitados a `MAX_BACKUPS`** (default 5) e podados a cada save → storage não cresce infinito. Antes: 1 backup novo por save, **sem nunca apagar**. |
| [services/gcs.py](services/gcs.py) | Cache em memória do GCS configurável (`GCS_CACHE_TTL`, default **600s**) → menos leituras no bucket. |
| [config.py](config.py) | Log padrão **`WARNING`** (era `INFO`) → menos ingestão no Cloud Logging. Logs de leitura/cache viraram `debug`. |
| [.dockerignore](.dockerignore) | Imagem Docker enxuta (fora `inicio.png` ~8 MB, docs, legados) → menos storage no Artifact Registry e build mais rápido. |
| [Dockerfile](Dockerfile) | `--cpu-throttling`, `--min-instances=0`, `--max-instances=1` (no workflow) → **CPU só é cobrada durante requisições; ocioso ≈ R$0**. |
| [cloudbuild-shutdown.yaml](cloudbuild-shutdown.yaml) | Serviço de shutdown também escala a zero (min=0, max=1, 256Mi, throttling). |

### Variáveis de ambiente para regular (Cloud Run → Variáveis)
- `ENABLE_BACKUPS=false` → desliga backups completamente (mais barato ainda).
- `MAX_BACKUPS=3` → menos backups guardados.
- `GCS_CACHE_TTL=1800` → 30 min de cache (menos leituras; dados demoram mais a atualizar entre instâncias).
- `LOG_LEVEL=ERROR` → quase nenhum log.

---

## 🔧 Passos manuais no console GCP (uma vez)

> Não dá para fazer por código — rode no Cloud Shell ou console.

### 1. Apagar a pilha de backups antigos já acumulada
O código novo limita os **futuros**, mas os antigos continuam lá. Limpe uma vez
(use `gcloud storage`, recomendado pelo Google no lugar do `gsutil`):
```bash
# Lista quantos existem
gcloud storage ls gs://rachaai-data-bucket/backups/ | wc -l
# Apaga TODOS os backups antigos (o app recria os próximos, limitados a MAX_BACKUPS)
gcloud storage rm --recursive gs://rachaai-data-bucket/backups/
```
> Se aparecer "1 files/objects could not be removed", normalmente é inofensivo
> (placeholder de pasta, versionamento, ou um backup novo criado durante a limpeza).
> Para incluir versões antigas: `gcloud storage rm --recursive --all-versions gs://rachaai-data-bucket/backups/`

### 2. (JÁ FEITO no workflow) Limpeza de imagens Docker
O [.github/workflows/deploy.yml](.github/workflows/deploy.yml) **já apaga a imagem anterior
do app e do shutdown a cada deploy** (`gcloud artifacts docker images delete ... --delete-tags`),
então só fica a imagem nova — não acumula.

Opcional (rede de segurança): uma **política de limpeza** roda continuamente mesmo se um
deploy falhar no meio (o passo atual usa `|| true` e pode engolir erros). Mantém só as 2 mais recentes:
```bash
gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy \
  --location=southamerica-east1 \
  --policy=- <<'EOF'
[
  { "name": "manter-recentes", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 2} },
  { "name": "apagar-resto", "action": {"type": "Delete"}, "condition": {"olderThan": "7d"} }
]
EOF
```

### 3. Orçamento + kill-switch (rede de segurança)
O serviço `rachaai-shutdown` **deleta o app** quando o orçamento passa de ~55% ([shutdown/main.py](shutdown/main.py)). Para isso ser barato, o **valor do orçamento precisa ser baixo**:
- Billing → Budgets & alerts → crie/edite um budget de, ex., **R$ 5/mês**.
- Conecte ao tópico Pub/Sub `budget-alerts` (o workflow já cria a subscription apontando para o `rachaai-shutdown`).

### 4. Evitar serviço de shutdown duplicado
Há **dois** caminhos que implantam o shutdown:
- [.github/workflows/deploy.yml](.github/workflows/deploy.yml) → serviço **`rachaai-shutdown`** (este é o usado, com Pub/Sub).
- [cloudbuild-shutdown.yaml](cloudbuild-shutdown.yaml) → serviço **`shutdown`** (alternativo).

Tenha **apenas um**. Se só usa o GitHub Actions, apague o outro:
```bash
gcloud run services delete shutdown --region=southamerica-east1 --quiet
```

### 5. Confirmar que o app está em escala-a-zero
```bash
gcloud run services describe rachaai-app --region=southamerica-east1 \
  --format='value(spec.template.metadata.annotations)'
# Esperado: autoscaling minScale=0, maxScale=1, cpu-throttling
```

---

## 📊 Resumo de onde o dinheiro vai (e por que agora é ~R$0)
- **Cloud Run**: cobra CPU/memória só durante requisições (throttling) e escala a zero → ocioso grátis.
- **GCS**: arquivos minúsculos; operações reduzidas (skip-unchanged) e **backups agora podados** (antes cresciam para sempre — era o vazamento real) → centavos.
- **Artifact Registry**: **já controlado** — o workflow apaga a imagem anterior a cada deploy. Política de limpeza (passo 2) é só rede de segurança.
- **Cloud Build**: free tier de 120 min/dia cobre os deploys.
- **Cloud Logging**: free tier de 50 GB/mês; com `LOG_LEVEL=WARNING` quase não ingere nada.
