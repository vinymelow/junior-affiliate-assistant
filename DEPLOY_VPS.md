# 🚀 Deploy na VPS - Guia Completo

## 📋 Pré-requisitos

### VPS Requirements
- **OS:** Ubuntu 20.04+ ou Debian 11+
- **RAM:** Mínimo 1GB (recomendado 2GB+)
- **Storage:** Mínimo 10GB
- **CPU:** 1 vCPU (recomendado 2+)

### Softwares Necessários
- Docker
- Docker Compose
- Git
- Nginx (será instalado via Docker)

## 🛠️ Preparação da VPS

### 1. Conectar na VPS
```bash
ssh root@SEU_IP_VPS
# ou
ssh usuario@SEU_IP_VPS
```

### 2. Atualizar Sistema
```bash
apt update && apt upgrade -y
```

### 3. Instalar Docker
```bash
# Instalar dependências
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar Docker
systemctl start docker
systemctl enable docker
```

### 4. Instalar Docker Compose (se não veio com o Docker)
```bash
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

## 📦 Deploy da Aplicação

### 1. Clonar/Enviar Código
```bash
# Opção 1: Git (se o código estiver no GitHub)
git clone https://github.com/SEU_USUARIO/junior-affiliate-assistant.git
cd junior-affiliate-assistant

# Opção 2: Upload via SCP
# No seu computador local:
# scp -r junior-affiliate-assistant/ root@SEU_IP_VPS:/root/
```

### 2. Configurar Variáveis de Ambiente
```bash
# Criar arquivo .env
nano .env
```

Conteúdo do `.env`:
```env
OPENAI_API_KEY=sua_chave_openai_aqui
EVOLUTION_API_URL=https://evolution.orla-tavira.com
EVOLUTION_API_KEY=sua_chave_evolution_aqui
EVOLUTION_INSTANCE=sua_instancia_aqui
```

### 3. Ajustar Configurações

#### Nginx (se necessário)
```bash
# Editar nginx.conf para seu domínio
nano nginx.conf

# Substituir 'server_name _;' por 'server_name seu-dominio.com;'
```

#### Docker Compose (se necessário)
```bash
nano docker-compose.yml
# Verificar portas e volumes
```

### 4. Construir e Iniciar
```bash
# Construir imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps
```

### 5. Verificar Logs
```bash
# Logs da aplicação
docker-compose logs junior-assistant

# Logs do nginx
docker-compose logs nginx

# Logs em tempo real
docker-compose logs -f
```

## 🔧 Configuração do Firewall

### UFW (Ubuntu Firewall)
```bash
# Instalar UFW
apt install -y ufw

# Configurar regras básicas
ufw default deny incoming
ufw default allow outgoing

# Permitir SSH
ufw allow ssh
ufw allow 22

# Permitir HTTP e HTTPS
ufw allow 80
ufw allow 443

# Ativar firewall
ufw enable

# Verificar status
ufw status
```

## 🌐 Configuração de Domínio (Opcional)

### 1. Apontar Domínio para VPS
No seu provedor de domínio, configure:
- **Tipo A:** `@` → `IP_DA_VPS`
- **Tipo A:** `www` → `IP_DA_VPS`

### 2. Certificado SSL com Let's Encrypt
```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Parar nginx temporariamente
docker-compose stop nginx

# Gerar certificado
certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com

# Copiar certificados para o projeto
mkdir -p ssl
cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ssl/key.pem

# Ajustar nginx.conf para usar HTTPS
nano nginx.conf
# Descomentar seção HTTPS e ajustar server_name

# Reiniciar nginx
docker-compose up -d nginx
```

## 🔄 Configurar Webhook na Evolution API

### 1. Acessar Painel da Evolution API
- URL: https://evolution.orla-tavira.com
- Login com suas credenciais

### 2. Configurar Webhook
- **URL:** `http://SEU_IP_VPS/api/whatsapp/webhook` (ou `https://seu-dominio.com/api/whatsapp/webhook`)
- **Eventos:** `MESSAGE_UPSERT`
- **Método:** `POST`

## ✅ Testes Finais

### 1. Testar API
```bash
# Teste básico
curl http://SEU_IP_VPS/

# Teste webhook
curl -X POST http://SEU_IP_VPS/api/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"messages.upsert","data":{"messageType":"conversation","key":{"remoteJid":"5511999999999@s.whatsapp.net"},"message":{"conversation":"teste"}}}'
```

### 2. Testar WhatsApp
- Envie uma mensagem para o número conectado na Evolution API
- Verifique se o bot responde

## 🔧 Manutenção

### Comandos Úteis
```bash
# Ver logs
docker-compose logs -f

# Reiniciar serviços
docker-compose restart

# Atualizar código
git pull
docker-compose build
docker-compose up -d

# Backup dos dados
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Monitorar recursos
docker stats
```

### Renovação SSL (Automática)
```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Porta 80/443 ocupada**
   ```bash
   sudo lsof -i :80
   sudo lsof -i :443
   # Parar serviços conflitantes
   ```

2. **Docker não inicia**
   ```bash
   systemctl status docker
   systemctl restart docker
   ```

3. **Webhook não funciona**
   - Verificar firewall
   - Testar URL manualmente
   - Verificar logs do nginx

4. **SSL não funciona**
   - Verificar se domínio aponta para VPS
   - Verificar certificados
   - Verificar configuração nginx

## 📊 Monitoramento

### Logs Importantes
```bash
# Aplicação
docker-compose logs junior-assistant | tail -100

# Nginx
docker-compose logs nginx | tail -100

# Sistema
tail -f /var/log/syslog
```

### Métricas
```bash
# Uso de recursos
docker stats

# Espaço em disco
df -h

# Memória
free -h

# CPU
top
```

---

## 🎯 Checklist Final

- [ ] VPS configurada e atualizada
- [ ] Docker e Docker Compose instalados
- [ ] Código enviado para VPS
- [ ] Arquivo .env configurado
- [ ] Firewall configurado
- [ ] Aplicação rodando (docker-compose up -d)
- [ ] Webhook configurado na Evolution API
- [ ] Testes de envio/recebimento funcionando
- [ ] SSL configurado (se usando domínio)
- [ ] Monitoramento configurado

**🎉 Parabéns! Seu assistente está rodando na VPS!**