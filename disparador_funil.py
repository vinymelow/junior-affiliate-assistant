import pandas as pd
import asyncio
import random
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status

LEADS_FILE_PATH = 'data/leads.csv'

# --- NOVA MENSAGEM PÓS-LIGAÇÃO ---
MESSAGE_TEMPLATE = """Fala, {nome_tratamento}! To de volta aqui no WhatsApp, é o Júnior que te ligou agora pouco.

Mano, aqui tá a promoção que eu tenho certeza que tu vai curtir: são **30 giros de graça no Gates of Olympus** depositando qualquer valor, além de concorrer a **5 mil em prêmios todos os dias** na BateuBet.

Clica aqui pra não ficar de fora: {link_afiliado}"""

async def start_campaign():
    """
    Inicia a campanha com uma mensagem de follow-up pós-ligação.
    """
    try:
        leads_df = pd.read_csv(LEADS_FILE_PATH)
        leads_df['telefone'] = leads_df['telefone'].astype(str)
    except FileNotFoundError:
        print(f"ERRO: Ficheiro de leads não encontrado em '{LEADS_FILE_PATH}'.")
        return

    print(f"--- Iniciando campanha PÓS-LIGAÇÃO para {len(leads_df)} leads ---")

    # Link único para esta campanha
    link_da_casa = "https://SEU-LINK-AFILIADO.com/bateubet" # Coloque o link real aqui

    for index, row in leads_df.iterrows():
        lead_id = str(row['lead_id'])
        nome = row['nome']
        telefone = str(row['telefone'])
        
        nome_tratamento = nome.split()[0]
        message = MESSAGE_TEMPLATE.format(nome_tratamento=nome_tratamento, link_afiliado=link_da_casa)

        print(f"\n--- Preparando para contactar {nome} ({telefone}) ---")

        success = await send_whatsapp_message(telefone, message)
        if success:
            await track_lead_status(
                lead_id=lead_id, nome=nome, telefone=telefone,
                new_status='Fase1_ContatoPosLigacao_LinkEnviado',
                details={"casa_ofertada": "BateuBet.br", "oferta": "30 Giros Grátis Gates of Olympus"}
            )
            print(f"Lead {nome} contactado. Status inicial 'Fase1_ContatoPosLigacao_LinkEnviado' registado.")
        
        delay = random.uniform(15, 30)
        print(f"Aguardando {delay:.2f} segundos antes do próximo envio...")
        await asyncio.sleep(delay)

    print("\n--- Campanha finalizada para todos os leads. ---")

if __name__ == '__main__':
    asyncio.run(start_campaign())