import os
import glob
import yaml

class SimpleRAG:
    def __init__(self, knowledge_base_path='knowledge_base'):
        self.knowledge_base_path = knowledge_base_path
        self.documents = self._load_documents()
        print(f"--- RAG: Carregados {len(self.documents)} bônus de {len(set(d.get('casa_de_aposta', 'N/A') for d in self.documents))} casas ---")

    def _load_documents(self):
        documents = []
        for filepath in glob.glob(os.path.join(self.knowledge_base_path, '*.txt')):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    # Usamos yaml.safe_load para ler o conteúdo estruturado do TXT
                    content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        documents.append(content)
                except yaml.YAMLError as e:
                    print(f"AVISO: Ignorando ficheiro com erro de formatação: {filepath}, Erro: {e}")
        return documents

    def find_best_offer(self, interest: str) -> str:
        interest_lower = interest.lower()
        best_offer = None
        highest_score = -1

        for doc in self.documents:
            score = 0
            # Aumenta a pontuação se o interesse principal corresponder
            if interest_lower in [kw.lower() for kw in doc.get('interesses_chave', [])]:
                score += 10
            
            # Bônus por palavras-chave secundárias
            for kw in doc.get('palavras_chave_secundarias', []):
                if kw.lower() in interest_lower:
                    score += 2

            if score > highest_score:
                highest_score = score
                best_offer = doc
        
        if best_offer:
            return f"Encontrei a boa pra você, parça! Na {best_offer['casa_de_aposta']}, tá rolando: {best_offer['descricao_curta']}. O depósito mínimo é de {best_offer['deposito_minimo']} e o link é: {best_offer['link_afiliado']}"
        
        return "Mano, não achei nenhuma oferta específica pra isso agora, mas posso ver outras paradas se quiser."

# --- CORREÇÃO APLICADA AQUI ---
# Criamos uma instância única do nosso sistema RAG
rag_system = SimpleRAG()

# Criamos uma função simples que pode ser importada facilmente por outros ficheiros
async def find_best_offer(interest: str) -> str:
    """
    Função de fachada que usa a instância do RAG para encontrar a melhor oferta.
    """
    return rag_system.find_best_offer(interest)