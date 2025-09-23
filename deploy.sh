#!/bin/bash

# --- CONFIGURAÇÕES ---
SERVER="dev@31.97.42.102"
REMOTE_DIR="/home/dev/junior-affiliate-assistant"
SERVICE_NAME="junior-assistant"
SERVICE_FILE="deployment/junior_assistant.service"

echo "🚀 Iniciando deploy 'Hard Reset' para o Júnior Affiliate Assistant..."

# --- PASSO 1: ENVIAR FICHEIROS ATUALIZADOS ---
echo "📤 A enviar a versão mais recente do código para o servidor..."
# Nota: Esta versão do rsync garante que a pasta 'deployment' seja copiada.
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='*.tar.gz' \
    --exclude='data/' \
    --exclude='*.db' \
    ./ "$SERVER:$REMOTE_DIR/"

# --- PASSO 2: EXECUTAR CONFIGURAÇÃO REMOTA VIA SSH ---
echo "🔧 A configurar o ambiente e a reiniciar o serviço no servidor..."
ssh "$SERVER" << EOF
    # Navega para o diretório do projeto
    cd "$REMOTE_DIR"

    echo "--- PASSO 1: PARAR E DESATIVAR O SERVIÇO ANTIGO (SE EXISTIR) ---"
    sudo systemctl stop "$SERVICE_NAME.service" 2>/dev/null || echo "INFO: Serviço não estava a correr."
    sudo systemctl disable "$SERVICE_NAME.service" 2>/dev/null || echo "INFO: Serviço não estava ativo."
    sudo rm -f "/etc/systemd/system/$SERVICE_NAME.service"
    sudo systemctl daemon-reload

    echo "--- PASSO 2: COPIAR O NOVO FICHEIRO DE SERVIÇO ---"
    if [ -f "$SERVICE_FILE" ]; then
        echo "✅ Ficheiro de serviço encontrado. A copiá-lo para o sistema..."
        sudo cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
    else
        echo "❌ ERRO CRÍTICO: Ficheiro de serviço '$SERVICE_FILE' não encontrado no servidor!"
        exit 1
    fi

    echo "--- PASSO 3: REINSTALAR AMBIENTE VIRTUAL E DEPENDÊNCIAS ---"
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo "✅ Ambiente virtual recriado e dependências instaladas."

    echo "--- PASSO 4: REINICIAR O GESTOR DE SERVIÇOS ---"
    sudo systemctl daemon-reload
    echo "✅ Gestor de serviços atualizado."

    echo "--- PASSO 5: INICIAR E VERIFICAR O NOVO SERVIÇO ---"
    sudo systemctl enable "$SERVICE_NAME.service"
    sudo systemctl start "$SERVICE_NAME.service"
    
    echo "⏳ A aguardar 5 segundos para o serviço estabilizar..."
    sleep 5
    
    echo "📊 Status final do serviço:"
    sudo systemctl status "$SERVICE_NAME.service" --no-pager
    
    echo "📝 A verificar os logs de arranque para confirmar a nova versão:"
    sudo journalctl -u "$SERVICE_NAME.service" -n 15 --no-pager
EOF

echo "✅ Deploy 'Hard Reset' concluído!"
echo "O assistente está agora a executar a versão mais recente. Por favor, teste novamente."