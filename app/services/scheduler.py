"""
⏰ SISTEMA DE AGENDAMENTO - DISPAROS AUTOMÁTICOS
Gerencia disparos automáticos do funil de 20 dias
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.core.funnel_orchestrator import funnel_orchestrator
from app.services.affiliate import get_all_active_leads, get_lead_current_status

class FunnelScheduler:
    """
    ⏰ Agendador de disparos automáticos do funil
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 3600  # Verifica a cada 1 hora
    
    async def get_leads_for_day_dispatch(self, target_day: int) -> List[Dict]:
        """
        📋 Busca leads que devem receber disparo de um dia específico
        """
        try:
            # Busca todos os leads ativos
            active_leads = await get_all_active_leads()
            leads_for_dispatch = []
            
            for lead in active_leads:
                phone_number = lead.get('telefone')
                if not phone_number:
                    continue
                
                # Verifica status atual do lead
                lead_status = await get_lead_current_status(phone_number)
                details = lead_status.get('details', {})
                
                # Verifica se está no dia correto do funil
                current_day = details.get('dia_funil', 1)
                last_dispatch = details.get('data_ultimo_disparo')
                
                # Se está no dia anterior ao target_day e passou tempo suficiente
                if current_day == target_day - 1:
                    if self._should_dispatch_today(last_dispatch):
                        leads_for_dispatch.append({
                            'phone_number': phone_number,
                            'nome': details.get('nome', 'parça'),
                            'current_day': current_day,
                            'target_day': target_day
                        })
            
            return leads_for_dispatch
            
        except Exception as e:
            print(f"ERRO ao buscar leads para disparo do dia {target_day}: {e}")
            return []
    
    def _should_dispatch_today(self, last_dispatch_str: Optional[str]) -> bool:
        """
        🤔 Verifica se deve fazer disparo hoje baseado no último disparo
        """
        if not last_dispatch_str:
            return True  # Nunca disparou, pode disparar
        
        try:
            last_dispatch = datetime.fromisoformat(last_dispatch_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Dispara se passou mais de 24 horas
            return (now - last_dispatch) > timedelta(hours=24)
            
        except Exception as e:
            print(f"ERRO ao verificar data do último disparo: {e}")
            return True  # Em caso de erro, permite disparo
    
    async def process_scheduled_dispatches(self):
        """
        🚀 Processa todos os disparos agendados para hoje
        """
        print("🔄 Verificando disparos agendados...")
        
        try:
            # Verifica cada dia do funil (1-20)
            for day in range(1, 21):
                leads_for_day = await self.get_leads_for_day_dispatch(day)
                
                if leads_for_day:
                    print(f"📤 Encontrados {len(leads_for_day)} leads para disparo do dia {day}")
                    
                    for lead in leads_for_day:
                        try:
                            await funnel_orchestrator.send_scheduled_message(
                                lead['phone_number'], 
                                lead['target_day']
                            )
                            
                            # Aguarda 2 segundos entre disparos para não sobrecarregar
                            await asyncio.sleep(2)
                            
                        except Exception as e:
                            print(f"ERRO ao enviar disparo para {lead['phone_number']}: {e}")
                
                # Aguarda 5 segundos entre verificações de dias
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"ERRO CRÍTICO no processamento de disparos: {e}")
    
    async def start_scheduler(self):
        """
        ▶️ Inicia o agendador em loop contínuo
        """
        print("🚀 Iniciando agendador de disparos do funil...")
        self.running = True
        
        while self.running:
            try:
                await self.process_scheduled_dispatches()
                
                # Aguarda o intervalo antes da próxima verificação
                print(f"⏳ Próxima verificação em {self.check_interval/3600:.1f} horas...")
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"ERRO no loop do agendador: {e}")
                await asyncio.sleep(300)  # Aguarda 5 minutos em caso de erro
    
    def stop_scheduler(self):
        """
        ⏹️ Para o agendador
        """
        print("⏹️ Parando agendador de disparos...")
        self.running = False
    
    async def manual_dispatch_day(self, day: int, phone_numbers: List[str] = None):
        """
        🎯 Disparo manual para um dia específico
        """
        print(f"🎯 Iniciando disparo manual para o dia {day}")
        
        if phone_numbers:
            # Dispara para números específicos
            for phone_number in phone_numbers:
                try:
                    await funnel_orchestrator.send_scheduled_message(phone_number, day)
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"ERRO no disparo manual para {phone_number}: {e}")
        else:
            # Dispara para todos os leads elegíveis
            leads_for_day = await self.get_leads_for_day_dispatch(day)
            
            for lead in leads_for_day:
                try:
                    await funnel_orchestrator.send_scheduled_message(
                        lead['phone_number'], 
                        day
                    )
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"ERRO no disparo manual para {lead['phone_number']}: {e}")
        
        print(f"✅ Disparo manual do dia {day} concluído")

# 🎯 Instância global do agendador
funnel_scheduler = FunnelScheduler()

# 🚀 Função para iniciar o agendador em background
async def start_funnel_scheduler():
    """
    Inicia o agendador de disparos em background
    """
    await funnel_scheduler.start_scheduler()

# 🎯 Função para disparo manual via API
async def manual_funnel_dispatch(day: int, phone_numbers: List[str] = None):
    """
    Executa disparo manual para um dia específico
    """
    await funnel_scheduler.manual_dispatch_day(day, phone_numbers)