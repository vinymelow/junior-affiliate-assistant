#!/usr/bin/env python3
"""
Teste para verificar se as mensagens estão humanizadas após as correções
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.ai import ASSISTANT_INSTRUCTIONS

def test_instructions():
    print("=== TESTE DAS INSTRUÇÕES ATUALIZADAS ===\n")
    
    # Verificar se as novas regras estão presentes
    checks = [
        ("Uso moderado de 'parça'", "Uso de \"parça\": Use com moderação!" in ASSISTANT_INSTRUCTIONS),
        ("Proibição de colchetes", "NUNCA use colchetes []" in ASSISTANT_INSTRUCTIONS),
        ("Proibição de parênteses", "parênteses ()" in ASSISTANT_INSTRUCTIONS),
        ("Exemplo correto", "Claro, parça! Aqui tá o link:" in ASSISTANT_INSTRUCTIONS),
        ("Exemplo errado", "[Acessa agora]" in ASSISTANT_INSTRUCTIONS)
    ]
    
    print("Verificações das instruções:")
    for check_name, result in checks:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {check_name}: {status}")
    
    print("\n=== EXEMPLOS DE MENSAGENS ===\n")
    
    print("ANTES (robotizado):")
    print('❌ "Confere aí, parça! Aqui tá o link: [Acessa agora](https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001). Bora lucrar! 🚀"')
    
    print("\nDEPOIS (humanizado):")
    print('✅ "Claro, parça! Aqui tá o link: https://go.aff.bateu.bet.br/ipyehjvg?utm_source=pt001 Bora lucrar! 🚀"')
    
    print("\n=== REGRAS DE USO DO 'PARÇA' ===")
    print("✅ Usar apenas no início da conversa e na mensagem final")
    print("✅ Evitar repetir em todas as mensagens")
    print("✅ Usar 'mano', 'demorou', 'fechou' como alternativas")

if __name__ == "__main__":
    test_instructions()