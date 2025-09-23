import sqlite3
import pandas as pd
import os

DB_PATH = 'leads_master.db'
CSV_PATH = 'data/leads_master.csv'
TABLE_NAME = 'leads'

def criar_base_de_dados():
    if os.path.exists(DB_PATH):
        print(f"AVISO: A base de dados '{DB_PATH}' já existe. Nenhuma ação foi tomada.")
        return

    print(f"INFO: A ler o ficheiro de leads de '{CSV_PATH}'...")
    try:
        colunas = [
            'username', 'lead_id', 'registration_date', 'primeiro_nome', 'sobrenome', 
            'email', 'coluna_vazia_1', 'genero', 'data_nascimento', 'rua', 
            'complemento', 'estado', 'cidade', 'cep', 'telefone_1', 'telefone_2', 
            'coluna_vazia_2', 'pais', 'cpf', 'coluna_vazia_3', 'ultima_atualizacao', 
            'id_afiliado', 'outro_id', 'valor'
        ]
        
        leads_df = pd.read_csv(CSV_PATH, delimiter=';', header=None, names=colunas, dtype={'telefone_1': str, 'lead_id': str})

        leads_df['nome'] = leads_df['primeiro_nome'].str.cat(leads_df['sobrenome'], sep=' ').str.strip()
        leads_df.rename(columns={'telefone_1': 'telefone'}, inplace=True)
        
        colunas_uteis = ['lead_id', 'nome', 'genero', 'cidade', 'telefone']
        leads_final_df = leads_df[colunas_uteis].copy()
        
        leads_final_df['status'] = 'pendente'

    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O ficheiro mestre de leads '{CSV_PATH}' não foi encontrado!")
        return
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao ler ou processar o ficheiro CSV. Erro: {e}")
        return

    print(f"INFO: A criar a base de dados em '{DB_PATH}'...")
    try:
        conn = sqlite3.connect(DB_PATH)
        leads_final_df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"✅ SUCESSO: Base de dados criada e {len(leads_final_df)} leads foram importados com os campos de personalização.")

    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao criar ou popular a base de dados. Erro: {e}")

if __name__ == '__main__':
    criar_base_de_dados()