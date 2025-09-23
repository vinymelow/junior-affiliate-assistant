import pandas as pd
import asyncio
import random
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status

LEADS_FILE_PATH = 'data/leads.csv'

MESSAGE_TEMPLATE = "{saudacao_genero}, aqui é da Bateu Bet 🌸. Quer que eu ative sua inscrição no Torneio da Primavera com R$20.000 em prêmios? Responda SIM."

async def start_campaign():
    try:
        leads_df = pd.read_csv(LEADS_FILE_PATH, dtype={'telefone': str, 'lead_id': str})
    except FileNotFoundError:
        print(f"ERRO: Ficheiro de leads não encontrado em '{LEADS_FILE_PATH}'.")
        return

    print(f"--- Iniciando campanha para {len(leads_df)} leads ---")

    for index, row in leads_df.iterrows():
        genero = row.get('genero', 'M')
        nome_tratamento = row['nome'].split()[0]
        
        saudacao = f"Fala, {nome_tratamento}" if genero == 'M' else f"Olá, {nome_tratamento}"
        
        message = MESSAGE_TEMPLATE.format(saudacao_genero=saudacao)

        success = await send_whatsapp_message(row['telefone'], message)
        if success:
            await track_lead_status(
                lead_id=str(row['lead_id']),
                nome=row['nome'],
                telefone=row['telefone'],
                new_status='Funil_Dia1_ContatoInicial',
                details={
                    "casa_ofertada": "BateuBet.br", 
                    "oferta": "Torneio da Primavera R$20.000",
                    "genero": genero,
                    "cidade": row.get('cidade', 'N/A')
                }
            )
            print(f"Lead {row['nome']} contactado. Status e dados de personalização registados.")
        
        delay = random.uniform(15, 30)
        print(f"Aguardando {delay:.2f} segundos antes do próximo envio...")
        await asyncio.sleep(delay)

    print("\n--- Campanha finalizada para todos os leads. ---")

if __name__ == '__main__':
    asyncio.run(start_campaign())