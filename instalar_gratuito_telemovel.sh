#!/usr/bin/env bash
# ==============================================================================
# INSTALADOR AUTOMÁTICO 100% GRATUITO (TELEMÓVEL TERMUX / LINUX / PC)
# Bot WhatsApp V4.0 Humanizado: Braga.io | Vanguard Living | Inglês Semestre
# ==============================================================================
set -e

echo "======================================================================"
echo "🚀 INICIANDO INSTALAÇÃO GRATUITA DO BOT WHATSAPP V4.0 (MOÇAMBIQUE)"
echo "======================================================================"

# 1. Instalar pacotes necessários
echo "📦 [1/3] A verificar e instalar dependências Python..."
pip install --quiet fastapi "uvicorn[standard]" requests pillow numpy pydantic

# 2. Verificar ficheiros locais e pastas de PDFs/Fotos
echo "✅ [2/3] A verificar catálogos PDF e fotos reais da oficina..."
mkdir -p media_assets pdf_assets
python3 -c "import whatsapp_multicompany_bot as b; print('   -> Motor V4.0 validado com sucesso! Empresas ativas:', list(b.COMPANIES.keys()))"

# 3. Iniciar servidor FastAPI na porta 8000
echo "🌐 [3/3] A iniciar o servidor do Bot na porta 8000..."
echo ""
echo "👉 O seu Webhook está pronto em: http://localhost:8000/webhook"
echo "👉 Para verificar o estado no navegador: http://localhost:8000/status"
echo "👉 Token de Verificação Oficial: BRAGA_IO_SECURE_TOKEN_2026"
echo "======================================================================"

python3 -m uvicorn whatsapp_multicompany_bot:create_fastapi_app --factory --host 0.0.0.0 --port "${PORT:-8000}"