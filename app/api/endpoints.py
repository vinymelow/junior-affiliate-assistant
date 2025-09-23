import json
from fastapi import APIRouter, Request, BackgroundTasks
from app.services.affiliate import get_lead_details, get_lead_current_status
from app.core.ai import get_ai_response, ASSISTANT_INSTRUCTIONS
from app.core.funnel_orchestrator import funnel_orchestrator
from app.services.whatsapp import send_whatsapp_message

router = APIRouter()

async def process_message(phone_number: str, user_message: str):
    print(f"--- Processando em background para {phone_number} ---")
    
    try:
        lead_details_json = await get_lead_details(phone_number)
        lead_details = json.loads(lead_details_json)

        nome_lead = lead_details.get('nome', 'parceiro(a)')
        if 'error' in lead_details:
            print(f"AVISO: Ocorreu um erro ao buscar detalhes do lead: {lead_details['error']}")

        lead_status = await get_lead_current_status(phone_number)

        affiliate_link = lead_status.get('details', {}).get('link_afiliado', 'https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001')

        lead_context = {
            "nome": nome_lead,
            "genero": lead_details.get('genero', 'N'),
            "cidade": lead_details.get('cidade', 'N/A'),
            "status_atual": lead_status.get('status', 'Nenhum'),
            "detalhes_status": lead_status.get('details', {}),
            "resumo_conversa_anterior": lead_status.get('summary', 'Nenhuma conversa anterior.'),
            "link_afiliado_principal": affiliate_link
        }

        # 🎯 NOVA LÓGICA: Verifica se deve usar o orquestrador de funil
        funnel_message = await funnel_orchestrator.process_funnel_interaction(
            phone_number, user_message, lead_context
        )
        
        if funnel_message:
            # Envia mensagem específica do funil
            print(f"🎯 Enviando mensagem do funil: {funnel_message}")
            await send_whatsapp_message(phone_number, funnel_message)
        else:
            # Usa a IA normal para responder
            system_prompt = ASSISTANT_INSTRUCTIONS.format(lead_context=json.dumps(lead_context, indent=2))
            print(f"System prompt preparado para {phone_number}")
            
            await get_ai_response(phone_number, user_message, system_prompt, lead_context)
        
    except Exception as e:
        print(f"ERRO CRÍTICO no processamento da mensagem para {phone_number}: {e}")
        import traceback
        traceback.print_exc()
        # Enviar mensagem de erro para o usuário
        await send_whatsapp_message(phone_number, "Opa, mano, deu um bug aqui no meu sistema. Pode repetir, por favor?")


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    print("--- Webhook recebido ---")
    
    try:
        if payload.get('event') == 'messages.upsert' and payload['data'].get('messageType') == 'conversation':
            phone_number = payload['data']['key']['remoteJid'].split('@')[0]
            user_message = payload['data']['message']['conversation']
            
            print(f"Mensagem recebida de {phone_number}: '{user_message}'")
            background_tasks.add_task(process_message, phone_number, user_message)
            
            return {"status": "recebido e processando em background"}

    except KeyError as e:
        print(f"ERRO: Payload do webhook com estrutura inesperada. Chave faltando: {e}")
        return {"status": "erro", "message": "Estrutura do payload inválida"}
    
    return {"status": "evento ignorado"}

@router.post("/test/message")
async def test_message(request: Request, background_tasks: BackgroundTasks):
    """🧪 Endpoint para testar mensagens diretamente (formato simplificado)"""
    try:
        # Recebe dados do teste com encoding correto
        body_bytes = await request.body()
        body_text = body_bytes.decode('utf-8')
        payload = json.loads(body_text)
        
        print("--- Teste de mensagem recebido ---")
        
        phone_number = payload.get('from')
        user_message = payload.get('body')
        
        if not phone_number or not user_message:
            return {"status": "erro", "message": "Campos 'from' e 'body' são obrigatórios"}
        
        print(f"Teste - Mensagem recebida de {phone_number}: '{user_message}'")
        background_tasks.add_task(process_message, phone_number, user_message)
        
        return {"status": "recebido e processando em background"}

    except Exception as e:
        print(f"ERRO no teste de mensagem: {e}")
        return {"status": "erro", "message": str(e)}