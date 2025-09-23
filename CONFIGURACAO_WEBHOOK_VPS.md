# 🔗 Configuração do Webhook - Evolution API para VPS

## ✅ Status do Deploy

**Sistema funcionando na VPS:**
- **IP da VPS:** `31.97.42.102`
- **Porta da aplicação:** `8000` (direto)
- **Porta do nginx:** `8080` (proxy)
- **Webhook endpoint:** `/api/whatsapp/webhook`

## 🎯 URLs para Configurar no Evolution API

### Opção 1: Acesso Direto (Recomendado)
```
http://31.97.42.102:8000/api/whatsapp/webhook
```

### Opção 2: Via Nginx (Alternativa)
```
http://31.97.42.102:8080/api/whatsapp/webhook
```

## 📋 Passos para Configurar

### 1. Acessar Evolution API
- **URL:** https://evolution.orla-tavira.com
- **Instância:** `bcl_instance`
- **API Key:** `15d1e1c55709fddef640ab79dbec2f2a`

### 2. Configurar Webhook
No painel da Evolution API:

1. **Vá para Configurações da Instância**
2. **Seção Webhook:**
   - **URL:** `http://31.97.42.102:8000/api/whatsapp/webhook`
   - **Método:** `POST`
   - **Eventos:** Selecionar `MESSAGE_UPSERT`
   - **Headers:** `Content-Type: application/json`

### 3. Testar Configuração
Após configurar, teste enviando uma mensagem para o número conectado na Evolution API.

## 🧪 Testes Realizados

✅ **Containers rodando:** junior-assistant e nginx  
✅ **API respondendo:** `http://31.97.42.102:8000/`  
✅ **Webhook funcionando:** Recebe e processa mensagens  
✅ **Firewall configurado:** Portas 8000 e 8080 abertas  

### Teste do Webhook
```bash
# Comando testado com sucesso:
curl -X POST http://31.97.42.102:8000/api/whatsapp/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "messageType": "conversation",
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "teste"
      }
    }
  }'

# Resposta: {"status":"recebido e processando em background"}
```

## 🔧 Monitoramento

### Verificar Logs
```bash
# Logs da aplicação
ssh dev@31.97.42.102 "sudo docker logs junior-assistant --tail 20"

# Logs do nginx
ssh dev@31.97.42.102 "sudo docker logs junior-nginx --tail 20"

# Status dos containers
ssh dev@31.97.42.102 "sudo docker ps"
```

### Testar Conectividade
```bash
# Teste básico da API
curl http://31.97.42.102:8000/

# Teste do webhook
curl -X POST http://31.97.42.102:8000/api/whatsapp/webhook \
  -H 'Content-Type: application/json' \
  -d '{"test": "message"}'
```

## 🚨 Troubleshooting

### Se o webhook não funcionar:

1. **Verificar firewall:**
   ```bash
   ssh dev@31.97.42.102 "sudo ufw status"
   ```

2. **Verificar containers:**
   ```bash
   ssh dev@31.97.42.102 "sudo docker ps"
   ```

3. **Verificar logs:**
   ```bash
   ssh dev@31.97.42.102 "sudo docker logs junior-assistant"
   ```

### Problemas Comuns:

- **Timeout:** Verificar se a porta está aberta no firewall
- **404 Not Found:** Verificar se a URL está correta
- **500 Internal Error:** Verificar logs da aplicação

## 🎉 Próximos Passos

1. **Configure o webhook** na Evolution API com a URL: `http://31.97.42.102:8000/api/whatsapp/webhook`
2. **Teste enviando uma mensagem** para o número conectado
3. **Monitore os logs** para verificar se está funcionando
4. **Opcional:** Configure um domínio e SSL para produção

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs dos containers
2. Teste a conectividade com curl
3. Verifique se o firewall está configurado corretamente
4. Confirme se a Evolution API está conectada

**Sistema pronto para uso!** 🚀