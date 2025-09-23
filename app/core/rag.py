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
        """
        NOVA FUNÇÃO: Procura uma resposta direta para uma pergunta geral na base de conhecimento.
        """
        query_lower = query.lower()
        best_match = None
        highest_score = 0

        for doc in self.documents:
            # Lógica para ficheiros de jogos
            if doc.get('tipo_documento') == 'info_jogo':
                for jogo in doc.get('jogos', []):
                    search_terms = jogo.get('palavras_chave', []) + jogo.get('apelidos', [])
                    for term in search_terms:
                        if term in query_lower:
                            score = 10 # Pontuação alta para correspondência direta
                            if score > highest_score:
                                highest_score = score
                                best_match = jogo.get('resposta_curta')
            
            # Lógica para ficheiros de informações gerais
            if doc.get('tipo_documento') == 'info_geral':
                for topico in doc.get('topicos', []):
                    for term in topico.get('palavras_chave', []):
                        if term in query_lower:
                            score = 10
                            if score > highest_score:
                                highest_score = score
                                best_match = topico.get('resposta_curta')
        
        return {"answer": best_match} if best_match else {"answer": None}

# --- Instância única do RAG ---
rag_system = SimpleRAG()

# --- Funções de Fachada que a IA pode chamar ---

async def find_answer_in_kb(query: str) -> str:
    """
    Função de fachada para a nova ferramenta de Q&A.
    """
    print(f"--- TOOL CALL: find_answer_in_kb(query='{query}') ---")
    result = rag_system.find_answer_in_kb(query)
    return json.dumps(result)

async def find_best_offer(interest: str) -> str:
    """
    Função mantida para procurar por ofertas específicas, se necessário.
    """
    # (O código desta função pode ser mantido como estava, ou simplificado se a outra assumir tudo)
    return json.dumps({"error": "Função não implementada para este exemplo."})