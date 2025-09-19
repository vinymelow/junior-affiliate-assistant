#!/bin/bash

# Script de Deploy para o Servidor SSH
# Servidor: dev@31.97.42.102

echo "🚀 Iniciando deploy do Júnior Affiliate Assistant..."

# Configurações do servidor
SERVER="dev@31.97.42.102"
REMOTE_DIR="/home/dev/junior-affiliate-assistant"
SERVICE_NAME="junior-assistant"

echo "📦 Fazendo backup do projeto atual..."
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' .

echo "📤 Enviando arquivos para o servidor..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='backup-*.tar.gz' \
    ./ $SERVER:$REMOTE_DIR/

echo "🔧 Configurando ambiente no servidor..."
ssh $SERVER << 'EOF'
cd /home/dev/junior-affiliate-assistant

echo "📋 Atualizando dependências..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔄 Reiniciando serviço..."
sudo systemctl stop junior-assistant
sudo systemctl daemon-reload
sudo systemctl start junior-assistant
sudo systemctl enable junior-assistant

echo "📊 Status do serviço:"
sudo systemctl status junior-assistant --no-pager

echo "📝 Logs recentes:"
sudo journalctl -u junior-assistant --no-pager -n 20
EOF

echo "✅ Deploy concluído!"
echo "🌐 A API deve estar rodando em: http://31.97.42.102:8000"
echo "📱 Webhook do WhatsApp: http://31.97.42.102:8000/whatsapp/webhook"
