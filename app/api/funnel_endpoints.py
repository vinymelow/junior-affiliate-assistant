"""
🎯 ENDPOINTS DO FUNIL - GERENCIAMENTO MANUAL
Endpoints para controlar e monitorar o funil de 20 dias
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from app.core.funnel_orchestrator import funnel_orchestrator
from app.services.scheduler import funnel_scheduler, manual_funnel_dispatch
from app.services.affiliate import get_all_active_leads, get_lead_current_status, track_lead_status

router = APIRouter(prefix="/funil", tags=["Funil"])

class ManualDispatchRequest(BaseModel):
    day: int
    phone_numbers: Optional[List[str]] = None

class FunnelStatusResponse(BaseModel):
    total_leads: int
    leads_by_day: dict
    active_leads: List[dict]

class LeadCreateRequest(BaseModel):
    telefone: str
    nome: str
    genero: str
    cidade: Optional[str] = "N/A"

@router.post("/lead")
async def create_or_update_lead(lead: LeadCreateRequest):
    """
    👤 Cria ou atualiza um lead no sistema
    """
    try:
        # Registra o lead no sistema de tracking
        await track_lead_status(
            lead_id=lead.telefone,  # Usando telefone como ID único
            nome=lead.nome,
            telefone=lead.telefone,
            new_status="Funil_Dia1_ContatoInicial",
            details={
                "genero": lead.genero,
                "cidade": lead.cidade,
                "data_criacao": "2025-09-23",
                "origem": "API"
            }
        )
        
        return {
            "status": "success",
            "message": f"Lead {lead.nome} criado/atualizado com sucesso",
            "lead": {
                "telefone": lead.telefone,
                "nome": lead.nome,
                "genero": lead.genero,
                "cidade": lead.cidade,
                "status_inicial": "Funil_Dia1_ContatoInicial"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar/atualizar lead: {e}")

@router.get("/status", response_model=FunnelStatusResponse)
async def get_funnel_status():
    """
    📊 Obtém status geral do funil
    """
    try:
        active_leads = await get_all_active_leads()
        leads_by_day = {}
        
        for lead in active_leads:
            phone_number = lead['telefone']
            current_day = await funnel_orchestrator.get_lead_funnel_day(phone_number)
            
            if current_day not in leads_by_day:
                leads_by_day[current_day] = []
            
            leads_by_day[current_day].append({
                'phone_number': phone_number,
                'nome': lead['nome'],
                'status': lead['status_atual']
            })
        
        return FunnelStatusResponse(
            total_leads=len(active_leads),
            leads_by_day=leads_by_day,
            active_leads=active_leads
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status do funil: {e}")

@router.post("/dispatch/manual")
async def manual_dispatch(request: ManualDispatchRequest, background_tasks: BackgroundTasks):
    """
    🎯 Executa disparo manual para um dia específico
    """
    try:
        if request.day < 1 or request.day > 20:
            raise HTTPException(status_code=400, detail="Dia deve estar entre 1 e 20")
        
        # Executa disparo em background
        background_tasks.add_task(
            manual_funnel_dispatch, 
            request.day, 
            request.phone_numbers
        )
        
        return {
            "status": "success",
            "message": f"Disparo manual do dia {request.day} iniciado em background",
            "day": request.day,
            "phone_numbers": request.phone_numbers or "todos os leads elegíveis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no disparo manual: {e}")

@router.get("/lead/{phone_number}/status")
async def get_lead_funnel_status(phone_number: str):
    """
    👤 Obtém status específico de um lead no funil
    """
    try:
        current_day = await funnel_orchestrator.get_lead_funnel_day(phone_number)
        lead_status = await get_lead_current_status(phone_number)
        
        return {
            "phone_number": phone_number,
            "current_day": current_day,
            "status": lead_status.get('status'),
            "details": lead_status.get('details', {}),
            "next_message": await funnel_orchestrator.get_day_message(current_day + 1)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status do lead: {e}")

@router.post("/lead/{phone_number}/advance")
async def advance_lead_day(phone_number: str):
    """
    ⏭️ Avança um lead para o próximo dia do funil
    """
    try:
        current_day = await funnel_orchestrator.get_lead_funnel_day(phone_number)
        new_day = await funnel_orchestrator.advance_funnel_day(phone_number, current_day)
        
        return {
            "status": "success",
            "phone_number": phone_number,
            "previous_day": current_day,
            "new_day": new_day,
            "message": f"Lead avançado do dia {current_day} para o dia {new_day}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao avançar lead: {e}")

@router.get("/schedule/info")
async def get_schedule_info():
    """
    📅 Obtém informações sobre o cronograma do funil
    """
    try:
        from app.core.funnel_orchestrator import FUNNEL_SCHEDULE
        
        schedule_info = {}
        for day, config in FUNNEL_SCHEDULE.items():
            schedule_info[day] = {
                "objetivo": config["objetivo"],
                "tipo": config["tipo"],
                "mensagem_exemplo": config["mensagem_fixa"][:50] + "..." if len(config["mensagem_fixa"]) > 50 else config["mensagem_fixa"]
            }
        
        return {
            "total_days": 20,
            "schedule": schedule_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter cronograma: {e}")

@router.post("/scheduler/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """
    ▶️ Inicia o agendador automático
    """
    try:
        if funnel_scheduler.running:
            return {"status": "info", "message": "Agendador já está rodando"}
        
        background_tasks.add_task(funnel_scheduler.start_scheduler)
        
        return {
            "status": "success",
            "message": "Agendador iniciado em background",
            "check_interval_hours": funnel_scheduler.check_interval / 3600
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar agendador: {e}")

@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    ⏹️ Para o agendador automático
    """
    try:
        funnel_scheduler.stop_scheduler()
        
        return {
            "status": "success",
            "message": "Agendador parado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar agendador: {e}")

@router.get("/test/message/{day}")
async def test_day_message(day: int, nome: str = "Teste"):
    """
    🧪 Testa a mensagem de um dia específico
    """
    try:
        if day < 1 or day > 20:
            raise HTTPException(status_code=400, detail="Dia deve estar entre 1 e 20")
        
        message = await funnel_orchestrator.get_day_message(day, nome)
        
        return {
            "day": day,
            "nome": nome,
            "message": message,
            "character_count": len(message)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar mensagem: {e}")