import pandas as pd
import asyncio
from datetime import datetime
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, parse_tracker_details

TRACKER_FILE_PATH = 'data/conversation_tracker.csv'

async def run_funnel_watcher():
    try:
        tracker_df = pd.read_csv(TRACKER_FILE_PATH)
        tracker_df['telefone'] = tracker_df['telefone'].astype(str)
    except FileNotFoundError:
        print("INFO (Vigia): Ficheiro de rastreamento ainda não existe.")
        return

    print(f"\n--- VIGIA DO FUNIL (Executado em {datetime.now()}) ---")
    
    leads_notificados = 0
    now = datetime.now()

    for index, row in tracker_df.iterrows():
        status = row['status']
        last_update = datetime.strptime(row['last_update'], '%Y-%m-%d %H:%M:%S')
        details = parse_tracker_details(row)
        
        # --- LÓGICA DO FUNIL (DIA 2): REFORÇO DA EXPERIÊNCIA ---
        if status == 'Fase1_LinkEnviado' and (now - last_update).days >= 1:
            nome = row['nome']
            telefone = row['telefone']
            oferta = details.get('oferta', 'suas rodadas grátis')
            
            mensagem = f"{nome.split()[0]}, suas {oferta} expiram em 24h! Não perca a chance de ganhar sem gastar. 🚀"
            
            print(f"AVISO: {nome} não usou a oferta inicial. Enviando lembrete de urgência...")
            success = await send_whatsapp_message(telefone, mensagem)
            if success:
                await track_lead_status(row['lead_id'], nome, telefone, 'Fase1_LembreteEnviado', details)
                leads_notificados += 1

        # --- LÓGICA DO FUNIL (DIA 6): OFERTA DE R$1 PARA EXPLORADORES ---
        if status == 'Fase1_JogouGratis' and (now - last_update).days >= 1:
            nome = row['nome']
            telefone = row['telefone']
            casa = details.get('casa_ofertada', 'a nossa casa')
            
            mensagem = f"E aí, {nome.split()[0]}! Vi que você curtiu as rodadas grátis na {casa}. Que tal jogar pra valer? Só pra você, deposite apenas R$1 e a gente te dá R$6 para jogar! 🤑"
            
            print(f"AVISO: {nome} é um 'Explorador'. Enviando oferta de R$1...")
            success = await send_whatsapp_message(telefone, mensagem)
            if success:
                await track_lead_status(row['lead_id'], nome, telefone, 'Fase2_OfertaR1_Enviada', details)
                leads_notificados += 1
            
    if leads_notificados > 0:
        print(f"--- VIGIA: {leads_notificados} leads avançaram no funil. ---")
    else:
        print("--- VIGIA: Nenhum lead precisou de ação neste ciclo. ---")

if __name__ == "__main__":
    asyncio.run(run_funnel_watcher())