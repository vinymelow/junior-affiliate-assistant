#!/bin/bash

# Script de Deploy Melhorado para o Servidor SSH
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
    --exclude='venv' \
    ./ $SERVER:$REMOTE_DIR/

echo "🔧 Configurando ambiente no servidor..."
ssh $SERVER << 'EOF'
cd /home/dev/junior-affiliate-assistant

echo "📋 Removendo ambiente virtual antigo..."
rm -rf venv

echo "🐍 Criando novo ambiente virtual..."
python3 -m venv venv

echo "📦 Ativando ambiente virtual e instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Configurando permissões..."
chmod +x main.py
chmod 755 /home/dev/junior-affiliate-assistant

echo "🔄 Parando serviço (se estiver rodando)..."
sudo systemctl stop junior-assistant 2>/dev/null || true

echo "📝 Atualizando arquivo de serviço..."
sudo cp deployment/junior_assistant.service /etc/systemd/system/

echo "🔄 Recarregando e iniciando serviço..."
sudo systemctl daemon-reload
sudo systemctl enable junior-assistant
sudo systemctl start junior-assistant

echo "⏳ Aguardando serviço inicializar..."
sleep 5

echo "📊 Status do serviço:"
sudo systemctl status junior-assistant --no-pager

echo "📝 Logs recentes:"
sudo journalctl -u junior-assistant --no-pager -n 10

echo "🌐 Testando conectividade..."
curl -s http://localhost:8000/docs > /dev/null && echo "✅ API está respondendo!" || echo "❌ API não está respondendo"
EOF

echo "✅ Deploy concluído!"
echo "🌐 A API deve estar rodando em: http://31.97.42.102:8000"
echo "📱 Webhook do WhatsApp: http://31.97.42.102:8000/whatsapp/webhook"
echo "📚 Documentação da API: http://31.97.42.102:8000/docs"
