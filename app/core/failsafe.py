import re
from app.core.rag import rag_system


def _is_greeting(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    greetings = [
        "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite",
        "e ai", "e aí", "salve", "como vai", "tudo bem", "td bem"
    ]
    return any(g in t for g in greetings) or bool(re.fullmatch(r"(?i)\s*o+i+\s*", t))


def generate_failsafe_reply(user_message: str, lead_context: dict) -> str:
    """
    Gera uma resposta curta, humana e segura sem depender da OpenAI.
    1) Cumprimentos simples → saudação curta
    2) Tenta responder via RAG
    3) Mensagem padrão amigável
    """
    try:
        if _is_greeting(user_message):
            return "E aí, parça! Sou o Júnior da BateuBet. Como posso te ajudar?"

        # Tenta responder via base de conhecimento
        rag_answer = rag_system.find_answer_in_kb(user_message or "")
        if rag_answer and rag_answer.get("answer"):
            return rag_answer["answer"]

        # Fallback curto e neutro
        nome = lead_context.get("nome", "parça")
        return f"Fala {nome}! Diz aí, como posso te ajudar agora?"
    except Exception:
        return "Tô aqui! Me diz como posso te ajudar, beleza?"


