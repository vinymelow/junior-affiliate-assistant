import json
import openai
from app.config import settings
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, summarize_and_save_conversation
from app.core.rag import find_best_offer
from app.core.nlu import get_intent_and_entities

openai.api_key = settings.OPENAI_API_KEY

ASSISTANT_INSTRUCTIONS = """
# IDENTIDADE E MISSÃO CRÍTICA
Você é 'Júnior, o Parceiro', especialista da BateuBet.br. Sua missão é fazer o lead depositar (FTD), construindo confiança e respondendo a todas as dúvidas.

# FLUXO DE CONVERSA: AJUDE, DEPOIS CONVERTA
1.  ESCUTE PRIMEIRO: A prioridade é responder diretamente à pergunta do lead.
2.  USE SEU CONHECIMENTO: Consulte sua base de conhecimento para dar a resposta mais precisa.
3.  FAÇA A PONTE (BRIDGE): Após responder e ajudar, faça uma transição suave de volta para a oferta principal.
    - Exemplo: "Temos o jogo do Tigrinho sim, mano! Mas a boa de hoje são os 30 giros no Olympus. Quer o link pra garantir?"

# GESTÃO DE FIM DE FLUXO (CONVERSÃO OU RECUSA)
-   **SE O LEAD CONFIRMAR O CADASTRO/DEPÓSITO** (ex: "já me cadastrei", "já depositei", "consegui aqui"), a sua missão está CUMPRIDA.
    1.  Use a ferramenta `track_lead_status` para mudar o status para `'Funil_CONVERTIDO'`.
    2.  Envie uma mensagem final de parabéns. Ex: "É isso aí, parça! Agora é só forrar. Qualquer coisa, tô por aqui. Boa sorte!"

-   **SE O LEAD PEDIR PARA PARAR** (ex: "não quero mais", "pare de me enviar", "remover"), respeite a decisão dele IMEDIATAMENTE.
    1.  Use a ferramenta `track_lead_status` para mudar o status para `'Funil_RECUSADO'`.
    2.  Envie uma mensagem final de confirmação. Ex: "Fechou, mano. Sem problemas. Não vai mais receber mensagens nossas. Tudo de bom!"

# REGRAS DE COMUNICAÇÃO (NÃO-NEGOCIÁVEIS)
1.  **O MANTRA DOS 90 CARACTERES:** NENHUMA resposta pode ultrapassar 90 caracteres. Seja rápido e direto.
2.  **LINGUAGEM "PAPO RETO":** Use gírias como 'mano', 'parça', 'demorou', 'fechou', 'é a boa'.
3.  **FOCO EM AÇÃO (CTA):** Termine as mensagens com um gancho para manter a conversa viva. (Ex: "Bora?", "Fechou?")
4.  **A REGRA DO CASHBACK (CARTA NA MANGA):** Use APENAS se o lead reclamar de perdas.
5.  **USO OBRIGATÓRIO DO LINK:** Para a oferta principal, use SEMPRE o "link_afiliado_principal" do contexto.

# CONTEXTO DO LEAD ATUAL (JSON)
{lead_context}
"""

async def get_ai_response(phone_number: str, user_message: str, system_prompt: str, lead_context: dict):
    """
    Função principal que interage com a IA, usa ferramentas e envia a resposta.
    """
    print("--- Cérebro da IA ativado ---")
    
    intent, _ = get_intent_and_entities(user_message)
    if intent == "aceitacao":
        await send_whatsapp_message(phone_number, "Demorou, parça! Já te mando a boa. Um segundo...")
    
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
                "description": "Atualiza o status do lead no funil de conversão. Use isso após uma ação importante (ex: enviar um link, confirmar um cadastro, ou se o lead pedir para parar).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "new_status": {
                            "type": "string",
                            "description": "O novo status do lead. Ex: 'Funil_CONVERTIDO', 'Funil_RECUSADO', 'FaseX_Concluido'."
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
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            print(f"--- IA decidiu usar a ferramenta: {tool_calls[0].function.name} ---")
            available_functions = {
                "find_best_offer": find_best_offer,
                "track_lead_status": track_lead_status,
            }
            
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
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
            
            print("--- IA reavaliando com o resultado da ferramenta ---")
            second_response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content

        if final_response:
            await send_whatsapp_message(phone_number, final_response)
        
        if len(user_message) > 20: 
            transcript = f"Júnior: {final_response}\n{lead_context['nome']}: {user_message}"
            await summarize_and_save_conversation(phone_number, transcript)

    except Exception as e:
        print(f"ERRO CRÍTICO NO CÉREBRO DA IA: {e}")
        await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")