import asyncio
import pandas as pd
from app.core import rag
from app.services import affiliate
import json

async def run_tests():
    """Executa testes para validar os componentes principais do sistema."""
    print("--- INICIANDO TESTES DO ASSISTENTE JÚNIOR (JOURNEY VERSION) ---")
    
    total_tests = 3
    passed_tests = 0
    
    try:
        assert len(rag.rag_system.documents) > 0, "Base de conhecimento não carregada."
        print("✅ TESTE 1/3 PASSOU: Base de Conhecimento (RAG) OK.")
        passed_tests += 1
    except Exception as e:
        print(f"❌ TESTE 1/3 FALHOU: RAG. Erro: {e}")

    try:
        leads_df = pd.read_csv('data/leads.csv')
        assert 'nome' in leads_df.columns, "Ficheiro de leads inválido."
        print("✅ TESTE 2/3 PASSOU: Ficheiro de leads OK.")
        passed_tests += 1
    except Exception as e:
        print(f"❌ TESTE 2/3 FALHOU: Leitura do Ficheiro de Leads. Erro: {e}")
        
    try:
        await affiliate.track_lead_status('test_id', 'test_nome', 'test_tel', 'test_status', {"key": "value"})
        tracker_df = pd.read_csv('data/conversation_tracker.csv')
        assert not tracker_df.empty, "O tracker não foi escrito."
        print("✅ TESTE 3/3 PASSOU: Sistema de Rastreamento (Tracker) OK.")
        passed_tests += 1
    except Exception as e:
        print(f"❌ TESTE 3/3 FALHOU: Sistema de Rastreamento. Erro: {e}")

    print(f"\n📊 RESUMO: {passed_tests}/{total_tests} PASSARAM")
    if passed_tests == total_tests:
        print("🎉 SISTEMA PRONTO PARA OPERAR!")
    else:
        print("🔥 ALERTA: Testes falharam.")

if __name__ == "__main__":
    asyncio.run(run_tests())