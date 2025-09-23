import sqlite3
import pandas as pd

# --- CONFIGURAÇÕES ---
DB_PATH = 'leads_master.db'
LEADS_DIARIOS_PATH = 'data/leads.csv'
TABLE_NAME = 'leads'
LOTE_DIARIO = 1200

def preparar_lote_diario():
    """
    Seleciona um novo lote de leads pendentes da base de dados mestre,
    escreve-os no ficheiro CSV do dia e atualiza o seu status para 'contactado'.
    """
    print("--- GERENCIADOR DE LEADS (Início) ---")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Seleciona o lote diário de leads pendentes
        query = f"SELECT lead_id, nome, telefone FROM {TABLE_NAME} WHERE status = 'pendente' LIMIT {LOTE_DIARIO}"
        leads_do_dia = pd.read_sql_query(query, conn)

        if leads_do_dia.empty:
            print("INFO: Não há mais leads pendentes para processar. Campanha concluída.")
            return

        print(f"INFO: {len(leads_do_dia)} novos leads selecionados para o disparo de hoje.")

        # Escreve os leads selecionados no ficheiro que o disparador_funil.py irá ler
        leads_do_dia.to_csv(LEADS_DIARIOS_PATH, index=False)
        print(f"INFO: Ficheiro '{LEADS_DIARIOS_PATH}' atualizado com o lote do dia.")

        # Atualiza o status dos leads selecionados para 'contactado' para não serem enviados novamente
        ids_para_atualizar = tuple(leads_do_dia['lead_id'].tolist())
        update_query = f"UPDATE {TABLE_NAME} SET status = 'contactado' WHERE lead_id IN {ids_para_atualizar}"
        
        cursor.execute(update_query)
        conn.commit()

        print(f"INFO: {len(ids_para_atualizar)} leads atualizados para 'contactado' na base de dados mestre.")

    except sqlite3.Error as e:
        print(f"ERRO CRÍTICO de base de dados: {e}")
    finally:
        if conn:
            conn.close()
    
    print("--- GERENCIADOR DE LEADS (Fim) ---")

if __name__ == '__main__':
    preparar_lote_diario()