import json
from fastapi import APIRouter, Request, BackgroundTasks
from app.services.affiliate import get_lead_details, get_lead_current_status
from app.core.ai import get_ai_response, ASSISTANT_INSTRUCTIONS

router = APIRouter()

async def process_message(phone_number: str, user_message: str):
    """
    Processa a mensagem em background para não bloquear a resposta ao webhook.
    """
    print(f"--- Processando em background para {phone_number} ---")
    
    # --- PASSO 1: BUSCAR OS DETALHES DO LEAD (onde 'lead_details' é definido) ---
    lead_details_json = await get_lead_details(phone_number)
    lead_details = json.loads(lead_details_json)

    # --- PASSO 2: EXTRAIR O NOME DO LEAD (onde 'nome_lead' é definido) ---
    nome_lead = lead_details.get('nome', 'parceiro(a)')
    if 'error' in lead_details:
        print(f"AVISO: Ocorreu um erro ao buscar detalhes do lead: {lead_details['error']}")

    # --- PASSO 3: BUSCAR O STATUS ATUAL ---
    lead_status = await get_lead_current_status(phone_number)

    # --- PASSO 4: ADICIONAR O LINK DE AFILIADO AO CONTEXTO ---
    affiliate_link = lead_status.get('details', {}).get('link_afiliado', 'https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001')

    # --- PASSO 5: MONTAR O CONTEXTO COMPLETO PARA A IA ---
    lead_context = {
        "nome": nome_lead,
        "genero": lead_details.get('genero', 'N'),
        "status_atual": lead_status.get('status', 'Nenhum'),
        "detalhes_status": lead_status.get('details', {}),
        "resumo_conversa_anterior": lead_status.get('summary', 'Nenhuma conversa anterior.'),
        "link_afiliado_principal": affiliate_link
    }

    system_prompt = ASSISTANT_INSTRUCTIONS.format(lead_context=json.dumps(lead_context, indent=2))
    
    await get_ai_response(phone_number, user_message, system_prompt, lead_context)


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    print("--- Webhook recebido ---")
    
    try:
        if payload.get('event') == 'messages.upsert' and payload['data'].get('messageType') == 'conversation':
            # --- CORREÇÃO APLICADA AQUI ---
            # Removemos a lógica que cortava o número de telefone.
            # Agora ele funciona para qualquer país.
            phone_number = payload['data']['key']['remoteJid'].split('@')[0]
            user_message = payload['data']['message']['conversation']
            
            print(f"Mensagem recebida de {phone_number}: '{user_message}'")
            background_tasks.add_task(process_message, phone_number, user_message)
            
            return {"status": "recebido e processando em background"}

    except KeyError as e:
        print(f"ERRO: Payload do webhook com estrutura inesperada. Chave faltando: {e}")
        return {"status": "erro", "message": "Estrutura do payload inválida"}
    
    return {"status": "evento ignorado"}