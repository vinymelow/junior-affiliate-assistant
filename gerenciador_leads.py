import sqlite3
import pandas as pd

DB_PATH = 'leads_master.db'
LEADS_DIARIOS_PATH = 'data/leads.csv'
TABLE_NAME = 'leads'
LOTE_DIARIO = 1200

def preparar_lote_diario():
    print("--- GERENCIADOR DE LEADS (Início) ---")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = f"SELECT lead_id, nome, genero, cidade, telefone FROM {TABLE_NAME} WHERE status = 'pendente' LIMIT {LOTE_DIARIO}"
        leads_do_dia = pd.read_sql_query(query, conn)

        if leads_do_dia.empty:
            print("INFO: Não há mais leads pendentes para processar.")
            return

        print(f"INFO: {len(leads_do_dia)} novos leads selecionados para o disparo de hoje.")

        leads_do_dia.to_csv(LEADS_DIARIOS_PATH, index=False)
        print(f"INFO: Ficheiro '{LEADS_DIARIOS_PATH}' atualizado com dados de personalização.")

        ids_para_atualizar_tuple = tuple(map(str, leads_do_dia['lead_id'].tolist()))
        if not ids_para_atualizar_tuple:
            print("INFO: Nenhum lead para atualizar.")
            return

        placeholders = ','.join('?' for _ in ids_para_atualizar_tuple)
        update_query = f"UPDATE {TABLE_NAME} SET status = 'contactado' WHERE lead_id IN ({placeholders})"
        
        cursor.execute(update_query, ids_para_atualizar_tuple)
        conn.commit()

        print(f"INFO: {len(ids_para_atualizar_tuple)} leads atualizados para 'contactado' na base de dados mestre.")

    except sqlite3.Error as e:
        print(f"ERRO CRÍTICO de base de dados: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    
    print("--- GERENCIADOR DE LEADS (Fim) ---")

if __name__ == '__main__':
    preparar_lote_diario()