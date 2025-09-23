#!/usr/bin/env python3
"""
🔄 CONVERSOR DE LEADS CSV
Converte o arquivo leads.csv atual para o formato esperado pelo sistema
"""

import csv
import os
from datetime import datetime

def converter_leads_csv():
    """
    Converte o CSV atual (sem cabeçalhos) para o formato esperado pelo sistema
    """
    
    # Caminhos dos arquivos
    arquivo_original = 'data/leads.csv'
    arquivo_backup = f'data/leads_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    print("🔄 Iniciando conversão do arquivo leads.csv...")
    
    # Verifica se o arquivo existe
    if not os.path.exists(arquivo_original):
        print(f"❌ ERRO: Arquivo {arquivo_original} não encontrado!")
        return False
    
    try:
        # Faz backup do arquivo original
        print(f"📋 Criando backup: {arquivo_backup}")
        os.rename(arquivo_original, arquivo_backup)
        
        # Define os índices das colunas que precisamos
        # Baseado na análise: username;lead_id;registration_date;primeiro_nome;sobrenome;email;...;genero;...;cidade;...;telefone;...
        idx_lead_id = 1
        idx_primeiro_nome = 3
        idx_sobrenome = 4
        idx_genero = 7
        idx_cidade = 12
        idx_telefone = 14
        
        leads_processados = []
        total_linhas = 0
        
        # Lê o arquivo CSV original
        print("📖 Lendo arquivo CSV original...")
        with open(arquivo_backup, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            
            for row in reader:
                total_linhas += 1
                
                # Verifica se a linha tem colunas suficientes
                if len(row) < 15:
                    continue
                
                # Extrai os dados necessários
                lead_id = row[idx_lead_id].strip() if len(row) > idx_lead_id else ''
                primeiro_nome = row[idx_primeiro_nome].strip() if len(row) > idx_primeiro_nome else ''
                sobrenome = row[idx_sobrenome].strip() if len(row) > idx_sobrenome else ''
                genero = row[idx_genero].strip() if len(row) > idx_genero else 'N'
                cidade = row[idx_cidade].strip() if len(row) > idx_cidade else 'N/A'
                telefone = row[idx_telefone].strip() if len(row) > idx_telefone else ''
                
                # Cria nome completo
                nome = f"{primeiro_nome} {sobrenome}".strip()
                if not nome:
                    nome = "Lead"
                
                # Valida telefone
                if not telefone or telefone == '':
                    continue
                
                # Padroniza dados
                if not genero or genero == '':
                    genero = 'N'
                if not cidade or cidade == '':
                    cidade = 'N/A'
                
                leads_processados.append({
                    'lead_id': lead_id,
                    'nome': nome,
                    'genero': genero,
                    'cidade': cidade,
                    'telefone': telefone
                })
        
        print(f"📊 Total de linhas lidas: {total_linhas}")
        print(f"✅ Leads válidos após limpeza: {len(leads_processados)}")
        
        # Salva o arquivo convertido
        print(f"💾 Salvando arquivo convertido: {arquivo_original}")
        with open(arquivo_original, 'w', encoding='utf-8', newline='') as file:
            fieldnames = ['lead_id', 'nome', 'genero', 'cidade', 'telefone']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Escreve cabeçalho
            writer.writeheader()
            
            # Escreve dados
            writer.writerows(leads_processados)
        
        print("🎉 Conversão concluída com sucesso!")
        print(f"📋 Backup salvo em: {arquivo_backup}")
        
        # Mostra amostra dos dados
        print(f"📊 Amostra dos primeiros 5 leads:")
        for i, lead in enumerate(leads_processados[:5]):
            print(f"  {i+1}. {lead['nome']} ({lead['genero']}) - {lead['telefone']} - {lead['cidade']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO durante a conversão: {e}")
        
        # Restaura o arquivo original em caso de erro
        if os.path.exists(arquivo_backup):
            print("🔄 Restaurando arquivo original...")
            os.rename(arquivo_backup, arquivo_original)
        
        return False

if __name__ == '__main__':
    converter_leads_csv()