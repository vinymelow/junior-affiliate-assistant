import spacy
import re

try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    from spacy.cli import download
    download("pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")

def get_intent_and_entities(text: str) -> dict:
    intent = "geral"
    text_lower = text.lower()

    if any(keyword in text_lower for keyword in ["quero", "sim", "pode mandar", "manda o link", "aceito"]):
        intent = "aceitacao"
    elif any(keyword in text_lower for keyword in ["não", "nao quero", "parar", "spam"]):
        intent = "recusa"
    elif '?' in text:
        intent = "pergunta_geral"
    
    return {"intent": intent, "entities": {}}