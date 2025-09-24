#!/usr/bin/env python3
"""
Script de teste para verificar se o módulo de IA está funcionando corretamente.
"""

import asyncio
import json
from app.core.ai import get_ai_response, ASSISTANT_INSTRUCTIONS
from app.config import settings

async def test_ai_response():
    """Testa a geração de resposta da IA"""
    print("=== TESTE DO MÓDULO DE IA ===")
    
    # Dados de teste
    phone_number = "5511999999999"
    user_message = "Oi, tudo bem?"
    
    # Contexto de teste
    lead_context = {
        "nome": "João",
        "genero": "M",
        "cidade": "São Paulo",
        "status_atual": "Fase1_ContatoInicial",
        "detalhes_status": {},
        "resumo_conversa_anterior": "Nenhuma conversa anterior.",
        "link_afiliado_principal": "https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001"
    }
    
    # Preparar system prompt
    system_prompt = ASSISTANT_INSTRUCTIONS.format(lead_context=json.dumps(lead_context, indent=2))
    
    print(f"Testando com:")
    print(f"- Telefone: {phone_number}")
    print(f"- Mensagem: {user_message}")
    print(f"- Contexto: {lead_context}")
    print("\n--- INICIANDO TESTE ---")
    
    try:
        # Simular chamada da IA (sem enviar WhatsApp)
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        ai_response = response.choices[0].message.content
        
        print(f"✅ SUCESSO! IA gerou resposta:")
        print(f"'{ai_response}'")
        print(f"\nTamanho da resposta: {len(ai_response)} caracteres")
        
        if len(ai_response) <= 90:
            print("✅ Resposta dentro do limite de 90 caracteres")
        else:
            print("⚠️  Resposta excede 90 caracteres")
            
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_response())
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n💥 TESTE FALHOU!")