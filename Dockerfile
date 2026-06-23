FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Smoke-import: falha o build cedo se algum módulo sumir,
# em vez de quebrar em runtime no Cloud Run (ModuleNotFoundError).
RUN python -c "import utils.validators, utils.components, utils.renderizador, utils.calculos, utils.formatacao, utils.algoritmo_divisao, models.grupo, services.gcs, config"

EXPOSE 8080

CMD ["streamlit", "run", "app_v2.py", "--server.port=8080", "--server.address=0.0.0.0"]