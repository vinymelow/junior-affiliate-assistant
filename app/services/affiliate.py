import json
import csv
from datetime import datetime
from app.core.rag import rag_system
import ast
import openai
from app.config import settings
import asyncio
import os

# --- CORREÇÃO CRÍTICA: LOCK PARA PROTEGER O ACESSO AOS FICHEIROS ---
# Este lock garante que apenas uma tarefa pode ler/escrever nos CSVs de cada vez.
file_lock = asyncio.Lock()

LEADS_FILE_PATH = 'data/leads.csv'
TRACKER_FILE_PATH = 'data/conversation_tracker.csv'

def parse_tracker_details(details_str):
    try:
        return ast.literal_eval(details_str) if isinstance(details_str, str) else details_str
    except (ValueError, SyntaxError):
        return {}

async def get_lead_details(phone_number: str) -> str:
    async with file_lock:
        try:
            if not os.path.exists(LEADS_FILE_PATH):
                return json.dumps({"nome": "parceiro(a)", "genero": "N", "lead_id": "unknown_file_not_found"})
            
            with open(LEADS_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('telefone') == phone_number:
                        return json.dumps({
                            "nome": row.get('nome', 'parceiro(a)'),
                            "genero": row.get('genero', 'N').upper(),
                            "lead_id": str(row.get('lead_id', 'unknown'))
                        })
            return json.dumps({"nome": "parceiro(a)", "genero": "N", "lead_id": "unknown"})
        except Exception as e:
            return json.dumps({"error": f"Erro ao ler leads: {e}"})

async def get_lead_current_status(phone_number: str) -> dict:
    async with file_lock:
        try:
            if not os.path.exists(TRACKER_FILE_PATH):
                return {"status": "novo", "details": {}, "summary": ""}
            
            last_entry = None
            with open(TRACKER_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('telefone') == phone_number:
                        last_entry = row
            
            if last_entry:
                details_dict = parse_tracker_details(last_entry.get('details', '{}'))
                return {
                    "status": last_entry.get('status', 'novo'),
                    "details": details_dict,
                    "summary": last_entry.get('summary', '')
                }
        except Exception:
            pass
        
        return {"status": "novo", "details": {}, "summary": ""}

async def track_lead_status(lead_id: str, nome: str, telefone: str, new_status: str, details: dict) -> bool:
    async with file_lock:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            details_str = json.dumps(details)
            telefone_str = str(telefone)

            # Ler dados existentes
            rows = []
            headers = ['lead_id', 'nome', 'telefone', 'status', 'last_update', 'details', 'summary']
            
            if os.path.exists(TRACKER_FILE_PATH):
                with open(TRACKER_FILE_PATH, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames or headers
                    rows = list(reader)

            # Procurar lead existente
            lead_found = False
            for i, row in enumerate(rows):
                if row.get('telefone') == telefone_str:
                    rows[i].update({
                        'lead_id': lead_id,
                        'nome': nome,
                        'status': new_status,
                        'last_update': now,
                        'details': details_str
                    })
                    lead_found = True
                    break

            # Se não encontrou, adicionar novo
            if not lead_found:
                rows.append({
                    'lead_id': lead_id,
                    'nome': nome,
                    'telefone': telefone_str,
                    'status': new_status,
                    'last_update': now,
                    'details': details_str,
                    'summary': ''
                })

            # Escrever de volta
            with open(TRACKER_FILE_PATH, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            return True
        except Exception as e:
            print(f"ERRO CRÍTICO ao rastrear status para {nome}: {e}")
            return False

async def get_all_active_leads() -> list:
    """
    📋 Busca todos os leads ativos do sistema
    """
    async with file_lock:
        try:
            active_leads = []
            
            if not os.path.exists(LEADS_FILE_PATH):
                return active_leads
            
            with open(LEADS_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Busca status atual do lead
                    phone_number = row.get('telefone')
                    if phone_number:
                        lead_status = await get_lead_current_status(phone_number)
                        
                        # Inclui apenas leads que não foram convertidos ou recusados
                        status = lead_status.get('status', 'novo')
                        if status not in ['Funil_CONVERTIDO', 'Funil_RECUSADO']:
                            active_leads.append({
                                'telefone': phone_number,
                                'nome': row.get('nome', 'parceiro(a)'),
                                'genero': row.get('genero', 'N'),
                                'lead_id': row.get('lead_id', 'unknown'),
                                'status_atual': status,
                                'details': lead_status.get('details', {})
                            })
            
            return active_leads
            
        except Exception as e:
            print(f"ERRO ao buscar leads ativos: {e}")
            return []

async def summarize_and_save_conversation(phone_number: str, conversation_history: list) -> str:
    try:
        transcript = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history if 'content' in msg and msg['content'] is not None])
        
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em resumir conversas. Crie um resumo conciso (1-2 frases) do diálogo a seguir, focando nos interesses e na decisão final do cliente."},
                {"role": "user", "content": transcript}
            ],
            temperature=0.2,
            max_tokens=100
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Salvar resumo no tracker
        async with file_lock:
            if os.path.exists(TRACKER_FILE_PATH):
                rows = []
                with open(TRACKER_FILE_PATH, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames
                    rows = list(reader)

                # Atualizar resumo do lead
                for i, row in enumerate(rows):
                    if row.get('telefone') == phone_number:
                        rows[i]['summary'] = summary
                        break

                # Escrever de volta
                with open(TRACKER_FILE_PATH, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(rows)

        return json.dumps({"status": "sucesso", "summary": summary})
    except Exception as e:
        print(f"ERRO ao resumir conversa para {phone_number}: {e}")
        return json.dumps({"status": "falha", "message": str(e)})