import os
import glob
import yaml

class SimpleRAG:
    def __init__(self, knowledge_base_path='knowledge_base'):
        self.knowledge_base_path = knowledge_base_path
        self.documents = self._load_documents()
        print(f"--- RAG: Carregados {len(self.documents)} documentos da base de conhecimento ---")

    def _load_documents(self):
        """
        Carrega todos os ficheiros .txt e os processa como documentos YAML.
        Lida com erros de formatação de forma graciosa.
        """
        documents = []
        for filepath in glob.glob(os.path.join(self.knowledge_base_path, '*.txt')):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    # safe_load é mais apropriado para ficheiros com um único documento YAML
                    content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        documents.append(content)
            except yaml.YAMLError as e:
                print(f"AVISO: Ignorando ficheiro com erro de formatação: {filepath}, Erro: {e}")
            except Exception as e:
                print(f"ERRO INESPERADO ao carregar {filepath}: {e}")
        return documents

    def find_answer_in_kb(self, query: str) -> dict:
        """
        Busca a melhor resposta na base de conhecimento de forma robusta e segura.
        """
        query_lower = query.lower()
        
        for doc in self.documents:
            # Itera sobre as listas de itens dentro de cada documento (ex: 'topicos', 'jogos', 'ofertas')
            for key, items in doc.items():
                if not isinstance(items, list):
                    continue

                for item in items:
                    # Garante que 'item' é um dicionário antes de tentar aceder
                    if not isinstance(item, dict):
                        continue

                    # Concatena todas as listas de palavras-chave num único local
                    search_terms = item.get('palavras_chave', []) + item.get('apelidos', [])
                    
                    for term in search_terms:
                        if term in query_lower:
                            # Encontrou uma correspondência, retorna a resposta curta
                            answer = item.get('resposta_curta')
                            if answer:
                                print(f"--- RAG: Resposta encontrada para '{query}' -> '{answer}'")
                                return {"answer": answer}
        
        # Se nenhuma resposta for encontrada após verificar todos os documentos
        print(f"--- RAG: Nenhuma resposta encontrada para '{query}' ---")
        return {"answer": None}

# --- Instância única do RAG ---
rag_system = SimpleRAG()

# --- Função de Fachada que a IA pode chamar ---
async def find_answer_in_kb(query: str) -> dict:
    """
    Função de fachada para a ferramenta de Q&A. Retorna um dicionário.
    """
    print(f"--- TOOL CALL: find_answer_in_kb(query='{query}') ---")
    return rag_system.find_answer_in_kb(query)