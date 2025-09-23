import json
import openai
import traceback
from app.config import settings
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, summarize_and_save_conversation
from app.core.rag import find_answer_in_kb

# Removida configuração obsoleta: openai.api_key (incompatível com AsyncOpenAI)

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

# GESTÃO DE FIM DE FLUXO (CONVERSÃO OU RECUSA) - PROTOCOLO OBRIGATÓRIO
-   SE O LEAD CONFIRMAR O CADASTRO/DEPÓSITO (palavras-chave: "já cadastrei", "já me cadastrei", "já fiz o cadastro", "já depositei", "já apostei", "já sou cliente", "já tenho conta"):
    1.  Use a ferramenta `track_lead_status` para mudar o status para `'Funil_CONVERTIDO'`.
    2.  Envie uma mensagem final: "Demais, mano! Parabéns pela decisão! Agora é só lucrar! 🚀"
    3.  PARE DE ENVIAR MENSAGENS DO FUNIL.

-   SE O LEAD PEDIR PARA PARAR (palavras-chave: "não quero mais", "para de mandar", "não me mande mais", "sair da lista", "não tenho interesse", "me tira daqui"):
    1.  Use a ferramenta `track_lead_status` para mudar o status para `'Funil_RECUSADO'`.
    2.  Envie uma mensagem final: "Tranquilo, parça! Respeitamos sua decisão. Valeu pelo papo! 👍"
    3.  PARE DE ENVIAR MENSAGENS DO FUNIL.

-   IMPORTANTE: Analise SEMPRE a mensagem do lead em busca dessas palavras-chave antes de responder.

# REGRAS DE COMUNICAÇÃO (NÃO-NEGOCIÁVEIS)
1.  O MANTRA DOS 90 CARACTERES: NENHUMA resposta pode ultrapassar 90 caracteres.
2.  LINGUAGEM "PAPO RETO": Use gírias como 'mano', 'parça', 'demorou', 'fechou', 'é a boa'.
3.  FOCO EM AÇÃO (CTA): Termine as mensagens com um gancho para manter a conversa viva.

# CONTEXTO DO LEAD ATUAL (JSON)
{lead_context}
"""

async def get_ai_response(phone_number: str, user_message: str, system_prompt: str, lead_context: dict):
    print("--- Cérebro da IA (Reativo) ativado ---")
    tools = [
        {"type": "function", "function": {"name": "find_answer_in_kb", "description": "Busca na base de conhecimento uma resposta para perguntas sobre a BateuBet.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
        {"type": "function", "function": {"name": "track_lead_status", "description": "Atualiza o status do lead no funil.", "parameters": {"type": "object", "properties": {"new_status": {"type": "string"}, "details": {"type": "object"}}, "required": ["new_status", "details"]}}}
    ]
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
    try:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(model="gpt-4o", messages=messages, tools=tools, tool_choice="auto")
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            messages.append(response_message)
            available_functions = {"find_answer_in_kb": find_answer_in_kb, "track_lead_status": track_lead_status}
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                if function_name == 'track_lead_status':
                    function_args.update({
                        'lead_id': lead_context.get('lead_id', 'unknown'), 
                        'nome': lead_context.get('nome'), 
                        'telefone': phone_number
                    })
                    # Garantir que details sempre existe
                    if 'details' not in function_args:
                        function_args['details'] = {}
                function_response = await function_to_call(**function_args)
                messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": json.dumps(function_response)})
            second_response = await client.chat.completions.create(model="gpt-4o", messages=messages)
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content
        if final_response:
            print(f"IA gerou resposta: {final_response}")
            await send_whatsapp_message(phone_number, final_response)
        else:
            print("ERRO: IA não gerou resposta válida")
            await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")
        if lead_context.get('status_atual') != 'Fase1_ContatoInicial':
             await summarize_and_save_conversation(phone_number, messages)
    except Exception as e:
        print(f"ERRO CRÍTICO NO CÉREBRO DA IA: {e}")
        traceback.print_exc()
        await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")

# --- NOVA FUNÇÃO CRIATIVA PARA O FUNIL ---
async def generate_funnel_message(objective: str) -> str:
    """
    Usa a IA para gerar uma mensagem de funil criativa com base num objetivo.
    """
    print(f"--- Cérebro da IA (Criativo) ativado para o objetivo: {objective} ---")
    
    system_prompt = f"""
    Você é 'Júnior, o Parceiro', um copywriter especialista em conversão para a casa de apostas BateuBet.
    Sua missão é criar uma mensagem de WhatsApp para atingir um objetivo específico.

    REGRAS OBRIGATÓRIAS:
    1. A mensagem DEVE ter menos de 120 caracteres.
    2. Use uma linguagem "papo reto" e pessoal, com gírias (mano, parça, bora, etc.).
    3. A mensagem deve ser direta, clara e focada no objetivo.
    4. Termine com uma pergunta ou um Call to Action claro.

    OBJETIVO DE HOJE: "{objective}"

    Crie a mensagem agora.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    
    try:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7 # Aumenta a criatividade
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERRO ao gerar mensagem de funil: {e}")
        traceback.print_exc()
        return None