import httpx
import time
import random
import asyncio
from app.config import settings

async def send_whatsapp_message(number: str, message: str) -> bool:
    print(f"--- INICIANDO ENVIO HUMANIZADO PARA: {number} ---")
    
    full_url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE}"
    headers = {"apikey": settings.EVOLUTION_API_KEY, "Content-Type": "application/json"}
    numero_formatado = f"{number}@s.whatsapp.net"
    
    CARACTERES_POR_SEGUNDO = 18
    MIN_DELAY_SEGUNDOS = 1.5
    MAX_DELAY_SEGUNDOS = 4.0

    paragrafos = [p.strip() for p in message.split('\n') if p.strip()]

    for i, paragrafo in enumerate(paragrafos):
        payload = {"number": numero_formatado, "options": {"delay": 1200, "presence": "composing"}, "text": paragrafo}

        if i > 0:
            delay_base = len(paragrafo) / CARACTERES_POR_SEGUNDO
            delay_com_jitter = delay_base + random.uniform(-0.5, 1.0)
            delay_final = max(MIN_DELAY_SEGUNDOS, min(delay_com_jitter, MAX_DELAY_SEGUNDOS))
            print(f"Pausa humanizada de {delay_final:.2f} segundos...")
            await asyncio.sleep(delay_final)

        try:
            async with httpx.AsyncClient() as client:
                print(f"Enviando parágrafo: '{paragrafo}'")
                response = await client.post(full_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"ERRO AO ENVIAR MENSAGEM: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"ERRO DE CONEXÃO com a API da Evolution: {e}")
            return False
            
    print(f"--- ENVIO PARA {number} CONCLUÍDO ---")
    return True