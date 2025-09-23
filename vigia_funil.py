import pandas as pd
import asyncio
from datetime import datetime
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, parse_tracker_details
from app.core.ai import generate_funnel_message # Importamos a nova função criativa

TRACKER_FILE_PATH = 'data/conversation_tracker.csv'

# MAPEAMENTO FINAL DO FUNIL COM OBJETIVOS PARA A IA (Extraído do vosso funil)
FUNNEL_LOGIC = {
    'Funil_Dia1_ContatoInicial': {
        'dias_para_agir': 4,
        'objetivo_do_dia': "Dia 5 (Consultivo): Lembre o lead {nome} sobre o Torneio PG Soft com R$1,6M em prêmios que já começou e pergunte de forma consultiva se ele quer garantir a vaga.",
        'novo_status': 'Funil_Dia5_TorneioPG'
    },
    'Funil_Dia5_TorneioPG': {
        'dias_para_agir': 3,
        'objetivo_do_dia': "Dia 8 (Urgência): Crie urgência para o lead {nome}, informando que é o último dia do Torneio Diário com R$5.000 em prêmios e pergunte se posso ativar a participação dele agora.",
        'novo_status': 'Funil_Dia8_TorneioDiario'
    },
    'Funil_Dia8_TorneioDiario': {
        'dias_para_agir': 5,
        'objetivo_do_dia': "Dia 13 (Consultivo): De forma amigável, pergunte ao lead {nome} o que ele prefere para começar: Cashback, Torneios ou Giros extras, e diga que pode indicar a melhor opção para ele.",
        'novo_status': 'Funil_Dia13_PerguntaInteresse'
    },
    'Funil_Dia13_PerguntaInteresse': {
        'dias_para_agir': 3,
        'objetivo_do_dia': "Dia 16 (Gatilho): Crie entusiasmo no lead {nome} sobre os R$60.000 em prêmios no Torneio Aviator deste mês e termine com um gatilho de resposta clara (Responda SIM).",
        'novo_status': 'Funil_Dia16_TorneioAviator'
    },
    'Funil_Dia16_TorneioAviator': {
        'dias_para_agir': 4,
        'objetivo_do_dia': "Dia 20 (Final): Use um tom de última chance para o lead {nome}. Informe que as promoções da Bateu Bet estão a encerrar em horas e que depois não há volta.",
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
        if status_atual in FUNNEL_LOGIC:
            last_update = datetime.strptime(row['last_update'], '%Y-%m-%d %H:%M:%S')
            regra = FUNNEL_LOGIC[status_atual]
            dias_desde_update = (now - last_update).days

            if dias_desde_update >= regra['dias_para_agir']:
                nome, telefone, lead_id = row['nome'], row['telefone'], row['lead_id']
                details = parse_tracker_details(row)
                
                nome_tratamento = nome.split()[0]
                objetivo_personalizado = regra['objetivo_do_dia'].format(nome=nome_tratamento)
                
                print(f"AVISO (Vigia): A gerar mensagem para '{nome}' com o objetivo: {regra['novo_status']}...")
                
                mensagem = await generate_funnel_message(objetivo_personalizado)
                
                if mensagem:
                    success = await send_whatsapp_message(telefone, mensagem)
                    if success:
                        await track_lead_status(lead_id, nome, telefone, regra['novo_status'], details)
                        leads_notificados += 1
                else:
                    print(f"ERRO (Vigia): A IA não conseguiu gerar a mensagem para o objetivo: {regra['novo_status']}")
            
    if leads_notificados > 0:
        print(f"--- VIGIA: {leads_notificados} leads avançaram no funil com mensagens geradas por IA. ---")
    else:
        print("--- VIGIA: Nenhum lead precisou de ação neste ciclo. ---")

if __name__ == "__main__":
    asyncio.run(run_funnel_watcher())