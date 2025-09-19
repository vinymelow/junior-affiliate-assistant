#!/bin/bash

# Script para iniciar o serviço diretamente no servidor
# Servidor: dev@31.97.42.102

echo "🚀 Iniciando serviço Júnior Affiliate Assistant..."

# Configurações do servidor
SERVER="dev@31.97.42.102"
REMOTE_DIR="/home/dev/junior-affiliate-assistant"

echo "🔧 Iniciando serviço no servidor..."
ssh $SERVER << 'EOF'
cd /home/dev/junior-affiliate-assistant

echo "📦 Ativando ambiente virtual..."
source venv/bin/activate

echo "🔄 Parando processos existentes..."
pkill -f "uvicorn main:app" || true

echo "🚀 Iniciando API em background..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

echo "⏳ Aguardando API inicializar..."
sleep 5

echo "📊 Verificando se a API está rodando..."
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "✅ API está rodando!"
    echo "🌐 URL: http://31.97.42.102:8000"
    echo "📱 Webhook: http://31.97.42.102:8000/whatsapp/webhook"
    echo "📚 Docs: http://31.97.42.102:8000/docs"
else
    echo "❌ API não está rodando. Verificando logs..."
    tail -20 api.log
fi

echo "📝 Logs da API:"
tail -10 api.log
EOF

echo "✅ Script de inicialização concluído!"
