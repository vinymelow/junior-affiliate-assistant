import pandas as pd
import asyncio
from datetime import datetime
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, parse_tracker_details

TRACKER_FILE_PATH = 'data/conversation_tracker.csv'

FUNNEL_LOGIC = {
    'Funil_Dia1_ContatoInicial': {
        'dias_para_agir': 4,
        'nova_mensagem': "Lembrete: o Torneio PG Soft com R$1,6M em prêmios já começou 🏆. Quer que eu garanta sua vaga agora?",
        'novo_status': 'Funil_Dia5_TorneioPG'
    },
    'Funil_Dia5_TorneioPG': {
        'dias_para_agir': 3,
        'nova_mensagem': "⚡ Último dia do Torneio Diário com R$5.000 em prêmios. Posso ativar sua participação agora?",
        'novo_status': 'Funil_Dia8_TorneioDiario'
    },
    'Funil_Dia8_TorneioDiario': {
        'dias_para_agir': 5,
        'nova_mensagem': "{nome}, você prefere começar com Cashback 🎲, Torneios 🏆 ou Giros extras 🔄? Posso indicar o melhor pra você.",
        'novo_status': 'Funil_Dia13_PerguntaInteresse'
    },
    'Funil_Dia13_PerguntaInteresse': {
        'dias_para_agir': 3,
        'nova_mensagem': "✈️ R$60.000 em prêmios no Torneio Aviator esse mês! Quer que eu ative sua inscrição agora? Responda SIM.",
        'novo_status': 'Funil_Dia16_TorneioAviator'
    },
    'Funil_Dia16_TorneioAviator': {
        'dias_para_agir': 4,
        'nova_mensagem': "⚠️ Promoções Bateu Bet encerrando em horas. Depois não há volta! Quer ativar já e garantir sua chance?",
        'novo_status': 'Funil_Dia20_UltimaChance'
    }
}

async def run_funnel_watcher():
    try:
        tracker_df = pd.read_csv(TRACKER_FILE_PATH, dtype={'telefone': str})
    except FileNotFoundError:
        print("INFO (Vigia): Ficheiro de rastreamento ainda não existe.")
        return

    print(f"\n--- VIGIA DO FUNIL (Executado em {datetime.now()}) ---")
    
    leads_notificados = 0
    now = datetime.now()

    for index, row in tracker_df.iterrows():
        status_atual = row['status']
        last_update = datetime.strptime(row['last_update'], '%Y-%m-%d %H:%M:%S')
        
        if status_atual in FUNNEL_LOGIC:
            regra = FUNNEL_LOGIC[status_atual]
            dias_desde_update = (now - last_update).days

            if dias_desde_update >= regra['dias_para_agir']:
                nome = row['nome']
                telefone = row['telefone']
                lead_id = row['lead_id']
                details = parse_tracker_details(row)
                
                nome_tratamento = nome.split()[0]
                mensagem = regra['nova_mensagem'].format(nome=nome_tratamento)
                
                print(f"AVISO (Vigia): Lead '{nome}' atingiu a condição para '{regra['novo_status']}'. Enviando mensagem...")
                
                success = await send_whatsapp_message(telefone, mensagem)
                
                if success:
                    await track_lead_status(lead_id, nome, telefone, regra['novo_status'], details)
                    leads_notificados += 1
            
    if leads_notificados > 0:
        print(f"--- VIGIA: {leads_notificados} leads avançaram no funil de WhatsApp. ---")
    else:
        print("--- VIGIA: Nenhum lead precisou de ação de WhatsApp neste ciclo. ---")

if __name__ == "__main__":
    asyncio.run(run_funnel_watcher())