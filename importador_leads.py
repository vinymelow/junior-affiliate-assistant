import sqlite3
import pandas as pd
import os

# --- CONFIGURAÇÕES ---
DB_PATH = 'leads_master.db'
CSV_PATH = 'data/leads_master.csv' # Coloque a sua lista principal de 100k leads aqui
TABLE_NAME = 'leads'

def criar_base_de_dados():
    """
    Cria a base de dados SQLite e a tabela de leads a partir de um ficheiro CSV.
    Este script deve ser executado apenas uma vez para configurar a campanha.
    """
    if os.path.exists(DB_PATH):
        print(f"AVISO: A base de dados '{DB_PATH}' já existe. Nenhuma ação foi tomada.")
        return

    print(f"INFO: A ler o ficheiro de leads de '{CSV_PATH}'...")
    try:
        leads_df = pd.read_csv(CSV_PATH)
        leads_df['telefone'] = leads_df['telefone'].astype(str)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O ficheiro mestre de leads '{CSV_PATH}' não foi encontrado!")
        return
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao ler o ficheiro CSV. Erro: {e}")
        return

    leads_df['status'] = 'pendente'

    print(f"INFO: A criar a base de dados em '{DB_PATH}'...")
    try:
        conn = sqlite3.connect(DB_PATH)
        leads_df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"✅ SUCESSO: Base de dados criada e {len(leads_df)} leads foram importados com o status 'pendente'.")
        print("INFO: O sistema está pronto para a próxima fase.")

    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao criar ou popular a base de dados. Erro: {e}")

if __name__ == '__main__':
    criar_base_de_dados()