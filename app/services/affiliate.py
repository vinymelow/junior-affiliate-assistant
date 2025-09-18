import pandas as pd
import json
from datetime import datetime
from app.core.rag import rag_system
import ast
import openai

LEADS_FILE_PATH = 'data/leads.csv'
TRACKER_FILE_PATH = 'data/conversation_tracker.csv'

def parse_tracker_details(row):
    """Função auxiliar para converter a coluna 'details' de string para dict."""
    details_str = row.get('details', '{}')
    try:
        return ast.literal_eval(details_str) if isinstance(details_str, str) else details_str
    except (ValueError, SyntaxError):
        return {}


async def get_lead_details(phone_number: str) -> str:
    try:
        leads_df = pd.read_csv(LEADS_FILE_PATH, dtype={'telefone': str})
        lead_info = leads_df[leads_df['telefone'] == phone_number]
        if not lead_info.empty:
            return json.dumps({
                "nome": lead_info.iloc[0]['nome'], "genero": lead_info.iloc[0]['genero'].upper(),
                "lead_id": str(lead_info.iloc[0]['lead_id'])
            })
        return json.dumps({"nome": "parceiro(a)", "genero": "N", "lead_id": "unknown"})
    except Exception as e:
        return json.dumps({"error": f"Erro ao ler leads: {e}"})


async def get_lead_current_status(phone_number: str) -> dict:
    try:
        tracker_df = pd.read_csv(TRACKER_FILE_PATH, dtype={'telefone': str})
        lead_status = tracker_df[tracker_df['telefone'] == phone_number]
        if not lead_status.empty:
            last_entry = lead_status.iloc[-1]
            details_dict = parse_tracker_details(last_entry)
            return {"status": last_entry['status'], "details": details_dict, "summary": last_entry.get('summary', '')}
    except FileNotFoundError:
        pass
    return {"status": "Fase1_ContatoInicial", "details": {}, "summary": ""}


async def find_best_offer(offer_type: str) -> str:
    print(f"--- TOOL CALL: find_best_offer(type='{offer_type}') ---")
    try:
        best_bonus = rag_system.search(query=offer_type)
        if best_bonus:
            return json.dumps({"nome_casa": best_bonus['casa'], "descricao_oferta": best_bonus['descricao']})
        return json.dumps({"error": "Nenhuma oferta encontrada."})
    except Exception as e:
        return json.dumps({"error": f"Erro na busca: {e}"})


async def track_lead_status(lead_id: str, nome: str, telefone: str, new_status: str, details: dict):
    """
    Rastreia e atualiza o status de um lead no ficheiro conversation_tracker.csv.
    Esta é a versão corrigida e padronizada.
    """
    try:
        file_path = TRACKER_FILE_PATH
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        details_str = json.dumps(details)

        if not pd.io.common.file_exists(file_path):
            tracker_df = pd.DataFrame(columns=['lead_id', 'nome', 'telefone', 'status', 'last_update', 'details', 'summary'])
        else:
            tracker_df = pd.read_csv(file_path, dtype={'telefone': str})

        # Procura pelo telefone para garantir consistência
        telefone_str = str(telefone)
        if telefone_str in tracker_df['telefone'].values:
            # Atualiza o lead existente
            index = tracker_df[tracker_df['telefone'] == telefone_str].index[0]
            tracker_df.loc[index, ['lead_id', 'nome', 'status', 'last_update', 'details']] = [lead_id, nome, new_status, now, details_str]
        else:
            # Adiciona um novo lead se não for encontrado
            new_row = pd.DataFrame([{
                'lead_id': lead_id, 'nome': nome, 'telefone': telefone_str,
                'status': new_status, 'last_update': now,
                'details': details_str, 'summary': ''
            }])
            tracker_df = pd.concat([tracker_df, new_row], ignore_index=True)

        tracker_df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"ERRO CRÍTICO ao rastrear status para {nome}: {e}")
        return False


async def summarize_and_save_conversation(phone_number: str, conversation_history: list) -> str:
    """NOVA FUNÇÃO: Cria um resumo da conversa e o salva no tracker."""
    print(f"--- TOOL CALL: summarize_and_save_conversation (phone='{phone_number}') ---")
    try:
        transcript = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history if 'content' in msg and msg['content'] is not None])
        
        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em resumir conversas. Crie um resumo conciso (1-2 frases) do diálogo a seguir, focando nos interesses e na decisão final do cliente. Ex: 'Cliente demonstrou interesse em bônus de slots para jackpot, aceitou o link da Casa Alpha Bet mas disse que se cadastraria mais tarde.'"},
                {"role": "user", "content": transcript}
            ],
            temperature=0.2,
        )
        summary = response.choices[0].message.content

        tracker_df = pd.read_csv(TRACKER_FILE_PATH, dtype={'telefone': str})
        if phone_number in tracker_df['telefone'].values:
            tracker_df.loc[tracker_df['telefone'] == phone_number, 'summary'] = summary
            tracker_df.to_csv(TRACKER_FILE_PATH, index=False)
            return json.dumps({"status": "sucesso", "summary": summary})
        else:
            return json.dumps({"status": "falha", "message": "Lead não encontrado no tracker para salvar o resumo."})

    except Exception as e:
        print(f"ERRO ao sumarizar: {e}")
        return json.dumps({"status": "falha", "message": str(e)})


async def generate_registration_link(house_name: str, lead_id: str) -> str:
    house_urls = {
        "Casa Alpha Bet": "https://alpharealbet.com/register",
        "Casa Beta Sorte": "https://betasorte.com.br/cadastro",
        "Casa Gamma Win": "https://gammawin.io/signup"
    }
    base_url = house_urls.get(house_name, "https://linkpadrao.com")
    full_link = f"{base_url}?aff_id=junior&sub_id={lead_id}"
    return json.dumps({"registration_link": full_link})