# 🔧 Configuração do WhatsApp - Guia Completo

## 📋 Status Atual

✅ **Python instalado e funcionando** (versão 3.13.7)  
✅ **Dependências instaladas**  
✅ **Servidor FastAPI rodando** (porta 8000)  
✅ **Evolution API conectada** (instância: bcl_instance)  
❌ **Envio de mensagens falhando** (erro 400 - número não existe)

## 🚨 Problema Identificado

O erro `400 - número não existe` indica que:
1. O número de teste não existe no WhatsApp, OU
2. O número não está nos contatos da instância conectada, OU
3. O formato do número está incorreto

## 🛠️ Soluções

### 1. Testar com Número Real

Execute o teste com seu próprio número:

```bash
py test_send_message.py
```

**Importante:** Use apenas números, sem símbolos:
- ✅ Correto: `5511999999999` (país + DDD + número)
- ❌ Errado: `+55 (11) 99999-9999`

### 2. Verificar Contatos na Evolution API

Acesse o painel da Evolution API:
- URL: https://evolution.orla-tavira.com
- Verifique se o número está na lista de contatos
- Se não estiver, envie uma mensagem manual primeiro

### 3. Configurar Webhook (Para Receber Mensagens)

No painel da Evolution API, configure:
- **URL do Webhook:** `http://SEU_IP_PUBLICO:8000/api/whatsapp/webhook`
- **Eventos:** `MESSAGE_UPSERT`
- **Método:** `POST`

### 4. Testar Localmente

Para testar o recebimento de mensagens:

```bash
# Simular mensagem recebida
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/whatsapp/webhook" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"event":"messages.upsert","data":{"messageType":"conversation","key":{"remoteJid":"SEU_NUMERO@s.whatsapp.net"},"message":{"conversation":"oi"}}}'
```

## 🚀 Deploy na VPS

### Pré-requisitos
- VPS com Ubuntu/Debian
- Docker instalado
- Domínio configurado (opcional)
- Certificado SSL (recomendado)

### Arquivos Necessários

1. **Dockerfile** (já existe)
2. **docker-compose.yml** (será criado)
3. **nginx.conf** (para proxy reverso)
4. **Variáveis de ambiente** (.env)

### Passos do Deploy

1. **Preparar arquivos de configuração**
2. **Fazer upload do código**
3. **Configurar nginx**
4. **Iniciar containers**
5. **Configurar webhook na Evolution API**

## 🔍 Diagnóstico

Execute estes comandos para diagnosticar problemas:

```bash
# Testar Evolution API
py test_evolution_api.py

# Testar envio de mensagem
py test_send_message.py

# Verificar logs do servidor
# (no terminal onde o uvicorn está rodando)
```

## 📞 Próximos Passos

1. **Teste com número real** usando `test_send_message.py`
2. **Configure o webhook** no painel da Evolution API
3. **Teste o fluxo completo** enviando uma mensagem para o bot
4. **Prepare o deploy** na VPS quando tudo estiver funcionando

## ⚠️ Observações Importantes

- O número de teste `5511999999999` não existe, por isso o erro 400
- Use sempre seu número real para testes
- A Evolution API precisa ter o número nos contatos
- Para produção, configure um domínio e SSL