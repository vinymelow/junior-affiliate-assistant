"""
🎯 ORQUESTRADOR DE FUNIL - BATEU BET
Sistema completo de 20 dias com mensagens específicas para WhatsApp
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.core.ai import generate_funnel_message
from app.services.whatsapp import send_whatsapp_message
from app.services.affiliate import track_lead_status, get_lead_current_status

# 📋 CRONOGRAMA COMPLETO DO FUNIL (20 DIAS)
FUNNEL_SCHEDULE = {
    # DIAS 1-5: IMPACTO INICIAL
    1: {
        "objetivo": "Apresentação do Convite Ouro (exclusividade + curiosidade)",
        "tipo": "whatsapp_gatilho",
        "mensagem_fixa": "Olá {nome}, aqui é o Alex, gerente da Bateu Bet. Alguns convites deram erro no bônus de 500%. Quer que eu verifique o seu? Responda SIM."
    },
    2: {
        "objetivo": "Confirmação e ajuda para começar",
        "tipo": "whatsapp_followup",
        "mensagem_fixa": "E aí {nome}! Notei que ainda não ativou seu Convite Ouro. Quer ajuda para começar agora? É rapidinho!"
    },
    3: {
        "objetivo": "Pressão social - outros já ativaram",
        "tipo": "whatsapp_social_proof",
        "mensagem_fixa": "Opa {nome}! Mais de 500 pessoas já ativaram o Convite Ouro hoje. Não vai ficar de fora né? Bora ativar!"
    },
    4: {
        "objetivo": "Urgência - bônus expirando",
        "tipo": "whatsapp_urgencia",
        "mensagem_fixa": "Eita {nome}! Seu bônus de 500% expira em breve. Posso ativar junto com você agora? É só confirmar!"
    },
    5: {
        "objetivo": "Lembrete consultivo - 48h para expirar",
        "tipo": "whatsapp_consultivo",
        "mensagem_fixa": "Lembrete {nome}: seu bônus de 500% expira em 48h. Precisa de ajuda para ativar? Estou aqui!"
    },
    
    # DIAS 6-10: ESCALAÇÃO
    6: {
        "objetivo": "Aversão à perda - o que perde se não ativar",
        "tipo": "whatsapp_aversao_perda",
        "mensagem_fixa": "Não perca {nome}: bônus 500% + 50 rodadas grátis. Últimas horas mesmo! Bora garantir?"
    },
    7: {
        "objetivo": "Alta pressão - menos de 24h",
        "tipo": "whatsapp_alta_pressao",
        "mensagem_fixa": "Urgente {nome}! Seu bônus expira em menos de 24h. Posso ativar agora com você? Responde aí!"
    },
    8: {
        "objetivo": "Convite expira hoje",
        "tipo": "whatsapp_expira_hoje",
        "mensagem_fixa": "Último dia {nome}! Seu Convite Ouro expira hoje. Quer que eu ative seu bônus? É rapidinho!"
    },
    9: {
        "objetivo": "Observação de engajamento",
        "tipo": "whatsapp_engajamento",
        "mensagem_fixa": "Oi {nome}! Vi que você abriu nossas mensagens mas não ativou ainda. Posso te ajudar? Qual a dúvida?"
    },
    10: {
        "objetivo": "História de sucesso",
        "tipo": "whatsapp_sucesso",
        "mensagem_fixa": "Olha só {nome}: ontem um cara transformou R$50 em R$5.000 aqui! Ainda dá tempo de você começar também!"
    },
    
    # DIAS 11-15: INCENTIVOS EXTRAS
    11: {
        "objetivo": "Oferta extra - rodadas adicionais",
        "tipo": "whatsapp_oferta_extra",
        "mensagem_fixa": "Oferta exclusiva {nome}: +10 rodadas grátis se ativar hoje! Bora aproveitar essa?"
    },
    12: {
        "objetivo": "Confirmação das rodadas extras",
        "tipo": "whatsapp_confirmacao",
        "mensagem_fixa": "E aí {nome}! Posso já ativar suas 10 rodadas extras? É só confirmar que eu libero tudo!"
    },
    13: {
        "objetivo": "Personalização - preferência de jogos",
        "tipo": "whatsapp_personalizacao",
        "mensagem_fixa": "Qual você prefere {nome}: Slots, Roleta ou Esportes? Posso indicar o melhor jogo pra começar!"
    },
    14: {
        "objetivo": "Cashback especial",
        "tipo": "whatsapp_cashback",
        "mensagem_fixa": "Novidade {nome}! Cashback de 20% para novos jogadores. Posso ativar agora? É garantido!"
    },
    15: {
        "objetivo": "Último lembrete do bônus",
        "tipo": "whatsapp_ultimo_lembrete",
        "mensagem_fixa": "Último lembrete {nome}: seu bônus acaba amanhã! Não deixa passar essa oportunidade!"
    },
    
    # DIAS 16-20: FECHAMENTO
    16: {
        "objetivo": "Seguro de 50%",
        "tipo": "whatsapp_seguro",
        "mensagem_fixa": "NOVO {nome}: seguro de 50%! Se perder, devolvemos metade do depósito. Quer ativar? Responda SEGURO."
    },
    17: {
        "objetivo": "Última chance do seguro",
        "tipo": "whatsapp_ultima_chance_seguro",
        "mensagem_fixa": "Última chance {nome}! Posso ativar o seguro no seu primeiro depósito? É só confirmar!"
    },
    18: {
        "objetivo": "Remoção da promoção",
        "tipo": "whatsapp_remocao",
        "mensagem_fixa": "Atenção {nome}: sua conta será removida da promoção hoje! Sua chance final termina HOJE!"
    },
    19: {
        "objetivo": "Última ligação/contato",
        "tipo": "whatsapp_ultima_ligacao",
        "mensagem_fixa": "Última tentativa {nome}! Posso ativar o bônus junto com você agora? É a última chance mesmo!"
    },
    20: {
        "objetivo": "Encerramento final",
        "tipo": "whatsapp_encerramento",
        "mensagem_fixa": "FINAL {nome}: promoção encerrando em horas! Depois não há volta. É sua última chance!"
    }
}

class FunnelOrchestrator:
    """
    🎯 Orquestrador principal do funil de 20 dias
    """
    
    def __init__(self):
        self.schedule = FUNNEL_SCHEDULE
    
    async def get_lead_funnel_day(self, phone_number: str) -> int:
        """
        📅 Determina em que dia do funil o lead está
        """
        try:
            lead_status = await get_lead_current_status(phone_number)
            details = lead_status.get('details', {})
            
            # Verifica se já tem dia do funil definido
            if 'dia_funil' in details:
                return details['dia_funil']
            
            # Se é primeiro contato, começa no dia 1
            if lead_status.get('status') == 'Fase1_ContatoInicial':
                return 1
            
            # Se já tem histórico mas não tem dia definido, assume dia 1
            return 1
            
        except Exception as e:
            print(f"ERRO ao determinar dia do funil para {phone_number}: {e}")
            return 1
    
    async def advance_funnel_day(self, phone_number: str, current_day: int) -> int:
        """
        ⏭️ Avança o lead para o próximo dia do funil
        """
        next_day = min(current_day + 1, 20)  # Máximo 20 dias
        
        try:
            await track_lead_status(
                lead_id=phone_number,
                nome="Lead",
                telefone=phone_number,
                new_status=f"Funil_Dia{next_day}",
                details={
                    "dia_funil": next_day,
                    "data_ultimo_disparo": datetime.now().isoformat(),
                    "tipo_mensagem": self.schedule[next_day]["tipo"]
                }
            )
            print(f"✅ Lead {phone_number} avançou para o dia {next_day}")
            return next_day
            
        except Exception as e:
            print(f"ERRO ao avançar dia do funil para {phone_number}: {e}")
            return current_day
    
    async def get_day_message(self, day: int, lead_name: str = "parça") -> str:
        """
        📝 Obtém a mensagem específica para um dia do funil (USANDO IA)
        """
        if day not in self.schedule:
            return "Opa, parça! Como posso te ajudar hoje?"
        
        day_config = self.schedule[day]
        objetivo = day_config["objetivo"]
        
        # 🤖 USA IA para gerar mensagem personalizada baseada no objetivo
        try:
            ai_message = await generate_funnel_message(objetivo)
            # Personaliza com o nome do lead
            personalized_message = ai_message.replace("parça", lead_name).replace("mano", lead_name)
            print(f"🤖 IA gerou mensagem para dia {day}: {personalized_message}")
            return personalized_message
        except Exception as e:
            print(f"ERRO na IA, usando mensagem fixa: {e}")
            # Fallback para mensagem fixa se IA falhar
            mensagem_base = day_config["mensagem_fixa"]
            return mensagem_base.replace("{nome}", lead_name)
    
    async def should_send_funnel_message(self, phone_number: str, user_message: str) -> bool:
        """
        🤔 Determina se deve enviar mensagem do funil ou responder à pergunta
        NOVA LÓGICA: Mais permissiva para ativar conversação com IA
        """
        user_lower = user_message.lower()
        
        # Palavras-chave que SEMPRE ativam conversação livre (não funil)
        conversation_keywords = [
            "como", "qual", "onde", "quando", "por que", "o que", "quem",
            "link", "apostar", "cadastro", "bônus", "deposito", "depósito",
            "ajuda", "suporte", "problema", "erro", "dúvida", "duvida",
            "funciona", "fazer", "posso", "consigo", "preciso", "quero saber",
            "me explica", "não entendi", "não sei", "como faço"
        ]
        
        # Se contém palavras-chave de pergunta/dúvida, SEMPRE ativa IA
        if any(keyword in user_lower for keyword in conversation_keywords):
            print(f"🤖 Pergunta detectada, ativando IA: {user_message}")
            return False  # False = IA responde
        
        # Cumprimentos muito simples podem enviar mensagem do funil
        simple_greetings = ["oi", "olá", "alô", "e aí", "opa", "sim", "ok", "blz"]
        if user_lower.strip() in simple_greetings:
            print(f"📨 Cumprimento simples, enviando mensagem do funil: {user_message}")
            return True  # True = envia mensagem do funil
        
        # Para mensagens mais elaboradas, deixa a IA responder
        if len(user_message.strip()) > 10:  # Mensagens com mais de 10 caracteres
            print(f"🤖 Mensagem elaborada, ativando IA: {user_message}")
            return False  # False = IA responde
        
        # Por padrão, envia mensagem do funil
        return True
    
    async def process_funnel_interaction(self, phone_number: str, user_message: str, lead_context: dict) -> str:
        """
        🎯 Processa interação do funil - decide se envia mensagem do dia ou responde pergunta
        """
        try:
            # 🛑 VERIFICAÇÃO CRÍTICA: Lead já converteu ou recusou?
            current_status = lead_context.get('status_atual', '')
            if current_status in ['Funil_CONVERTIDO', 'Funil_RECUSADO']:
                print(f"🛑 Lead {phone_number} já finalizou o funil com status: {current_status}")
                return None  # Não envia mais mensagens do funil
            
            # 🔍 DETECÇÃO DE CONVERSÃO/RECUSA por palavras-chave
            user_message_lower = user_message.lower()
            
            # Palavras-chave de CONVERSÃO
            conversion_keywords = [
                "já cadastrei", "já me cadastrei", "já fiz o cadastro", 
                "já depositei", "já apostei", "já sou cliente", "já tenho conta",
                "cadastrado", "depositei", "apostei", "sou cliente"
            ]
            
            # Palavras-chave de RECUSA
            refusal_keywords = [
                "não quero mais", "para de mandar", "não me mande mais", 
                "sair da lista", "não tenho interesse", "me tira daqui",
                "pare", "chega", "não quero", "desisto"
            ]
            
            # Verifica conversão
            if any(keyword in user_message_lower for keyword in conversion_keywords):
                print(f"🎉 CONVERSÃO DETECTADA para {phone_number}: {user_message}")
                await track_lead_status(
                    lead_id=phone_number,
                    nome=lead_context.get('nome', 'Lead'),
                    telefone=phone_number,
                    new_status="Funil_CONVERTIDO",
                    details={
                        "motivo": "Conversão detectada por palavra-chave",
                        "mensagem_conversao": user_message,
                        "data_conversao": datetime.now().isoformat()
                    }
                )
                return "Demais, mano! Parabéns pela decisão! Agora é só lucrar! 🚀"
            
            # Verifica recusa
            if any(keyword in user_message_lower for keyword in refusal_keywords):
                print(f"❌ RECUSA DETECTADA para {phone_number}: {user_message}")
                await track_lead_status(
                    lead_id=phone_number,
                    nome=lead_context.get('nome', 'Lead'),
                    telefone=phone_number,
                    new_status="Funil_RECUSADO",
                    details={
                        "motivo": "Recusa detectada por palavra-chave",
                        "mensagem_recusa": user_message,
                        "data_recusa": datetime.now().isoformat()
                    }
                )
                return "Tranquilo, parça! Respeitamos sua decisão. Valeu pelo papo! 👍"
            
            # Determina o dia atual do funil
            current_day = await self.get_lead_funnel_day(phone_number)
            lead_name = lead_context.get('nome', 'parça')
            
            print(f"📅 Lead {phone_number} está no dia {current_day} do funil")
            
            # Verifica se deve enviar mensagem do funil
            should_send_funnel = await self.should_send_funnel_message(phone_number, user_message)
            
            if should_send_funnel:
                # Envia mensagem específica do dia
                day_message = await self.get_day_message(current_day, lead_name)
                
                # Avança para o próximo dia (para próxima interação)
                await self.advance_funnel_day(phone_number, current_day)
                
                print(f"🎯 Enviando mensagem do dia {current_day}: {day_message}")
                return day_message
            else:
                # Deixa a IA responder normalmente à pergunta
                print(f"❓ Usuário fez pergunta específica, deixando IA responder")
                return None
                
        except Exception as e:
            print(f"ERRO no processamento do funil para {phone_number}: {e}")
            return None
    
    async def send_scheduled_message(self, phone_number: str, day: int):
        """
        📤 Envia mensagem agendada para um dia específico
        """
        try:
            # Busca contexto do lead
            lead_status = await get_lead_current_status(phone_number)
            lead_name = lead_status.get('details', {}).get('nome', 'parça')
            
            # Obtém mensagem do dia
            message = await self.get_day_message(day, lead_name)
            
            # Envia mensagem
            await send_whatsapp_message(phone_number, message)
            
            # Atualiza status
            await track_lead_status(
                lead_id=phone_number,
                nome=lead_name,
                telefone=phone_number,
                new_status=f"Funil_Dia{day}_Enviado",
                details={
                    "dia_funil": day,
                    "data_disparo": datetime.now().isoformat(),
                    "mensagem_enviada": message,
                    "tipo_mensagem": self.schedule[day]["tipo"]
                }
            )
            
            print(f"✅ Mensagem do dia {day} enviada para {phone_number}")
            
        except Exception as e:
            print(f"ERRO ao enviar mensagem agendada para {phone_number}: {e}")

# 🎯 Instância global do orquestrador
funnel_orchestrator = FunnelOrchestrator()