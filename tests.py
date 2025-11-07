#!/usr/bin/env python3
"""
Testes das integrações SDR Agent
"""

from integracoes.cal_integration import CalIntegration
from integracoes.pipefy_real import PipefyIntegration


def testar_disponibilidade_real():
    """Testa consulta de disponibilidade real no Cal.com"""
    print("\nTESTANDO DISPONIBILIDADE REAL")
    print("=" * 30)
    
    cal = CalIntegration()
    if not cal.api_token:
        print("❌ Token Cal.com não configurado")
        return
    
    # Testar busca de slots disponíveis
    print("Buscando slots disponíveis...")
    slots = cal.get_available_slots()
    
    if slots:
        print(f"✅ Encontrados {len(slots)} slots disponíveis:")
        for i, slot in enumerate(slots):
            print(f"   {i+1}. {slot}")
    else:
        print("❌ Nenhum slot disponível encontrado")
        
    # Testar método oferecer_horarios do SDR Agent
    print("\nTestando oferecer_horarios do SDR Agent...")
    from agent.sdr_agent import SDRAgent
    
    agent = SDRAgent()
    horarios = agent.oferecer_horarios()
    
    if horarios:
        print(f"✅ SDR Agent retornou {len(horarios)} horários:")
        for horario in horarios:
            print(f"   {horario}")
    else:
        print("❌ SDR Agent não retornou horários")


if __name__ == "__main__":
    testar_disponibilidade_real()