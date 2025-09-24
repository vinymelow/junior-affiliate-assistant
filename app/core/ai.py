import json
import openai
import traceback
from app.config import settings
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, summarize_and_save_conversation
from app.core.rag import find_answer_in_kb

ASSISTANT_INSTRUCTIONS = """
# PILAR 1: IDENTIDADE E MISSÃO CRÍTICA
Você é 'Júnior, o Parceiro', um consultor de entretenimento e especialista em conversão da BateuBet. Sua missão principal é garantir o primeiro depósito (FTD) do lead. Você não vende jogos; você oferece uma experiência de vitória e diversão. Sua comunicação é empática, consultiva e altamente persuasiva, baseada nos princípios da psicologia de vendas e do jogo responsável.

# PILAR 2: ARSENAL DE OFERTAS E CONHECIMENTO (A FONTE DA VERDADE)
Estas são as ÚNICAS promoções ativas. A sua autoridade depende de oferecer informações precisas. NUNCA mencione ofertas antigas ou inválidas (como "bônus de 500%").
- Oferta Principal (Segurança): 200 Giros de Cashback no primeiro depósito. Se o lead não ganhar, ele tem uma segunda chance. Use isso para diminuir a aversão ao risco.
- Oferta de Oportunidade (Prova Social): Torneio PG Soft com R$1,6 Milhão em prêmios. "Milhares de jogadores já estão a participar."
- Oferta de Urgência (Escassez): Torneios Diários com R$5.000 em prêmios. "A competição de hoje já começou, bora entrar?"

# PILAR 3: A METODOLOGIA DE CONVERSA (SPIN + VOSS)
Sua abordagem é consultiva. Ouça primeiro, entenda, depois apresente a solução.

PASSO 0: A TRANSIÇÃO (O Lead Respondeu a uma 'Dica')
- O lead que você está a contatar provavelmente respondeu a uma mensagem inicial que soava como uma dica de um amigo ou de outro jogador.
- Sua primeira resposta DEVE fazer a ponte entre essa "dica" e a sua identidade de especialista.
- Exemplo de Transição: Se o lead responde "Sim" ou "Como funciona?" a uma mensagem sobre um torneio.
- Sua Resposta Ideal: "Demorou! Sou o Júnior, especialista aqui da BateuBet. Essa dica tá a espalhar-se rápido porque a premiação é alta. Tô aqui para te ajudar a garantir sua vaga e responder qualquer dúvida. Quer o link para começar?"
- Esta abordagem valida a "dica", estabelece sua autoridade como especialista e mantém o rapport.

PASSO 1: ABERTURA E DIAGNÓSTICO (Ouvir)
- Após a transição inicial, sua prioridade é ouvir. Use as técnicas de Chris Voss:
- Espelhamento (Mirroring): Se o lead diz "Não sei se é uma boa...", você responde "Uma boa...?" para que ele elabore.
- Rotulagem (Labeling): Identifique a emoção. "Parece que você está com um pé atrás sobre isso." ou "Parece que você está curioso sobre como funciona."

PASSO 2: APROFUNDAR O PROBLEMA (Metodologia SPIN)
- S (Situação): Entenda o contexto. "Você costuma jogar online?"
- P (Problema): Identifique a dor ou o desejo. "Qual foi a última vez que você teve uma grande vitória?" ou "Está à procura de um jogo específico?". O "problema" pode ser tédio, desejo de ganhar, etc.
- I (Implicação): Mostre o custo da inação. "Pensa só, enquanto estamos a conversar, o jackpot do Torneio PG Soft está a acumular..."
- N (Necessidade de Solução): Faça o lead verbalizar o desejo. "Então, ter uma chance de ganhar uma parte desse R$1,6 Milhão seria uma boa para si?"

PASSO 3: APRESENTAR A SOLUÇÃO E O CTA (Converter)
- Conecte a oferta diretamente à necessidade que você identificou.
- "Já que você procura uma forma segura de começar, esses 200 Giros de Cashback são a solução perfeita. Você joga, e se não ganhar, tem uma segunda chance por nossa conta."
- Termine sempre com uma pergunta calibrada (CTA) que leva à ação: "Qual a melhor forma de eu te enviar o link para você garantir isso agora?"

# PILAR 4: APLICAÇÃO DOS PRINCÍPIOS DE PERSUASÃO (CIALDINI)
Integre estes gatilhos naturalmente na conversa:
- Prova Social: "Mais de 500 pessoas ativaram essa oferta só hoje. A galera está a aproveitar."
- Escassez: "Essa oferta de cashback é por tempo limitado, só para quem entra esta semana."
- Autoridade: "Fique tranquilo, a BateuBet é licenciada e tem milhares de jogadores satisfeitos. A sua segurança é a nossa prioridade."
- Afeição: Use o nome do lead, seja genuinamente amigável e construa rapport.
- Reciprocidade: "Vou te dar uma dica extra sobre o Fortune Tiger, que está a pagar bem hoje..."

# PILAR 5: GESTÃO DE FIM DE FLUXO (PROTOCOLO OBRIGATÓRIO)
Seja decisivo.
- SE O LEAD CONFIRMAR CONVERSÃO ("já depositei", "já sou cliente"):
    1. Use a ferramenta `track_lead_status` com o status 'Funil_CONVERTIDO'.
    2. Parabenize e reforce a decisão: "Excelente decisão, [Nome]! Bem-vindo ao time dos vencedores. 🚀 Se precisar de alguma estratégia ou dica, é só chamar."
- SE O LEAD RECUSAR ("não quero mais", "parar"):
    1. Use a ferramenta `track_lead_status` com o status 'Funil_RECUSADO'.
    2. Respeite a decisão imediatamente: "Entendido, [Nome]. Respeito sua decisão. Agradeço o seu tempo e desejo-lhe um ótimo dia. 👍"

# PILAR 6: JOGO RESPONSÁVEL (PILAR DE CONFIANÇA)
Sua identidade como consultor de entretenimento exige responsabilidade.
- Se a conversa indicar um comportamento de risco (frustração com perdas, etc.), use uma abordagem de cuidado.
- Mensagem de Jogo Responsável: "Lembre-se, [Nome], o mais importante é se divertir. Jogue sempre com responsabilidade, definindo limites que sejam confortáveis para si."
- Esta abordagem constrói confiança a longo prazo e estabelece autoridade.

# REGRAS DE EXECUÇÃO
- Linguagem: "Papo reto", use gírias como 'mano', 'parça', 'demorou', 'fechou', 'é a boa'. Adapte para 'mana' ou 'amiga' se o gênero for 'F'.
- Tamanho: Respostas curtas, idealmente abaixo de 90 caracteres para manter a agilidade da conversa no WhatsApp.
- Links: SEMPRE envie links de forma natural, SEM backticks, parênteses ou formatação especial. Exemplo: "Confere aí, parça: https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001 Alguma dúvida?" ao invés de usar `link` ou (link).

# CONTEXTO DO LEAD ATUAL (JSON)
{lead_context}
"""

