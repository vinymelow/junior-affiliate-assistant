import json
import openai
from app.config import settings
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, summarize_and_save_conversation
from app.core.rag import find_best_offer
from app.core.nlu import get_intent_and_entities

# Configura a chave da API da OpenAI
openai.api_key = settings.OPENAI_API_KEY

ASSISTANT_INSTRUCTIONS = """
# CONTEXTO
Você é 'Júnior, o Parceiro', um especialista da BateuBet.br. Sua missão é finalizar a conversão de um lead que ACABOU de receber uma ligação sua sobre uma promoção.

# PONTO DE PARTIDA
O lead JÁ SABE da promoção principal: "depositar qualquer valor para ganhar 30 giros no Gates of Olympus e concorrer a R$5000 por dia". Sua primeira mensagem no WhatsApp foi um lembrete com o link.

# PERSONA
-   **Linguagem:** Direta, benefício em primeiro lugar, Classe C. Use gírias como 'mano', 'parça', 'demorou', 'fechou', 'é a boa'.
-   **Tom:** Confiante e persuasivo. Aja como se fosse óbvio que o lead vai aproveitar a vantagem. Crie um senso de urgência e oportunidade.

# FLUXO DE TRABALHO
-   **Seu Objetivo Principal:** Fazer o lead clicar no link, depositar e jogar. Quebre qualquer objeção que o impeça.
-   **Tirar Dúvidas:** Esteja pronto para responder sobre como funciona o depósito, a segurança da plataforma, como usar os giros, etc.
-   **Se o lead reclamar de perdas ou azar (depois de já ter jogado):** Use a 'carta na manga' do cashback.

# REGRAS DE OURO
1.  **SEJA DIRECIONADO A BENEFÍCIOS:** Sempre reforce as vantagens: "são 30 giros na faixa", "é a chance de forrar com 5 mil todo dia".
2.  **A REGRA DO CASHBACK (MUITO IMPORTANTE):** Você sabe que existe um cashback de até 200 giros na sexta-feira. **NUNCA** mencione que a pessoa precisa perder para ganhar. Se alguém reclamar "ah, perdi meu dinheiro", você responde algo como: "Relaxa, mano! Na BateuBet a gente te dá uma moral. Toda sexta rola um cashback pra te dar uma segunda chance e tentar forrar de novo." Use-o como uma ferramenta de retenção e objeção, NUNCA como uma oferta inicial.
3.  **FOCO TOTAL:** Não fale de outras casas ou outros jogos. O foco é Gates of Olympus e BateuBet.br.

# CONTEXTO DO LEAD ATUAL (JSON)
{lead_context}
"""

async def get_ai_response(phone_number: str, user_message: str, system_prompt: str, lead_context: dict):
    """
    Função principal que interage com a IA, usa ferramentas e envia a resposta.
    """
    print("--- Cérebro da IA ativado ---")
    
    # Simples lógica de NLU para intenções óbvias
    intent, _ = get_intent_and_entities(user_message)
    if intent == "aceitacao":
        await send_whatsapp_message(phone_number, "Demorou, parça! Já te mando a boa. Um segundo...")
    
    # Ferramentas disponíveis para a IA
    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_best_offer",
                "description": "Busca na base de conhecimento a melhor oferta ou bônus com base no interesse do lead (ex: 'futebol', 'slots', 'roleta').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "interest": {
                            "type": "string",
                            "description": "O interesse principal do lead, ex: 'futebol', 'slots', 'cassino ao vivo'."
                        }
                    },
                    "required": ["interest"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_lead_status",
                "description": "Atualiza o status do lead no funil de conversão. Use isso após uma ação importante (ex: enviar um link, confirmar um cadastro).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "new_status": {
                            "type": "string",
                            "description": "O novo status do lead. Ex: 'Fase1_LinkEnviado', 'FaseX_Concluido', 'FaseX_Recusou'."
                        },
                        "details": {
                            "type": "object",
                            "description": "Um objeto JSON com detalhes relevantes. Ex: {\"casa_ofertada\": \"Casa Alpha Bet\", \"oferta\": \"Link de R$1\"}"
                        }
                    },
                    "required": ["new_status", "details"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        # Primeiro chamado para a IA
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Passo 2: Se a IA decidir usar uma ferramenta
        if tool_calls:
            print(f"--- IA decidiu usar a ferramenta: {tool_calls[0].function.name} ---")
            available_functions = {
                "find_best_offer": find_best_offer,
                "track_lead_status": track_lead_status,
            }
            
            # Por simplicidade, executamos apenas a primeira ferramenta chamada
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            # Adicionando parâmetros que a IA não conhece mas a função precisa
            if function_name == 'track_lead_status':
                function_args['lead_id'] = lead_context.get('lead_id', 'unknown')
                function_args['nome'] = lead_context.get('nome')
                function_args['telefone'] = phone_number

            function_response = await function_to_call(**function_args)

            messages.append(response_message)
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(function_response),
            })
            
            # Terceiro Passo: Chamado final com o resultado da ferramenta
            print("--- IA reavaliando com o resultado da ferramenta ---")
            second_response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content

        # Envia a resposta final para o usuário
        await send_whatsapp_message(phone_number, final_response)
        
        # Opcional: Sumariza a conversa após uma interação significativa
        if len(user_message) > 20: # Simples heurística
            transcript = f"Júnior: {final_response}\n{lead_context['nome']}: {user_message}"
            await summarize_and_save_conversation(phone_number, transcript)

    except Exception as e:
        print(f"ERRO CRÍTICO NO CÉREBRO DA IA: {e}")
        await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")