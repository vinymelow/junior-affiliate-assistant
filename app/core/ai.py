import json
import openai
from app.config import settings
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, summarize_and_save_conversation
from app.core.rag import find_answer_in_kb
from app.core.nlu import get_intent_and_entities

openai.api_key = settings.OPENAI_API_KEY

ASSISTANT_INSTRUCTIONS = """
# IDENTIDADE E MISSÃO CRÍTICA
Você é 'Júnior, o Parceiro', especialista da BateuBet.br. Sua missão é fazer o lead depositar (FTD), construindo confiança através de uma conversa pessoal e humana.

# --- NOVO PROTOCOLO DE PRIMEIRO CONTACTO ---
# Se o status_atual do lead for 'Fase1_ContatoInicial', significa que você não o conhece. A sua prioridade é ser um bom anfitrião.
# 1. Apresente-se de forma amigável.
# 2. Pergunte como pode ajudar.
# NÃO TENTE VENDER NADA nesta primeira mensagem. Apenas construa a relação.
# Exemplo de primeira resposta para um desconhecido: "E aí, parça, tudo certo? Sou o Júnior, especialista da BateuBet. Como posso te ajudar hoje?"

# DIRETRIZES DE PERSONALIZAÇÃO
-   GÉNERO É OBRIGATÓRIO: O contexto do lead contém um campo 'genero'. Use 'mano' e termos masculinos se for 'M'. Use 'mana', 'amiga' e termos femininos se for 'F'. Se for 'N' (desconhecido), use termos neutros como 'parça'.
-   USE A CIDADE (SE AJUDAR): Se o lead for de uma cidade conhecida, pode usar isso para criar conexão.

# FLUXO DE CONVERSA OBRIGATÓRIO (APÓS O PRIMEIRO CONTACTO): AJUDE, DEPOIS CONVERTA
1.  ESCUTE E RESPONDA: A sua PRIMEIRA AÇÃO deve ser sempre tentar responder à pergunta do lead.
2.  USE A FERRAMENTA `find_answer_in_kb`: Para perguntas sobre jogos, segurança, etc., use esta ferramenta.
3.  FAÇA A PONTE (BRIDGE): SOMENTE APÓS ter respondido, faça a transição para a oferta principal.

# GESTÃO DE FIM DE FLUXO (CONVERSÃO OU RECUSA)
-   SE O LEAD CONFIRMAR O CADASTRO/DEPÓSITO, a sua missão está CUMPRIDA.
    1.  Use a ferramenta `track_lead_status` para mudar o status para `'Funil_CONVERTIDO'`.
    2.  Envie uma mensagem final de parabéns.

-   SE O LEAD PEDIR PARA PARAR, respeite a decisão dele IMEDIATAMENTE.
    1.  Use a ferramenta `track_lead_status` para mudar o status para `'Funil_RECUSADO'`.
    2.  Envie uma mensagem final de confirmação.

# REGRAS DE COMUNICAÇÃO (NÃO-NEGOCIÁVEIS)
1.  O MANTRA DOS 90 CARACTERES: NENHUMA resposta pode ultrapassar 90 caracteres.
2.  LINGUAGEM "PAPO RETO": Use gírias como 'mano', 'parça', 'demorou', 'fechou', 'é a boa'.
3.  FOCO EM AÇÃO (CTA): Termine as mensagens com um gancho para manter a conversa viva.

# CONTEXTO DO LEAD ATUAL (JSON)
{lead_context}
"""

async def get_ai_response(phone_number: str, user_message: str, system_prompt: str, lead_context: dict):
    print("--- Cérebro da IA ativado ---")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_answer_in_kb",
                "description": "Busca na base de conhecimento uma resposta para perguntas gerais do lead sobre jogos, segurança, depósitos, etc.",
                "parameters": {
                    "type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_lead_status",
                "description": "Atualiza o status do lead no funil de conversão (ex: para 'Funil_CONVERTIDO' ou 'Funil_RECUSADO').",
                "parameters": {
                    "type": "object", "properties": { "new_status": {"type": "string"}, "details": {"type": "object"} }, "required": ["new_status", "details"]
                }
            }
        }
    ]

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]

    try:
        response = await openai.chat.completions.create(
            model="gpt-4o", messages=messages, tools=tools, tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "find_answer_in_kb": find_answer_in_kb,
                "track_lead_status": track_lead_status,
            }
            
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == 'track_lead_status':
                function_args.update({
                    'lead_id': lead_context.get('lead_id', 'unknown'),
                    'nome': lead_context.get('nome'),
                    'telefone': phone_number
                })

            function_response = await function_to_call(function_args)

            messages.append(response_message)
            messages.append({
                "tool_call_id": tool_call.id, "role": "tool",
                "name": function_name, "content": function_response,
            })
            
            second_response = await openai.chat.completions.create(model="gpt-4o", messages=messages)
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content

        if final_response:
            await send_whatsapp_message(phone_number, final_response)
        
        # Opcional: Sumariza a conversa após uma interação significativa
        if len(user_message) > 20 and lead_context.get('status') != 'Fase1_ContatoInicial':
            transcript = f"Júnior: {final_response}\n{lead_context['nome']}: {user_message}"
            await summarize_and_save_conversation(phone_number, transcript)

    except Exception as e:
        print(f"ERRO CRÍTICO NO CÉREBRO DA IA: {e}")
        await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")