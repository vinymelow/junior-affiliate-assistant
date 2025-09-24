"""
Teste para verificar se a IA está gerando mensagens com links de forma humanizada
"""
import asyncio
import json
from app.core.ai import ASSISTANT_INSTRUCTIONS

async def test_link_message():
    lead_context = {
        'nome': 'João',
        'genero': 'M',
        'cidade': 'São Paulo',
        'status_atual': 'Fase1_ContatoInicial',
        'detalhes_status': {},
        'resumo_conversa_anterior': 'Nenhuma conversa anterior.',
        'link_afiliado_principal': 'https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001'
    }
    
    system_prompt = ASSISTANT_INSTRUCTIONS.format(lead_context=json.dumps(lead_context, indent=2))
    
    print('=== TESTE DE MENSAGEM COM LINK ===')
    print('Pergunta do usuário: "Quero me cadastrar, como faço?"')
    print('\n--- INSTRUÇÕES DA IA ---')
    print('Verificando se as instruções incluem a regra sobre links...')
    
    # Verificar se a regra sobre links está nas instruções
    if "Links: SEMPRE envie links de forma natural" in system_prompt:
        print("✅ REGRA ENCONTRADA: IA foi instruída a enviar links sem backticks")
    else:
        print("❌ REGRA NÃO ENCONTRADA: IA pode ainda estar usando backticks")
    
    print('\n--- EXEMPLO DE RESPOSTA ESPERADA ---')
    print('ANTES (robotizada): "Confere aí, parça: `https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001` . Alguma dúvida?"')
    print('DEPOIS (humanizada): "Confere aí, parça: https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001 Alguma dúvida?"')

if __name__ == "__main__":
    asyncio.run(test_link_message())