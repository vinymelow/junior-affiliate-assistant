import pandas as pd
import json
from datetime import datetime
from app.core.rag import rag_system
import ast
import openai
from app.config import settings
import asyncio

file_lock = asyncio.Lock()

LEADS_FILE_PATH = 'data/leads.csv'
TRACKER_FILE_PATH = 'data/conversation_tracker.csv'

def parse_tracker_details(row):
    details_str = row.get('details', '{}')
    try:
        return ast.literal_eval(details_str) if isinstance(details_str, str) else details_str
    except (ValueError, SyntaxError):
        return {}

async def get_lead_details(phone_number: str) -> str:
    async with file_lock:
        try:
            leads_df = pd.read_csv(LEADS_FILE_PATH, dtype={'telefone': str})
            lead_info = leads_df[leads_df['telefone'] == phone_number]
            if not lead_info.empty:
                return json.dumps({
                    "nome": lead_info.iloc[0]['nome'], 
                    "genero": lead_info.iloc[0]['genero'],
                    "cidade": lead_info.iloc[0]['cidade'],
                    "lead_id": str(lead_info.iloc[0]['lead_id'])
                })
            return json.dumps({"nome": "parceiro(a)", "genero": "N", "cidade": "N/A", "lead_id": "unknown"})
        except FileNotFoundError:
            return json.dumps({"nome": "parceiro(a)", "genero": "N", "cidade": "N/A", "lead_id": "unknown_file_not_found"})
        except Exception as e:
            return json.dumps({"error": f"Erro ao ler leads: {e}"})

async def get_lead_current_status(phone_number: str) -> dict:
    async with file_lock:
        try:
            tracker_df = pd.read_csv(TRACKER_FILE_PATH, dtype={'telefone': str})
            lead_status = tracker_df[tracker_df['telefone'] == phone_number]
            if not lead_status.empty:
                last_entry = lead_status.iloc[-1]
                details_dict = parse_tracker_details(last_entry)
                return {"status": last_entry['status'], "details": details_dict, "summary": last_entry.get('summary', '')}
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"AVISO: Não foi possível ler o tracker para {phone_number}. Erro: {e}")
        return {"status": "Fase1_ContatoInicial", "details": {}, "summary": ""}

async def track_lead_status(lead_id: str, nome: str, telefone: str, new_status: str, details: dict) -> bool:
    async with file_lock:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            details_str = json.dumps(details)

            try:
                tracker_df = pd.read_csv(TRACKER_FILE_PATH, dtype={'telefone': str})
            except FileNotFoundError:
                tracker_df = pd.DataFrame(columns=['lead_id', 'nome', 'telefone', 'status', 'last_update', 'details', 'summary'])

            telefone_str = str(telefone)
            existing_lead_index = tracker_df[tracker_df['telefone'] == telefone_str].index
            
            if not existing_lead_index.empty:
                index = existing_lead_index[0]
                tracker_df.loc[index, ['lead_id', 'nome', 'status', 'last_update', 'details']] = [lead_id, nome, new_status, now, details_str]
            else:
                new_row = pd.DataFrame([{'lead_id': lead_id, 'nome': nome, 'telefone': telefone_str, 'status': new_status, 'last_update': now, 'details': details_str, 'summary': ''}])
                tracker_df = pd.concat([tracker_df, new_row], ignore_index=True)

            tracker_df.to_csv(TRACKER_FILE_PATH, index=False)
            return True
        except Exception as e:
            print(f"ERRO CRÍTICO ao rastrear status para {nome}: {e}")
            return False

async def summarize_and_save_conversation(phone_number: str, conversation_history: list) -> str:
    try:
        transcript = "\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in conversation_history if msg.get('content')])
        
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em resumir conversas. Crie um resumo conciso (1-2 frases) do diálogo a seguir, focando nos interesses e na decisão final do cliente."},
                {"role": "user", "content": transcript}
            ],
            temperature=0.2,
        )
        summary = response.choices[0].message.content

        async with file_lock:
            tracker_df = pd.read_csv(TRACKER_FILE_PATH, dtype={'telefone': str})
            if phone_number in tracker_df['telefone'].values:
                tracker_df.loc[tracker_df['telefone'] == phone_number, 'summary'] = summary
                tracker_df.to_csv(TRACKER_FILE_PATH, index=False)
                return json.dumps({"status": "sucesso", "summary": summary})
            else:
                return json.dumps({"status": "falha", "message": "Lead não encontrado no tracker."})
    except Exception as e:
        print(f"ERRO ao sumarizar: {e}")
        return json.dumps({"status": "falha", "message": str(e)})