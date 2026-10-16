# ==============================================================================
# Dockerfile Oficial — Bot WhatsApp Multi-Empresa (Moçambique V4.0 Humanizado)
# Compatível com Render.com (Free), Koyeb (Free), Fly.io e Docker Local
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Variáveis de ambiente para execução limpa e sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    WHATSAPP_VERIFY_TOKEN="BRAGA_IO_SECURE_TOKEN_2026"

# Instalar dependências do Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copiar código do bot, base de dados JSON e pastas de mídias/PDFs oficiais
COPY whatsapp_multicompany_bot.py /app/whatsapp_multicompany_bot.py
COPY companies_data.json /app/companies_data.json
COPY media_assets /app/media_assets
COPY pdf_assets /app/pdf_assets

EXPOSE 8000

# Iniciar o servidor FastAPI na porta dinâmica do servidor gratuito ($PORT)
CMD ["sh", "-c", "uvicorn whatsapp_multicompany_bot:create_fastapi_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
