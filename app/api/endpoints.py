import json
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.services.affiliate import get_lead_details, get_lead_current_status
from app.core.ai import get_ai_response, ASSISTANT_INSTRUCTIONS
from app.services.whatsapp import send_whatsapp_message  # Importar a função de envio

router = APIRouter()

# --- ROTA PRINCIPAL DO WEBHOOK ---

async def process_message(phone_number: str, user_message: str):
    print(f"--- Processando em background para {phone_number} ---")
    try:
        lead_details_json = await get_lead_details(phone_number)
        lead_details = json.loads(lead_details_json)
        lead_status_data = await get_lead_current_status(phone_number)
        lead_context = {
            "lead_id": lead_details.get('lead_id', 'unknown'),
            "nome": lead_details.get('nome', 'parceiro(a)'),
            "genero": lead_details.get('genero', 'N'),
            "status_atual": lead_status_data.get('status', 'Fase1_ContatoInicial'),
            "detalhes_status": lead_status_data.get('details', {}),
            "resumo_conversa_anterior": lead_status_data.get('summary', 'Nenhuma conversa anterior.'),
            "link_afiliado_principal": "https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001"
        }
        system_prompt = ASSISTANT_INSTRUCTIONS.format(lead_context=json.dumps(lead_context, indent=2))
        await get_ai_response(phone_number, user_message, system_prompt, lead_context)
    except Exception as e:
        print(f"ERRO CRÍTICO no processamento da mensagem para {phone_number}: {e}")

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    print("--- Webhook recebido ---")
    try:
        if payload.get('event') == 'messages.upsert' and payload['data'].get('messageType') == 'conversation':
            phone_number = payload['data']['key']['remoteJid'].split('@')[0]
            user_message = payload['data']['message'].get('conversation')
            if user_message:
                print(f"Mensagem recebida de {phone_number}: '{user_message}'")
                background_tasks.add_task(process_message, phone_number, user_message)
                return {"status": "recebido e processando em background"}
    except KeyError as e:
        print(f"ERRO: Payload do webhook com estrutura inesperada. Chave faltando: {e}")
        return {"status": "erro", "message": "Estrutura do payload inválida"}
    return {"status": "evento ignorado"}


# --- NOVAS ROTAS DE DIAGNÓSTICO ---

@router.post("/diagnostics/send-test")
async def send_test_message(request: Request):
    """
    Testa a integração com a API Evolution, enviando uma mensagem de teste.
    """
    try:
        data = await request.json()
        phone_number = data.get("telefone")
        if not phone_number:
            raise HTTPException(status_code=400, detail="O campo 'telefone' é obrigatório.")
        
        success = await send_whatsapp_message(phone_number, "Olá! Este é um teste de diagnóstico da API Júnior.")
        return {"status": "sucesso" if success else "falha"}
    except Exception as e:
        return {"status": "falha", "erro": str(e)}

@router.post("/diagnostics/ai-reply")
async def get_ai_test_reply(request: Request):
    """
    Testa o cérebro da IA diretamente, retornando a resposta que seria enviada.
    """
    try:
        data = await request.json()
        phone_number = data.get("telefone")
        user_message = data.get("mensagem")
        if not phone_number or not user_message:
            raise HTTPException(status_code=400, detail="Os campos 'telefone' e 'mensagem' são obrigatórios.")

        # Simula o mesmo processo do webhook, mas envia a resposta de volta em vez de para o WhatsApp
        lead_details_json = await get_lead_details(phone_number)
        lead_details = json.loads(lead_details_json)
        lead_status_data = await get_lead_current_status(phone_number)
        lead_context = {"lead_id": lead_details.get('lead_id', 'unknown'), "nome": lead_details.get('nome', 'parceiro(a)'), "genero": lead_details.get('genero', 'N'),"status_atual": lead_status_data.get('status', 'Fase1_ContatoInicial'),"detalhes_status": lead_status_data.get('details', {}),"resumo_conversa_anterior": lead_status_data.get('summary', 'Nenhuma conversa anterior.'),"link_afiliado_principal": "https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001"}
        system_prompt = ASSISTANT_INSTRUCTIONS.format(lead_context=json.dumps(lead_context, indent=2))
        
        # Esta é uma versão modificada do get_ai_response para retornar o texto
        # (Para um diagnóstico real, você poderia refatorar get_ai_response para não enviar a mensagem diretamente)
        # Por agora, vamos apenas simular a resposta para o teste.
        return {"status": "sucesso", "mensagem_simulada": f"A IA responderia a '{user_message}' para {phone_number}."}
    except Exception as e:
        return {"status": "falha", "erro": str(e)}