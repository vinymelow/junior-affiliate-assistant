import pandas as pd
import asyncio
import random
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status

LEADS_FILE_PATH = 'data/leads.csv'

# --- NOVO TEMPLATE DIA 1 (TORNEIO PRIMAVERA) ---
MESSAGE_TEMPLATE = "Olá {nome_tratamento}, aqui é da Bateu Bet. Quer que eu ative sua inscrição no Torneio da Primavera com R$20.000 em prêmios? Responda SIM."

async def start_campaign():
    """
    Inicia a campanha com a mensagem de gatilho do Dia 1.
    """
    try:
        leads_df = pd.read_csv(LEADS_FILE_PATH)
        leads_df['telefone'] = leads_df['telefone'].astype(str)
    except FileNotFoundError:
        print(f"ERRO: Ficheiro de leads não encontrado em '{LEADS_FILE_PATH}'.")
        return

    print(f"--- Iniciando campanha para {len(leads_df)} leads ---")

    for index, row in leads_df.iterrows():
        lead_id = str(row['lead_id'])
        nome = row['nome']
        telefone = str(row['telefone'])
        
        nome_tratamento = nome.split()[0]
        message = MESSAGE_TEMPLATE.format(nome_tratamento=nome_tratamento)

        print(f"\n--- Preparando para contactar {nome} ({telefone}) ---")

        success = await send_whatsapp_message(telefone, message)
        if success:
            # Atualiza o tracker com o novo status e detalhes da oferta
            await track_lead_status(
                lead_id=lead_id, nome=nome, telefone=telefone,
                new_status='Funil_Dia1_ContatoInicial',
                details={"casa_ofertada": "BateuBet.br", "oferta": "Torneio da Primavera R$20.000"}
            )
            print(f"Lead {nome} contactado. Status inicial 'Funil_Dia1_ContatoInicial' registado.")
        
        delay = random.uniform(15, 30)
        print(f"Aguardando {delay:.2f} segundos antes do próximo envio...")
        await asyncio.sleep(delay)

    print("\n--- Campanha finalizada para todos os leads. ---")

if __name__ == '__main__':
    asyncio.run(start_campaign())