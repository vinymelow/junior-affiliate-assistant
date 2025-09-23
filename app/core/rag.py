import os
import glob
import yaml
import json

class SimpleRAG:
    def __init__(self, knowledge_base_path='knowledge_base'):
        self.knowledge_base_path = knowledge_base_path
        self.documents = self._load_documents()
        print(f"--- RAG: Carregados {len(self.documents)} documentos da base de conhecimento ---")

    def _load_documents(self):
        documents = []
        for filepath in glob.glob(os.path.join(self.knowledge_base_path, '*.txt')):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    content_list = list(yaml.safe_load_all(f))
                    for content in content_list:
                        if isinstance(content, dict):
                            documents.append(content)
                except yaml.YAMLError as e:
                    print(f"AVISO: Ignorando ficheiro com erro de formatação: {filepath}, Erro: {e}")
        return documents

    def find_answer_in_kb(self, query: str) -> dict:
        query_lower = query.lower()
        best_match = None
        
        for doc in self.documents:
            for key, items in doc.items():
                if isinstance(items, list):
                    for item in items:
                        search_terms = item.get('palavras_chave', []) + item.get('apelidos', [])
                        for term in search_terms:
                            if term in query_lower:
                                best_match = item.get('resposta_curta')
                                break 
                        if best_match:
                            break
            if best_match:
                break
        
        return {"answer": best_match}

# --- Instância única do RAG ---
rag_system = SimpleRAG()

# --- Funções de Fachada que a IA pode chamar ---
async def find_answer_in_kb(query: str) -> dict:
    """
    Função de fachada para a ferramenta de Q&A. Retorna um dicionário.
    """
    print(f"--- TOOL CALL: find_answer_in_kb(query='{query}') ---")
    return rag_system.find_answer_in_kb(query)