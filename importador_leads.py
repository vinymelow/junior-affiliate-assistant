import sqlite3
import pandas as pd
import os

# --- CONFIGURAÇÕES ---
DB_PATH = 'leads_master.db'
CSV_PATH = 'data/leads_master.csv'
TABLE_NAME = 'leads'

def criar_base_de_dados():
    """
    Cria a base de dados SQLite e a tabela de leads a partir do ficheiro CSV mestre.
    Este script deve ser executado apenas uma vez para configurar a campanha.
    """
    if os.path.exists(DB_PATH):
        print(f"AVISO: A base de dados '{DB_PATH}' já existe. Nenhuma ação foi tomada.")
        return

    print(f"INFO: A ler o ficheiro de leads de '{CSV_PATH}'...")
    try:
        # Define os nomes das colunas com base na estrutura do CSV fornecido
        colunas = [
            'username', 'lead_id', 'registration_date', 'primeiro_nome', 'sobrenome', 
            'email', 'coluna_vazia_1', 'genero', 'data_nascimento', 'rua', 
            'complemento', 'estado', 'cidade', 'cep', 'telefone_1', 'telefone_2', 
            'coluna_vazia_2', 'pais', 'cpf', 'coluna_vazia_3', 'ultima_atualizacao', 
            'id_afiliado', 'outro_id', 'valor'
        ]
        
        # Lê o CSV com o delimitador correto e os nomes das colunas
        leads_df = pd.read_csv(CSV_PATH, delimiter=';', header=None, names=colunas, dtype={'telefone_1': str})

        # Limpeza e preparação dos dados
        leads_df['nome'] = leads_df['primeiro_nome'].str.cat(leads_df['sobrenome'], sep=' ').str.strip()
        leads_df.rename(columns={'telefone_1': 'telefone'}, inplace=True)
        
        # Seleciona apenas as colunas que vamos usar
        colunas_uteis = ['lead_id', 'nome', 'genero', 'cidade', 'telefone']
        leads_final_df = leads_df[colunas_uteis].copy()
        
        # Adicionar a coluna 'status' com o valor padrão 'pendente'
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
        
        # Salva o DataFrame limpo na base de dados
        leads_final_df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"✅ SUCESSO: Base de dados criada e {len(leads_final_df)} leads foram importados com os campos de personalização.")

    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao criar ou popular a base de dados. Erro: {e}")

if __name__ == '__main__':
    criar_base_de_dados()