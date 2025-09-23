#!/usr/bin/env python3
"""
Teste da Evolution API - Verifica se a instância está conectada e funcionando
"""

import asyncio
import httpx
from app.config import settings

async def test_evolution_api():
    """Testa a conexão com a Evolution API"""
    
    print("=== TESTE DA EVOLUTION API ===")
    print(f"URL: {settings.EVOLUTION_API_URL}")
    print(f"Instância: {settings.EVOLUTION_INSTANCE}")
    print(f"API Key: {settings.EVOLUTION_API_KEY[:10]}...")
    print()
    
    # 1. Testar status da instância
    print("1. Verificando status da instância...")
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.EVOLUTION_API_URL}/instance/connectionState/{settings.EVOLUTION_INSTANCE}"
            headers = {"apikey": settings.EVOLUTION_API_KEY}
            
            response = await client.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Resposta: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("instance", {}).get("state") == "open":
                    print("✅ Instância conectada!")
                else:
                    print("❌ Instância não está conectada")
                    print("Você precisa escanear o QR Code no painel da Evolution API")
            else:
                print("❌ Erro ao verificar status da instância")
                
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print()
    
    # 2. Listar contatos (se conectado)
    print("2. Listando contatos disponíveis...")
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.EVOLUTION_API_URL}/chat/findContacts/{settings.EVOLUTION_INSTANCE}"
            headers = {"apikey": settings.EVOLUTION_API_KEY}
            
            response = await client.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                contacts = response.json()
                if contacts:
                    print(f"✅ Encontrados {len(contacts)} contatos:")
                    for contact in contacts[:5]:  # Mostrar apenas os primeiros 5
                        print(f"  - {contact.get('pushName', 'Sem nome')}: {contact.get('id', 'N/A')}")
                else:
                    print("⚠️ Nenhum contato encontrado")
            else:
                print(f"❌ Erro ao listar contatos: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro ao listar contatos: {e}")
    
    print()
    print("=== INSTRUÇÕES ===")
    print("1. Se a instância não estiver conectada:")
    print("   - Acesse o painel da Evolution API")
    print("   - Escaneie o QR Code com seu WhatsApp")
    print()
    print("2. Para testar o envio:")
    print("   - Use um número real que aparece na lista de contatos")
    print("   - Formato: apenas números (ex: 5511999999999)")
    print()
    print("3. Para receber mensagens:")
    print("   - Configure o webhook na Evolution API para:")
    print(f"   - URL: http://SEU_IP:8000/api/whatsapp/webhook")
    print("   - Eventos: MESSAGE_UPSERT")

if __name__ == "__main__":
    asyncio.run(test_evolution_api())