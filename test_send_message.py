#!/usr/bin/env python3
"""
Teste de envio de mensagem WhatsApp
"""

import asyncio
from app.services.whatsapp import send_whatsapp_message

async def test_send_message():
    """Testa o envio de mensagem"""
    
    print("=== TESTE DE ENVIO DE MENSAGEM ===")
    
    # IMPORTANTE: Substitua pelo seu número real (apenas números)
    # Exemplo: "5511999999999" (código do país + DDD + número)
    numero = input("Digite seu número de WhatsApp (apenas números, ex: 5511999999999): ").strip()
    
    if not numero:
        print("❌ Número não informado!")
        return
    
    if not numero.isdigit():
        print("❌ Use apenas números!")
        return
    
    if len(numero) < 10:
        print("❌ Número muito curto!")
        return
    
    mensagem = "🤖 Teste do assistente Júnior!\n\nSe você recebeu esta mensagem, significa que a integração está funcionando perfeitamente! ✅"
    
    print(f"Enviando mensagem para: {numero}")
    print(f"Mensagem: {mensagem}")
    print()
    
    sucesso = await send_whatsapp_message(numero, mensagem)
    
    if sucesso:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print("❌ Falha no envio da mensagem")
        print()
        print("Possíveis causas:")
        print("1. Número não existe no WhatsApp")
        print("2. Número não está salvo nos contatos")
        print("3. Instância do WhatsApp não está conectada")
        print("4. Configuração da Evolution API incorreta")

if __name__ == "__main__":
    asyncio.run(test_send_message())