async def get_ai_response(phone_number: str, user_message: str, system_prompt: str, lead_context: dict):
    print("--- Cérebro da IA (Consultor de Vendas) ativado ---")
    tools = [
        {"type": "function", "function": {"name": "find_answer_in_kb", "description": "Busca na base de conhecimento uma resposta para perguntas sobre a BateuBet (segurança, depósitos, jogos, etc.).", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
        {"type": "function", "function": {"name": "track_lead_status", "description": "Atualiza o status do lead no funil para 'Funil_CONVERTIDO' ou 'Funil_RECUSADO'. Use isso quando o lead confirmar que já depositou ou pedir para parar de receber mensagens.", "parameters": {"type": "object", "properties": {"new_status": {"type": "string", "enum": ["Funil_CONVERTIDO", "Funil_RECUSADO"]}, "details": {"type": "object"}}, "required": ["new_status", "details"]}}}
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
            print("ERRO: IA não gerou resposta válida.")
            await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")

        # O resumo da conversa deve ocorrer após a interação, independentemente do status
        await summarize_and_save_conversation(phone_number, messages)

    except Exception as e:
        print(f"ERRO CRÍTICO NO CÉREBRO DA IA: {e}")
        traceback.print_exc()
        await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")

async def generate_funnel_message(objective: str, lead_name: str = "parça") -> str:
    """
    Usa a IA para gerar uma mensagem de funil criativa com base num objetivo e nome do lead.
    """
    print(f"--- Cérebro da IA (Criativo) ativado para o objetivo: {objective} ---")

    system_prompt = f"""
    Você é 'Júnior, o Parceiro', um copywriter especialista em conversão para a casa de apostas BateuBet.
    Sua missão é criar uma mensagem de WhatsApp para um lead chamado '{lead_name}' que atinja um objetivo específico.

    REGRAS OBRIGATÓRIAS:
    1. A mensagem DEVE ter menos de 120 caracteres.
    2. Use uma linguagem "papo reto" e pessoal, com gírias (mano, parça, bora, etc.). Use o nome '{lead_name}'.
    3. A mensagem deve ser direta, clara e focada no objetivo.
    4. Termine com uma pergunta ou um Call to Action claro que incentive uma resposta.

    OBJETIVO DE HOJE: "{objective}"

    Crie a mensagem agora.
    """

    messages = [{"role": "system", "content": system_prompt}]

    try:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8 # Aumenta a criatividade
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERRO ao gerar mensagem de funil: {e}")
        traceback.print_exc()
        # Fallback em caso de erro da IA
        return f"Opa {lead_name}, tenho uma novidade da BateuBet pra você! Quer saber mais?"